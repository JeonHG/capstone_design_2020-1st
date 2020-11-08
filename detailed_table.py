import os
import math
from xfoil import XFoil
from xfoil.model import Airfoil
import numpy as np
import pandas as pd

# load .dat files
array6409 = np.loadtxt("NACA6409.dat", skiprows=1)
array2412 = np.loadtxt("NACA2412.dat", skiprows=1)
naca6409 = Airfoil(x=array6409[:, 0], y=array6409[:, 1])
naca2412 = Airfoil(x=array2412[:, 0], y=array2412[:, 1])
# naca6409 = Airfoil(x=1.155*array6409[:, 0], y=2.541*array6409[:, 1])
# naca2412 = Airfoil(x=1.155*array2412[:, 0], y=2.541*array2412[:, 1])
# xf = XFoil()
# xf.airfoil = naca6409
# xf.Re = 1e6
# xf.max_it er = 40
# print(xf.a(10)[0])

# load blade profile - fixed values : pitch, chord_length
base_dir = r'C:\Users\USER\dev\mechanics'
csv_file = 'blade_profile_50-8.csv'
csv_dir = os.path.join(base_dir, csv_file)
df = pd.read_csv(csv_dir)

# df to dict
dfdict = df.to_dict(orient="index")
density = 1.225
# df_collection = []

def total_dict(angular_velocity):
    torque_sum = 0
    w = angular_velocity
    for key, value in dfdict.items():
        value["blade_velocity"] = value['r_position'] * w
        value["relative_velocity"] = round(math.sqrt(value["blade_velocity"]**2 + value["wind_velocity"]**2),2)
        value["arctan"] = math.degrees(math.atan2(value["wind_velocity"], value["blade_velocity"]))
        aoa = round(value["arctan"] - value["pitch_angle"], 1)
        value["angle_of_attack"] = aoa
        re_n = round(value["relative_velocity"] * value["chord_length"] / 0.00001511)
        value["Reynolds_number"] = re_n
        xf = XFoil()
        if key < 13: 
            xf.airfoil = naca6409
        else:
            xf.airfoil = naca2412
        xf.Re = round(re_n / 100) * 100
        xf.max_iter = 200
        xf.n_crit = 9.00
        xf.xtr = [1.00, 1.00]
        xf.M = 0
        c_l, c_d, c_m, c_p = xf.a(aoa)
        force_reference = 0.5 * density * value["relative_velocity"]**2
        if math.isnan(c_l):
            pass
        else:
            value["Cl"] = c_l
            value["Cd"] = c_d
            value["Cm"] = c_m
            value["Cp"] = c_p
            lift = c_l * force_reference * 0.0125 * value['chord_length']
            drag = c_d * force_reference * 0.0125 * value['chord_length']
            value["lift"] = lift
            value["drag"] = drag
            # value["torque"] = value["r_position"] * lift * math.sin(math.radians(value["pitch_angle"])) 
            torque = value["r_position"] * (lift * math.sin(math.radians(value["pitch_angle"])) - drag * math.cos(math.radians(value["pitch_angle"])))
            value["torque"] = torque
            torque_sum += torque
        xf.reset_bls()
    # detailed_df = pd.DataFrame.from_dict(dfdict, orient="index")
    # print(detailed_df)
    print(torque_sum, angular_velocity)
    return dfdict, torque_sum

from dict_df_excel import dict_to_xlsx

angular_speeds = np.arange(0,150,10)
# angular_speeds = [70, 80, 90, 100]
r_positions = np.arange(0.025, 0.2, 0.0125)
# r_positions = [0.025]
performance_dict = {}
for w in angular_speeds:
    dict_data, torque_sum = total_dict(w)
    dict_to_xlsx(dict_data, 're-round-50-8', w)
    performance_dict[w] = {"torque":torque_sum, "power":w * torque_sum}
dict_to_xlsx(performance_dict, "re-round-50-8", "performance")