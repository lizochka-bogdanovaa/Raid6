import numpy as np
import os

#массив с названием файлов
disks_names = ['disk_0.txt', 'disk_1.txt', 'disk_2.txt', 'disk_3.txt', 'disk_4.txt']
count_lines = 64
count_disks = 5
#распределение блоков с контрольными суммами и данными
#1 - блок избыточности; 0 - блок данных
blocks_distribution = [[0,0,0,1,1],
                       [0,0,1,1,0],
                       [0,1,1,0,0],
                       [1,1,0,0,0],
                       [1,0,0,0,1]]


#функция проверки дисков (файлов): проверяем, какого диска нет в директории и выводим в консоль
#заполняем массив индексами утерянных дисков
def check_disks() -> list:
    lost_disks = []
    for i in range(len(disks_names)):
        if not os.path.isfile(disks_names[i]):
            print(f"Диск {disks_names[i]} был утерян")
            lost_disks.append(i)
    return lost_disks


#функция создания файла: создаем файл и заполняем 64 строки нулями
def create_file(file_name: str):
    with open(file_name, 'w') as f:
        f.write('0\n'*count_lines)


#функция для вывода строки из файлов
def result_output(data_fr_disks: list, superfluity_blocks_list: list):
    res = ''
    count = 0
    for i in range(count_disks):
        if (i not in superfluity_blocks_list):
            res += data_fr_disks[i]
            count+=1
            if (len(data_fr_disks[i]) != 3 and count == 1):
                res = "пустая строка"
                break
    print(res)


#функция проверки: можно ли перевести строку в 16сс (входят ли символы строки в алфавит 16сс)
def can_convert_to_hex(str_conv: str) -> bool:
    try:
        int(str_conv, 16)
        return True
    except ValueError:
        return False


#функция подсчета избыточности: считаем первую контрольную сумму
def first_superfluity(all_parts: list) -> str:
    A = int(all_parts[0], 16)
    B = int(all_parts[1], 16)
    C = int(all_parts[2], 16)
    # A + B + C= p
    return f"{(A+B+C):x}"


#функция подсчета избыточности: считаем вторую контрольную сумму
def second_superfluity(all_parts: list) -> str:
    A = int(all_parts[0], 16)
    B = int(all_parts[1], 16)
    C = int(all_parts[2], 16)
    # A - B - 2*C= q
    return f"{(A - B - 2*C):x}"


