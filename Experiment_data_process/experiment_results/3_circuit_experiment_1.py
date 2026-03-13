from utils.plotting import getplots

# 电路实验一：U-I特性曲线
I = [3.72, 2.32, 1.19, 0.99, 0.75]
U = [5.58, 5.79, 5.96, 5.99, 6.03]
I1 = [3.72, 2.32, 1.19, 0.99, 0.75]
U1 = [5.58, 5.79, 5.96, 5.99, 6.03]
I2 = [3.72, 2.32, 1.19, 0.99, 0.75]
U2 = [5.58, 5.79, 5.96, 5.99, 6.03]

ifolsts = [
    (I, U, 'I', 'U', 'red', 'o', 'Original U'),
    (I1, U1, 'I\'', 'U\'', 'blue', '^', 'Thevenin U\''),
    (I2, U2, 'I\'\'', 'U\'\'', 'green', 'v', 'Norton U\'\'')
]
getplots(ifolsts, 'mA', 'V', 'I', 'U', 'U-I Curves')