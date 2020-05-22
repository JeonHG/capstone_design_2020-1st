from xfoil import XFoil
from xfoil.model import Airfoil
import numpy as np
import pandas as pd
import os


array6409 = np.loadtxt("NACA6409.dat", skiprows=1)
array2412 = np.loadtxt("NACA2412.dat", skiprows=1)
naca6409 = Airfoil(x=array6409[:, 0], y=array6409[:, 1])
# xf = XFoil()
# xf.airfoil = naca6409
# xf.Re = 1e6
# xf.max_iter = 40
# print(xf.a(10)[0])

base_dir = r'C:\Users\USER\dev\mechanics'
csv_file = 'blade_profile.csv'
csv_dir = os.path.join(base_dir, csv_file)
df = pd.read_csv(csv_dir)
print(df)