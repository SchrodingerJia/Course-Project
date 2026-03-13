import numpy as np
from math import sqrt
from .useful_numbers import Usefulnum, Uncertainty

def average(lst):
    sum = 0
    for i in lst:
        sum += i
    avg = sum / len(lst)
    return avg

def variance(lst):
    avg = average(lst)
    sum = 0
    for i in lst:
        sum += (i - avg) ** 2
    vrc = sum / len(lst)
    return vrc

def standard_deviation(lst):
    vrc = variance(lst)
    sdd = sqrt(vrc)
    return sdd

def standard_error(lst):
    vrc = variance(lst)
    sde = sqrt(vrc / (len(lst) - 1))
    sde = Usefulnum(sde)
    return sde

def overall_uncertainty(lst, iste):
    sde = standard_error(lst)
    oau = sqrt(sde.value ** 2 + iste ** 2)
    oau = Uncertainty(oau)
    return oau

def avgddt(lst):
    l = len(lst)
    dl = int(l / 2 if l % 2 == 0 else (l - 1) / 2)
    sum = 0
    for i in range(dl):
        sum += lst[i + dl] - lst[i]
    return sum / dl ** 2

def deduction(lst):
    newlst = [(lst[i + 1] - lst[i]) for i in range(len(lst) - 1)]
    return newlst

def Subtract(num, numlst):
    newlst = []
    for i in numlst:
        newlst.append(num - i)
    return newlst

def Divide(numlst, num):
    newlst = []
    for i in numlst:
        newlst.append(i / num)
    return newlst

def ln(numlst):
    newlst = []
    for i in numlst:
        newlst.append(float(np.log(i)))
    return newlst

def inverselst(lst):
    newlst = [1 / i for i in lst]
    return newlst

def printE(cvalue, truevalue):
    print('E = {0:.2%}'.format(abs(cvalue.average.value - truevalue) / truevalue))