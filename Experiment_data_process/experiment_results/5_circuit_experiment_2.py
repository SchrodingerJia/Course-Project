from utils.plotting import getplots

# 电路实验二：U-I特性曲线
I = [5.0, 12.5, 19.3, 25.3, 32.7]
U = [5.37, 4.23, 3.19, 2.28, 1.16]
I1 = [5.0, 12.7, 19.8, 25.3, 32.7]
U1 = [5.39, 4.21, 3.13, 2.29, 1.16]
I2 = [5.0, 12.6, 19.9, 25.4, 32.6]
U2 = [5.32, 4.17, 3.02, 2.23, 1.11]

ifolsts = [
    (I, U, 'I', 'U', 'red', 'o', 'Original U'),
    (I1, U1, 'I\'', 'U\'', 'blue', '^', 'Thevenin U\''),
    (I2, U2, 'I\'\'', 'U\'\'', 'green', 'v', 'Norton U\'\'')
]
getplots(ifolsts, 'mA', 'V', 'I', 'U', 'U-I Curves')