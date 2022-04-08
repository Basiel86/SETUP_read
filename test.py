
import csv
import numpy as np
from numpy import genfromtxt

filename = r"c:\Users\Vasily\OneDrive\Macro\PYTHON\SETUP_read\Book1.csv"

with open(filename, encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    headers = next(reader)
    print('Headers: ', headers)
    # for row in reader:
    #     print(row)

# my_data = genfromtxt(filename, delimiter=',')

axis_array = np.loadtxt(filename,delimiter=',',skiprows=1, usecols=range(0, 2))

print (axis_array)