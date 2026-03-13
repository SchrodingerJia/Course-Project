import numpy as np

# 模电实验三：磁滞回线数据处理
def f(x, A1, A2, LOGx0, p):
    return A1 + (A2 - A1) / (1 + 10 ** ((LOGx0 - x) * p))

def f_1(y, A1, A2, LOGx0, p):
    return LOGx0 - np.log10((A2 - A1) / (y - A1) - 1) / p

Br1 = f(0, -0.84226, 0.94914, 131.1146, 0.00591)
Br2 = f(0, -0.91327, 0.88662, -132.67558, 0.0059)
Br = (Br2 - Br1) / 2

Hc1 = f_1(0, -0.91327, 0.88662, -132.67558, 0.0059)
Hc2 = f_1(0, -0.84226, 0.94914, 131.1146, 0.00591)
Hc = (Hc2 - Hc1) / 2

print(Br1)
print(Br2)
print(Br)
print()
print(Hc1)
print(Hc2)
print(Hc)