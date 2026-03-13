from utils.physics_quantity import Physicsnum
from utils.data_processing import avgddt

# 杨氏模量实验
pi = Physicsnum(3.14159265)
g = Physicsnum(9.78, 0, 'm*s^-2', 'g')

L = Physicsnum(721.0, 0, 'mm', 'L', 0.8)
H = Physicsnum(682.0, 0, 'mm', 'H', 0.8)
D = Physicsnum(37.14, 0, 'mm', 'D', 0.02)

d0 = Physicsnum(-0.015, 0, 'mm', 'd0', 0.004)
dlst = [0.620, 0.618, 0.621, 0.623, 0.619, 0.620]
d = Physicsnum(dlst, 0, 'mm', 'd', 0.004) + d0
d.name = 'd'

dm = Physicsnum(1.00, 0, 'kg', '△m', 0.005)
xlst = [8.7, 13.4, 18.2, 23.3, 27.8, 31.6, 36.8, 41.2, 46.5, 50.8]
dx = Physicsnum(avgddt(xlst), 0.5, 'mm', '△x', 0.5)

E = dm * g * L * H / (pi * D * d ** 2 * dx) * 8
E.unit.str = 'N/mm^2'
E.name = 'E'
print(dm, g, L, H, D, d, dx, E, sep='\n')