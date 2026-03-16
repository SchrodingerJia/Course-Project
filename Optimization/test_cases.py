import numpy as np
from optimization_methods import OptimizationSolver

def test1():
    def objective(X: np.ndarray):
        return 100 * (X[1] - X[0] ** 2) ** 2 + (1 - X[0]) ** 2
    constraints = {}
    X0 = np.array([2.0, -3.0])
    return objective, constraints, X0

def test2():
    def objective(X: np.ndarray):
        return X[0] ** 2 + X[1] ** 2
    def eg_cons1(X: np.ndarray):
        return -(X[0] ** 2 + X[1] ** 2 - 1)
    def eq_cons1(X: np.ndarray):
        return X[0] + X[1] - 3
    def el_cons1(X: np.ndarray):
        return X[0] ** 2 + X[1] ** 2 + 2 * X[0] - 36
    constraints = {'el': (eg_cons1, el_cons1), 'eq': (eq_cons1,)}
    X0 = np.array([-2.0, 5.0])
    return objective, constraints, X0

def test3():
    def objective(X: np.ndarray):
        return 5 - np.exp(-(X[0] ** 2 + X[1] ** 2) / 16)
    def eq_cons1(X: np.ndarray):
        return X[0] + X[1] - 2
    constraints = {'eq': (eq_cons1,)}
    X0 = np.array([-3.0, 5.0])
    return objective, constraints, X0

def test4():
    def objective(X: np.ndarray):
        return np.cos(X[0]) + 2 * np.cos(X[1])
    def eq_cons1(X: np.ndarray):
        return X[0] + X[1]
    constraints = {'eq': (eq_cons1,)}
    X0 = np.array([1.0, -1.0])
    return objective, constraints, X0

def test5():
    def objective(x, A=10):
        n = len(x)
        return A * n + np.sum(x ** 2 - A * np.cos(2 * np.pi * x))
    constraints = {}
    X0 = np.array([i * 1.0 + 10 * (-1) ** i for i in range(10)])
    return objective, constraints, X0

if __name__ == '__main__':
    solver = OptimizationSolver()
    # 测试用例1
    objective, constraints, X0 = test1()
    mX = solver.PRP(objective, constraints, X0)
    solver.plot_process(objective, mX)
    # 测试用例2
    objective, constraints, X0 = test2()
    mX = solver.PRP(objective, constraints, X0)
    solver.plot_process(objective, mX)
    # 测试用例3
    objective, constraints, X0 = test3()
    mX = solver.PRP(objective, constraints, X0)
    solver.plot_process(objective, mX)
    # 测试用例4
    objective, constraints, X0 = test4()
    mX = solver.PRP(objective, constraints, X0)
    solver.plot_process(objective, mX)
    # 测试用例5
    objective, constraints, X0 = test5()
    mX = solver.PRP(objective, constraints, X0)
