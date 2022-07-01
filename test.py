dict_A = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}
dict_B = {2: 20, 4: 30}

if __name__ == '__main__':

    print(dict_A)
    print(dict_B)

    for i in dict_A:
        if i in dict_B:
            if dict_A[i] != dict_B[i]:
                dict_A[i] = dict_B[i]

    print(dict_A)


