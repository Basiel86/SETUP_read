
import csv
import numpy as np
import pandas as pd

from numpy import genfromtxt

filename = r"c:\Users\Vasily\OneDrive\Macro\PYTHON\SETUP_read\test.xlsx"

WS = pd.read_excel(filename)
axis_array = np.array(WS)
print (WS.columns.values)
print (axis_array)