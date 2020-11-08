import math
from random import *
from xfoil import XFoil
from xfoil.model import Airfoil
import numpy as np
import pandas as pd
from dict_df_excel import dict_to_xlsx


array6409 = np.loadtxt("NACA6409.dat", skiprows=1)
array2412 = np.loadtxt("NACA2412.dat", skiprows=1)
naca6409 = Airfoil(x=array6409[:, 0], y=array6409[:, 1])
naca2412 = Airfoil(x=array2412[:, 0], y=array2412[:, 1])


def get_max_cl(Re, r):
    """
    Analyze airfoil at a fixed Re,
    changing aoa from 10 to 15 by 0.1
    and returns cl, cd, aoa that makes maximum cl
    """
    xf = XFoil()
    if r <= 0.175: 
        xf.airfoil = naca6409
    else:
        xf.airfoil = naca2412
    xf.Re = Re
    xf.Re = Re
    xf.max_iter = 200
    xf.n_crit = 9.00
    xf.xtr = [1.00, 1.00]
    xf.M = 0
    a_seq, cl_seq, cd_seq, cm_seq, cp_seq = xf.aseq(10,15,0.1)
    # ignore nan by making it 0
    cl_seq = np.nan_to_num(cl_seq)
    # find the maximum cl 
    cl_maxi = np.max(cl_seq)
    # index of the maximum cl
    idx = np.argmax(cl_seq)
    return round(cl_maxi,2),round(a_seq[idx],2), round(cd_seq[idx],2)


def get_re(r, cl, aoa, arctan, rel_v, blade_number):
    """
    Calculate Re and chord length
    """
    chord = 8*math.pi*r*(1-math.cos(math.radians(arctan-aoa))) / blade_number / cl
    Re = round(rel_v * chord / 0.00001511 / 100) * 100
    return Re, chord


def random_iteration(r, w):
    """
    Find cl, aoa, chord length, Re at particular r-position by iteration
    """
    density = 1.225
    blade_number = 6
    wind_v = round(-168.75*r**2-36.75*r+20.05 , 2)
    blade_v = r*w
    rel_v = round(math.sqrt(blade_v**2 + wind_v**2),2)
    arctan = round(math.degrees(math.atan2(wind_v, blade_v)), 2)
    # cl is a random float in range 1.0 to 1.7
    cl = uniform(1.0, 1.7)
    # aoa is a random float in range 10 to 15
    aoa = uniform(10, 15)
    treeHit = 0
    Re = get_re(r, cl, aoa, arctan, rel_v, blade_number)[0]
    new_cl, new_a, new_cd = get_max_cl(Re, r)
    new_Re, new_chord = get_re(r, round(new_cl, 2), round(new_a, 2), arctan, rel_v, blade_number)
    re_devi = abs((new_Re - Re) / Re)
    # iterate until Re_deviation goes under 5%
    while re_devi > 0.05:
        Re = new_Re
        new_cl, new_a, new_cd = get_max_cl(new_Re, r)
        new_Re, new_chord = get_re(r, new_cl, new_a, arctan, rel_v, blade_number)
        re_devi = abs((new_Re - Re) / Re)
        treeHit += 1
        # stop iteration over 10 times
        if treeHit > 10:
            break
    force_reference = 0.5 * density * rel_v**2 * 0.0125 * round(new_chord, 3)
    return {
        "r": r,
        "arctan": arctan, 
        "chord": round(new_chord, 3), 
        "aoa": new_a, 
        "cl": new_cl, 
        "cd": new_cd, 
        "Re": new_Re,
        "lift": new_cl * force_reference, 
        "drag": new_cd * force_reference,
        "torque": r * (new_cl * force_reference * math.sin(math.radians(arctan - new_a)) - new_cd * force_reference * math.cos(math.radians(arctan - new_a)))
    }


angular_speeds = np.arange(0,170,10)
# angular_speeds = [160]
r_positions = np.arange(0.025, 0.2, 0.0125)
# r_positions = [0.025]
performance_dict = {}
for w in angular_speeds:
    position_dict = {}
    torque_sum = 0
    for position in r_positions:
        position_dict[position] = random_iteration(round(position, 4), w)
        torque_sum += random_iteration(round(position, 4), w)["torque"]
    dict_to_xlsx(position_dict, '6-iteration', w)
    performance_dict[w] = {"torque":torque_sum, "power":w * torque_sum}
dict_to_xlsx(performance_dict, "6-iteration", "performance")
