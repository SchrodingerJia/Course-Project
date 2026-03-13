import numpy as np
from utils.data_processing import Divide, ln, inverselst
from utils.plotting import getplot

# RLC实验数据处理
t = [32 + i * 292 for i in range(9)]
Uc = [6.6, 4.4, 3.2, 2.2, 1.52, 1.12, 0.88, 0.64, 0.56]

t = Divide(t, 1000)
Y = ln(Divide(Uc, 10))
print(Y)
getplot(t, Y, 't', 'ln(Uc/E)', 'ms', getline=True)

# 时间常数与电容、电阻关系
trc1 = [0.00112, 5.40, 45.0, 262]
Crc = [0.0022, 10, 100, 470]
trc2 = [5.8, 11.2, 18.4, 45]
Rrc = [10, 50, 100, 500]

trl1 = [60, 18.4, 12]
Rrl = [100, 500, 900]
trl2 = [11.2, 45.6, 90]
Lrl = [10, 50, 100]

getplot(Crc, trc1, 'C', 'τ', 'μF', 'ms', title='R=500Ω   ')
getplot(Rrc, trc2, 'R', 'τ', 'Ω', 'ms', title='C=100μF   ')
getplot(inverselst(Rrl), trl1, 'R^-1', 'τ', 'Ω^-1', 'μs', title='L=10mH   ')
getplot(Lrl, trl2, 'L', 'τ', 'mH', 'μs', title='R=1000Ω   ')