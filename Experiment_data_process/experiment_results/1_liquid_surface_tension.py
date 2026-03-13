from utils.data_processing import deduction, printE, avgddt, standard_error
from utils.physics_quantity import Physicsnum

#实验数据
m=[0,500,1000,1500,2000,2500,3000,3500]
V=[0.005,0.538,1.079,1.607,2.139,2.668,3.202,3.734]
dV=deduction(V)
d=[32.86,32.88,32.90,32.88,32.88]
D=[34.70,34.70,34.70,34.72,34.72]
V30=[1.839,1.835,1.836,1.839,1.827]
V40=[1.849,1.851,1.845,1.854,1.848]

#数据作图
#getplot(m,V,'m','V','10^-6 kg','mV')

#仪器误差
iste=0.0005*0.0005

#物理量表:
m=Physicsnum(0.0005,0.0005**2,'kg')
g=Physicsnum(9.78,0,'kg*m*s^-2')
dV=Physicsnum(avgddt(V),standard_error(dV),'mV')
pi=Physicsnum(3.14159,0,'1')
d=Physicsnum(d,0.02,unit='mm')
D=Physicsnum(D,0.01,unit='mm')
V30=Physicsnum(V30,0.001,'mV')
V40=Physicsnum(V40,0.001,'mV')

#公式:
L=pi*(d+D)
K=m*g/dV
a30=V30*K/L
a40=V40*K/L
a30.name='α(29.7℃)'
a30.unit.str='N/mm'
a40.name='α(39.0℃)'
a40.unit.str='N/mm'

#输出
print(avgddt(V))
print(dV)
print(L)
print(a30)
printE(a30,7.10e-5)
print(a40)
printE(a40,6.94e-5)
