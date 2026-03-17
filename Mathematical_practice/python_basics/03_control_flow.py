# 流程控制练习

## 九九乘法表

for i in range(9):
    for j in range(i+1):
        print(f'{j+1}*{i+1}={(i+1)*(j+1)}',end = '\t')
    print()

## 三角形判断

from math import sqrt
# 浮点数判断精度
eta = 1e-3
# 输入分割为列表，转化为float类型并升序排序
a,b,c = sorted([float(i) for i in input('输入a b c空格隔开:').split(' ')])
if not a+b > c:
    print('不能构成三角形！')
else:
    # 面积计算
    p = (a+b+c)/2
    S = sqrt(p*(p-a)*(p-b)*(p-c))
    # 三角形类型判断
    tri_type = ''
    iso_flag_ab = abs(a-b) < eta
    iso_flag_bc = abs(b-c) < eta
    iso_flag_ac = abs(a-c) < eta
    # 等边条件
    equ_flag = (iso_flag_ab and iso_flag_bc) and iso_flag_ac
    # 等腰条件
    iso_flag = (iso_flag_ab or iso_flag_bc) or iso_flag_ac
    # 直角条件
    rig_flag = abs(c**2 - a**2 - b**2) < eta
    # 非一般条件
    spe_flag = (equ_flag or iso_flag) or rig_flag
    if not spe_flag:
        tri_type += '一般'
    elif equ_flag:
        tri_type += '等边'
    elif iso_flag:
        tri_type += '等腰'
    if rig_flag:
        tri_type += '直角'
    # 面积保留5位小数
    print('为' + tri_type + '三角形,其面积为' + '{0:.5f}'.format(S))

## 猜数字

import random
random.seed(3)
# 获取随机数
ans = random.randint(1,100)
guess = int(input('请输入一个非负整数:'))
sum = 1
while(guess != ans):
    # 猜测次数计数
    sum += 1
    print('输入的数字偏'+ ('大' if guess>ans else '小') + ',请继续输入！')
    guess = int(input('请输入一个非负整数:'))
print(f'恭喜您，猜对了！共猜了{sum}次')

## 韩信点兵

for i in range(1001):
    if i % 3 == 2 and i % 5 == 3 and i % 7 == 2:
        print(i)