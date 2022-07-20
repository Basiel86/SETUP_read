import numpy as np
from numpy import inf

# np.seterr(divide='ignore', invalid='ignore')

if __name__ == '__main__':
    x1 = np.array(
        [[1, 44634.53952],
         [2, 44634.53952],
         [3, 44634.53953],
         [4, 44634.53953],
         [5, 44634.53954]])

    print(x1)

    # забираем 2 столбца
    y1 = x1[:, 0]
    y2 = x1[:, 1]

    # считаем разницу для каждого
    y1 = np.diff(y1)
    y2 = np.diff(y2) * 100000

    # делим друг на друга для скорости
    # удаляем деление на ноль
    z = y1 / y2
    z[z == inf] = 0

    # перевращаем результаты в столбцы
    z = np.resize(z, len(z) + 1)
    z = np.reshape(z, (len(z), 1))

    # добавляем столбец в наш массив
    x1 = np.append(x1, z, axis=1)

    print(x1)

    # x2 = np.array([10, 20, 30, 40, 50])
    # y = np.diff(x1)
    # y1 = np.diff(x1[0])
    # y2 = np.diff(x2)
    #
    # z = y1 / y2
    #
    # print(y1)
    # print(y2)
    #
    # print(x1.names)
