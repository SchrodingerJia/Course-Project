import numpy as np
from math import exp
import sympy as sp

# 利润数据
x0 = np.array([2.67, 3.13, 3.25, 3.36, 3.56, 3.72])
n = len(x0)

# 使用条件判断：级比检验
def con(lamdak, n):
    lower_bound = exp(-2.0 / (n + 1))
    upper_bound = exp(2.0 / (n + 1))
    if lamdak > lower_bound and lamdak < upper_bound:
        return True
    else:
        return False

lamda = x0[:-1] / x0[1:]
for k in range(0, n - 1):
    if not con(lamda[k], n):
        print('不满足级比检验，不可采用灰色预测模型进行预测')
        break
print('满足级比检验，可以采用灰色预测模型进行预测')

# GM(1,1)建模求解
def GM11(x0, nk=3):
    # x0:原始序列, nk:预测后nk年
    # 累加生成序列
    x1 = np.cumsum(x0)
    # 均值生成序列
    z1 = (x1[1:] + x1[:-1]) / 2
    # 最小二乘法求解参数
    B = np.vstack([-z1, np.ones(n - 1)]).T
    Y = x0[1:].T
    u = np.linalg.inv(B.T.dot(B)).dot(B.T).dot(Y)
    a = u[0]
    b = u[1]
    print('GM(1,1)模型发展系数为:{0:.2f}'.format(a))
    # 时间响应解
    def x(k):
        return (x0[0] - b / a) * exp(-a * k) + b / a
    x_1 = np.array([x(k) for k in range(n + nk)])
    # 还原预测值
    x_0 = np.concatenate((np.array([x0[0]]), np.diff(x_1)))
    # 计算相对误差
    cha = x0 - x_0[:n]
    delta = abs(cha / x0) * 100
    avg_delta = np.average(delta)
    print('GM(1,1)模型平均相对误差为:{0:.2f}'.format(avg_delta))
    return x_0[n:n + nk]

# GM(1,2)建模求解
def GM21(x0, nk=3):
    # x0:原始序列, nk:预测后nk年
    # 累加生成序列
    x1 = np.cumsum(x0)
    # 1阶累减序列
    a1x0 = np.diff(x0)
    # 均值生成序列
    z1 = (x1[1:] + x1[:-1]) / 2
    # 最小二乘法求解参数
    B = np.vstack([-x0[1:], -z1, np.ones(n - 1)]).T
    Y = a1x0.T
    u = np.linalg.inv(B.T.dot(B)).dot(B.T).dot(Y)
    print(u)
    a1 = u[0]
    a2 = u[1]
    b = u[2]
    print('GM(2,1)模型发展系数为:{0:.2f},{1:.2f}'.format(a1, a2))
    # 解析求解
    t = sp.symbols('t')
    x = sp.Function('x')(t)
    eq = sp.Eq(sp.diff(x, t, 2) + a1 * sp.diff(x, t) + a2 * x, b)
    try:
        # 边界条件：x(0)=x1[0], x(n-1)=x1[-1]
        sol = sp.dsolve(eq, ics={x.subs(t, 0): x1[0], x.subs(t, n - 1): x1[-1]})
        xt = sol.rhs  # 提取解的右侧表达式
        # 转换为可调用的函数
        x_func = sp.lambdify(t, xt, 'numpy')
    except Exception as e:
        print(f"解析求解失败: {str(e)}")
    x_1 = np.array([x_func(k) for k in range(n + nk)])
    # 还原预测值
    x_0 = np.concatenate((np.array([x0[0]]), np.diff(x_1)))
    # 计算相对误差
    cha = x0 - x_0[:n]
    delta = abs(cha / x0) * 100
    avg_delta = np.average(delta)
    print('GM(2,1)模型平均相对误差为:{0:.2f}'.format(avg_delta))
    return np.around(x_0[n:n + nk], 2)

# 未来三年利润预测与对比
# GM(1,1)
profit_1 = GM11(x0, 3)
print('使用GM(1,1)模型预测未来三年的利润为:{0:.2f},{1:.2f},{2:.2f}'.format(profit_1[0], profit_1[1], profit_1[2]))
# GM(2,1)
profit_2 = GM21(x0, 3)
print('使用GM(2,1)模型预测未来三年的利润为:{0:.2f},{1:.2f},{2:.2f}'.format(profit_2[0], profit_2[1], profit_2[2]))