#чтение с дисков
def read():
    #просим пользователя ввести номер строки, с которой он хочет прочитать информацию
    #если номер строки от 0 до 63, то выходим из цикла
    #иначе, просим ввести номер строки еще раз
    while (True):
        input_address = input("Введите номер строки, которую хотите прочитать (от 0 до 63): ")
        int_address = int(input_address)
        if (int_address > 63 or int_address < 0):
            print("Неправильный номер строки")
        else:
            break
    #создаем массив, в котором будет храниться вся информация со всех дисков
    all_disks = []
    #индексы дисков, которые удалили
    lost_disks = check_disks()
    #создаем файлы, которые были удалены и заполняем нулями
    for i in range(len(lost_disks)):
        create_file(f'disk_{lost_disks[i]}.txt')
    #по очереди открываем все файлы (диски) и записываем в общий список по очереди список информации с каждого диска
    for i in range(count_disks):
        file = open(disks_names[i], 'r')
        all_disks += [file.readlines()]
        file.close()

    for adr in range(64):
        #проверям, умер ли блок данных или блок с контрольной суммой
        data_died = []
        superfluity_died = []
        for i in range(len(lost_disks)):
            #записали номера блоков данных, которые умерли
            if (blocks_distribution[adr % count_disks][lost_disks[i]] == 0):
                data_died.append(lost_disks[i])
                #print("умер блок данных", data_died)
            else:
                #записали номера блоков избыточности, которые умерли
                superfluity_died.append(lost_disks[i])
                #print("умер блок с контрольной суммой", superfluity_died)
        #получили список индексов блоков избыточности
        superfluity_blocks_list = [item for item in range(count_disks) if blocks_distribution[adr % count_disks][item] == 1]
        #номер 1го блока избыточности
        p_ind = superfluity_blocks_list[0]
        #номер 2го блока избыточности
        q_ind = superfluity_blocks_list[1]
        #получили список индексов блоков данных
        data_blocks_list = [item for item in range(count_disks) if item not in superfluity_blocks_list]
        #номер 1го блока данных
        a_ind = data_blocks_list[0]
        #номер 2го блока данных
        b_ind = data_blocks_list[1]
        #номер 3го блока данных
        c_ind = data_blocks_list[2]
        #список, в котором хранится вся информация с дисков по очереди по выбранному адресу
        data_fr_disks = []
        for i in range(count_disks):
            data_fr_disks.append((all_disks[i][adr])[:-1])


        #список, в котором хранится вся информация с дисков по очереди в 10сс для счета по выбранному адресу
        data_fr_disks_hex = []
        for i in range(count_disks):
            if (data_fr_disks[i] != '0'):
                data_fr_disks_hex.append(int(data_fr_disks[i], 16))
            else:
                data_fr_disks_hex.append(0)

        #если умерло два и меньше блока контрольных сумм и не умерли блоки данных, то восстанавливаем контрольные суммы и можно просто вывести инфу из блоков данных
        if (len(superfluity_died) <= 2 and len(data_died) == 0):
            #восстанавливаем контрольные суммы
            if (len(superfluity_died) == 1 and superfluity_died[0] == p_ind):
                data_fr_disks[p_ind] = first_superfluity([data_fr_disks[a_ind],data_fr_disks[b_ind],data_fr_disks[c_ind]])
            elif (len(superfluity_died) == 1 and superfluity_died[0] == q_ind):
                data_fr_disks[q_ind] = second_superfluity([data_fr_disks[a_ind], data_fr_disks[b_ind], data_fr_disks[c_ind]])
            elif (len(superfluity_died) == 2):
                data_fr_disks[p_ind] = first_superfluity([data_fr_disks[a_ind], data_fr_disks[b_ind], data_fr_disks[c_ind]])
                data_fr_disks[q_ind] = second_superfluity([data_fr_disks[a_ind], data_fr_disks[b_ind], data_fr_disks[c_ind]])
        else:
            #если не умерли 2 диска избыточности и умер 1 диск данных
            if(len(superfluity_died) == 0 and len(data_died) == 1):
                #если умер блок А
                if(data_died[0] == a_ind):
                    A = data_fr_disks_hex[p_ind] - data_fr_disks_hex[b_ind] - data_fr_disks_hex[c_ind]
                    if (len(hex(A)[2:]) == 3):
                        data_fr_disks[a_ind] = f"{A:x}"
                    else:
                        if (data_fr_disks[c_ind] != '0'):
                            n = 3 - len(hex(A)[2:])
                            data_fr_disks[a_ind] = '0' * n + f"{A:x}"
                        else:
                            data_fr_disks[a_ind] = '0'
                    #data_fr_disks[a_ind] = f"{A:x}"
                #если умер блок B
                elif (data_died[0] == b_ind):
                    B = data_fr_disks_hex[p_ind] - data_fr_disks_hex[a_ind] - data_fr_disks_hex[c_ind]
                    if (len(hex(B)[2:]) == 3):
                        data_fr_disks[b_ind] = f"{B:x}"
                    else:
                        if (data_fr_disks[c_ind] != '0'):
                            n = 3 - len(hex(B)[2:])
                            data_fr_disks[b_ind] = '0' * n + f"{B:x}"
                        else:
                            data_fr_disks[b_ind] = '0'
                    #data_fr_disks[b_ind] = f"{B:x}"
                # если умер блок C
                elif (data_died[0] == c_ind):
                    C = data_fr_disks_hex[p_ind] - data_fr_disks_hex[a_ind] - data_fr_disks_hex[b_ind]
                    if (len(hex(C)[2:]) == 2):
                        data_fr_disks[c_ind] = f"{C:x}"
                    else:
                        if (data_fr_disks[b_ind] != '0'):
                            n = 2 - len(hex(C)[2:])
                            data_fr_disks[c_ind] = '0' * n + f"{C:x}"
                        else:
                            data_fr_disks[c_ind] = '0'
                    #data_fr_disks[c_ind] = f"{C:x}"
                if (adr == int_address):
                    print(f"Диск {disks_names[data_died[0]]} восстановлен")
            else:
                #если не умерли 2 диска избыточности и умерло 2 диска данных
                if (len(superfluity_died) == 0 and len(data_died) == 2):
                    if (a_ind in data_died and b_ind in data_died):
                        left = np.array([[1, 1], [1, -1]])
                        right = np.array([data_fr_disks_hex[p_ind]-data_fr_disks_hex[c_ind], data_fr_disks_hex[q_ind]+2*data_fr_disks_hex[c_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        A = vect_solution[0]
                        B = vect_solution[1]
                        if (len(hex(A)[2:]) == 3):
                            data_fr_disks[a_ind] = f"{A:x}"
                        else:
                            if (data_fr_disks[c_ind] != '0'):
                                n = 3 - len(hex(A)[2:])
                                data_fr_disks[a_ind] = '0'*n + f"{A:x}"
                            else:
                                data_fr_disks[a_ind] = '0'

                        if (len(hex(B)[2:]) == 3):
                            data_fr_disks[b_ind] = f"{B:x}"
                        else:
                            if (data_fr_disks[c_ind] != '0'):
                                n = 3 - len(hex(B)[2:])
                                data_fr_disks[b_ind] = '0' * n + f"{B:x}"
                            else:
                                data_fr_disks[b_ind] = '0'

                    elif (a_ind in data_died and c_ind in data_died):
                        left = np.array([[1, 1], [1, -2]])
                        right = np.array([data_fr_disks_hex[p_ind]-data_fr_disks_hex[b_ind], data_fr_disks_hex[q_ind]+data_fr_disks_hex[b_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        A = vect_solution[0]
                        C = vect_solution[1]
                        if (len(hex(A)[2:]) == 3):
                            data_fr_disks[a_ind] = f"{A:x}"
                        else:
                            if (data_fr_disks[b_ind] != '0'):
                                n = 3 - len(hex(A)[2:])
                                data_fr_disks[a_ind] = '0' * n + f"{A:x}"
                            else:
                                data_fr_disks[a_ind] = '0'

                        if (len(hex(C)[2:]) == 2):
                            data_fr_disks[c_ind] = f"{C:x}"
                        else:
                            if (data_fr_disks[b_ind] != '0'):
                                n = 2 - len(hex(C)[2:])
                                data_fr_disks[c_ind] = '0' * n + f"{C:x}"
                            else:
                                data_fr_disks[c_ind] = '0'

                    elif (b_ind in data_died and c_ind in data_died):
                        left = np.array([[1, 1], [-1, -2]])
                        right = np.array([data_fr_disks_hex[p_ind]-data_fr_disks_hex[a_ind], data_fr_disks_hex[q_ind]-data_fr_disks_hex[a_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        B = vect_solution[0]
                        C = vect_solution[1]
                        if (len(hex(B)[2:]) == 3):
                            data_fr_disks[b_ind] = f"{B:x}"
                        else:
                            if (data_fr_disks[a_ind] != '0'):
                                n = 3 - len(hex(B)[2:])
                                data_fr_disks[b_ind] = '0' * n + f"{B:x}"
                            else:
                                data_fr_disks[b_ind] = '0'

                        if (len(hex(C)[2:]) == 2):
                            data_fr_disks[c_ind] = f"{C:x}"
                        else:
                            if (data_fr_disks[a_ind] != '0'):
                                n = 2 - len(hex(C)[2:])
                                data_fr_disks[c_ind] = '0' * n + f"{C:x}"
                            else:
                                data_fr_disks[c_ind] = '0'

                    if (adr == int_address):
                        print(f"Диски {disks_names[data_died[0]],disks_names[data_died[1]]} восстановлены")
                #если умер 1 диск избыточности и умер 1 диск данных
                elif(len(superfluity_died) == 1 and len(data_died) == 1):
                    if (a_ind in data_died and p_ind in superfluity_died):
                        left = np.array([[1, -1], [1, 0]])
                        right = np.array([-data_fr_disks_hex[b_ind]-data_fr_disks_hex[c_ind], data_fr_disks_hex[q_ind]+data_fr_disks_hex[b_ind]+2*data_fr_disks_hex[c_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        A = vect_solution[0]
                        p = vect_solution[1]
                        if (len(hex(A)[2:]) == 3):
                            data_fr_disks[a_ind] = f"{A:x}"
                        else:
                            if (data_fr_disks[b_ind] != '0'):
                                n = 3 - len(hex(A)[2:])
                                data_fr_disks[a_ind] = '0' * n + f"{A:x}"
                            else:
                                data_fr_disks[a_ind] = '0'
                        data_fr_disks[p_ind] = f"{p:x}"
                    elif (a_ind in data_died and q_ind in superfluity_died):
                        left = np.array([[1, 0], [1, -1]])
                        right = np.array([data_fr_disks_hex[p_ind]-data_fr_disks_hex[b_ind]-data_fr_disks_hex[c_ind], data_fr_disks_hex[b_ind]+2*data_fr_disks_hex[c_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        A = vect_solution[0]
                        q = vect_solution[1]
                        if (len(hex(A)[2:]) == 3):
                            data_fr_disks[a_ind] = f"{A:x}"
                        else:
                            if (data_fr_disks[b_ind] != '0'):
                                n = 3 - len(hex(A)[2:])
                                data_fr_disks[a_ind] = '0' * n + f"{A:x}"
                            else:
                                data_fr_disks[a_ind] = '0'

                        data_fr_disks[q_ind] = f"{q:x}"
                    elif (b_ind in data_died and p_ind in superfluity_died):
                        left = np.array([[1, -1], [-1, 0]])
                        right = np.array([-data_fr_disks_hex[a_ind]-data_fr_disks_hex[c_ind], data_fr_disks_hex[q_ind]-data_fr_disks_hex[a_ind]+2*data_fr_disks_hex[c_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        B = vect_solution[0]
                        p = vect_solution[1]
                        if (len(hex(B)[2:]) == 3):
                            data_fr_disks[b_ind] = f"{B:x}"
                        else:
                            if (data_fr_disks[a_ind] != '0'):
                                n = 3 - len(hex(B)[2:])
                                data_fr_disks[b_ind] = '0' * n + f"{B:x}"
                            else:
                                data_fr_disks[b_ind] = '0'

                        data_fr_disks[p_ind] = f"{p:x}"
                    elif (b_ind in data_died and q_ind in superfluity_died):
                        left = np.array([[1, 0], [-1, -1]])
                        right = np.array([data_fr_disks_hex[p_ind]-data_fr_disks_hex[a_ind]-data_fr_disks_hex[c_ind], -data_fr_disks_hex[a_ind]+2*data_fr_disks_hex[c_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        B = vect_solution[0]
                        q = vect_solution[1]
                        if (len(hex(B)[2:]) == 3):
                            data_fr_disks[b_ind] = f"{B:x}"
                        else:
                            if (data_fr_disks[a_ind] != '0'):
                                n = 3 - len(hex(B)[2:])
                                data_fr_disks[b_ind] = '0' * n + f"{B:x}"
                            else:
                                data_fr_disks[b_ind] = '0'

                        data_fr_disks[q_ind] = f"{q:x}"
                    elif (c_ind in data_died and p_ind in superfluity_died):
                        left = np.array([[1, -1], [-2, 0]])
                        right = np.array([-data_fr_disks_hex[a_ind]-data_fr_disks_hex[b_ind], data_fr_disks_hex[q_ind]-data_fr_disks_hex[a_ind]+data_fr_disks_hex[b_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        C = vect_solution[0]
                        p = vect_solution[1]
                        if (len(hex(C)[2:]) == 2):
                            data_fr_disks[c_ind] = f"{C:x}"
                        else:
                            if (data_fr_disks[a_ind] != '0'):
                                n = 2 - len(hex(C)[2:])
                                data_fr_disks[c_ind] = '0' * n + f"{C:x}"
                            else:
                                data_fr_disks[c_ind] = '0'

                        data_fr_disks[p_ind] = f"{p:x}"
                    elif (c_ind in data_died and q_ind in superfluity_died):
                        left = np.array([[1, 0], [-2, -1]])
                        right = np.array([data_fr_disks_hex[p_ind]-data_fr_disks_hex[a_ind]-data_fr_disks_hex[b_ind], -data_fr_disks_hex[a_ind]+data_fr_disks_hex[b_ind]])
                        vect_solution = np.linalg.solve(left, right).astype(int)
                        C = vect_solution[0]
                        q = vect_solution[1]
                        if (len(hex(C)[2:]) == 2):
                            data_fr_disks[c_ind] = f"{C:x}"
                        else:
                            if (data_fr_disks[a_ind] != '0'):
                                n = 2 - len(hex(C)[2:])
                                data_fr_disks[c_ind] = '0' * n + f"{C:x}"
                            else:
                                data_fr_disks[c_ind] = '0'

                        data_fr_disks[q_ind] = f"{q:x}"
                    if (adr == int_address):
                        print(f"Диски {disks_names[data_died[0]],disks_names[superfluity_died[0]]} восстановлены")
        #выводим полученную строку
        if (adr == int_address):
            result_output(data_fr_disks, superfluity_blocks_list)

        #в массив, хранящий информацию с дисков добавляем восстановленную информацию
        for i in range(count_disks):
            all_disks[i][adr] = data_fr_disks[i]+'\n'
    #записываем все из массива в файлы (диски)
    for i in range(count_disks):
        file = open(disks_names[i], 'w')
        file.writelines(all_disks[i])
        file.close()


#запись на диски (в файлы)
def write():
    #запрашиваем у пользователя строку
    while (True):
        input_str = input("Введите число в 16сс, состоящее из 8 символов, которое хотите записать: ")
        #проверки, что размер введенного сообщения подходящий и что строка содержит только символы 16ного алфавита
        if (len(input_str) != 8):
            print("Строка должна содержать 8 символов")
        elif (not can_convert_to_hex(input_str)):
                print('Число введено не в 16сс')
        else:
            break
    #разбиваем строку на три части (3-3-2 символа) и кладем в массив
    all_parts = [input_str[:3], input_str[3:6], input_str[6:]]
    #запрашиваем у пользователя адрес для записи строки
    while (True):
        input_address = input("Введите номер строки (от 0 до 63), в которую хотите записать Ваше число: ")
        int_address = int(input_address)
        #проверяем, что адрес от 0 до 63
        if (int_address > 63 or int_address < 0):
            print("Неправильный номер строки")
        else:
            break
    #создаем массив, в котором будет храниться вся информация со всех дисков
    all_disks = []
    # по очереди открываем все файлы (диски) и записываем в общий список по очереди список информации с каждого диска
    for i in range(count_disks):
        file = open(disks_names[i], 'r')
        all_disks += [file.readlines()]
        file.close()
    #считаем первую контрольную сумму
    first_superfluity(all_parts)
    #считаем вторую контрольную сумму
    second_superfluity(all_parts)
    count_iter_fl = 0
    count_iter_p = 0
    #проходимся по всем дискам
    for i in range(count_disks):
        #по введенному адресу % кол-во дисков проверяем в каких блоках должны лежать части строки, а в каких контрольные суммы
        #если по этому индексу для этого диска в распределении 0 => это блок данных, записываем туда часть строки пользователя
        if (blocks_distribution[int_address % count_disks][i] == 0):
            all_disks[i][int_address] = all_parts[count_iter_p]+'\n'
            count_iter_p+=1
        #иначе, это блок для контрольной суммы
        else:
            #если первый раз зашли в этот блок кода, то считаем первую контрольную сумму и записываем
            if (count_iter_fl == 0):
                all_disks[i][int_address] = first_superfluity(all_parts)+'\n'
                count_iter_fl += 1
            #иначе считаем и записываем вторую контрольную сумму
            else:
                all_disks[i][int_address] = second_superfluity(all_parts)+'\n'
    #записываем все из массива в файлы (диски)
    for i in range(count_disks):
        file = open(disks_names[i], 'w')
        file.writelines(all_disks[i])
        file.close()


def printmenu():
    print("Введите цифру от 0 до 2:\n"
          "0 - Завершить работу программы",
          "\n1 - Записать по адресу",
          "\n2 - Прочитать по адресу")


def intinput() -> int:
    flag = True
    while (flag):
        user_input = input()
        try:
            val = int(user_input)
            flag = False
            return val
        except ValueError:
            print("Вы ввели некоректное значение. Повторите ввод.")


def menu():
    flag = True
    while (flag):
        printmenu()
        user_input = intinput()
        match user_input:
            case 0:
                flag = False
            case 1:
                write()
            case 2:
                read()


#создаем файлы в начале программы
for i in range(len(disks_names)):
    create_file(f'disk_{i}.txt')

menu()