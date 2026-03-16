import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class OptimizationSolver:
    def __init__(self):
        pass

    @staticmethod
    def grad(f, X: np.ndarray):
        n = X.shape[0]
        gradient = []
        for i in range(n):
            delta_X = np.zeros_like(X)
            if X[i] != 0:
                delta_X[i] += X[i] * 1e-7
            else:
                delta_X[i] = 1e-8
            gradient.append((f(X + delta_X) - f(X)) / delta_X[i])
        gradient = np.array(gradient)
        return gradient

    @staticmethod
    def nabs(X):
        X = list(X)
        d = 0
        for i in X:
            d += i ** 2
        return d ** 0.5

    @staticmethod
    def wolfe_powell(f, xk, d, rho=0.1, sigma=0.1, eta=0.1):
        lamda = 1
        beta = 0.5
        alpha = 1.5
        phi_1 = f(xk)
        phi_prime_1 = np.dot(OptimizationSolver.grad(f, xk), d)
        while True:
            phi_2 = f(xk + lamda * d)
            if phi_2 <= phi_1 + rho * phi_prime_1 * lamda:
                phi_prime_2 = np.dot(OptimizationSolver.grad(f, xk + lamda * d), d)
                if phi_prime_2 >= sigma * phi_prime_1 * lamda:
                    return lamda
                else:
                    lamda = alpha * lamda
            else:
                lamda = beta * lamda
            if lamda < 1e-9:
                return 0

    @staticmethod
    def beta(f, X_k, X_kp):
        grad_k = OptimizationSolver.grad(f, X_k)
        grad_kp = OptimizationSolver.grad(f, X_kp)
        return (grad_kp.T.dot(grad_kp - grad_k)) / (grad_k.T.dot(grad_k))

    @staticmethod
    def phi(lamda):
        if lamda > 0:
            return lamda ** 2
        else:
            return 0

    @staticmethod
    def psi(lamda):
        return lamda ** 2

    @staticmethod
    def penalty(objective, constraints: dict, factor: float = 1e5):
        def auxiliary_function(X: np.ndarray):
            result = objective(X)
            alpha = 0
            for cons_type in constraints.keys():
                match cons_type:
                    case 'el':
                        g = OptimizationSolver.phi
                    case 'eq':
                        g = OptimizationSolver.psi
                    case _:
                        pass
                for con in constraints[cons_type]:
                    alpha += g(con(X))
            result += factor * alpha
            return result
        return auxiliary_function

    def PRP(self, objective, constraints, initial_value: np.ndarray, factor: float = 1e3, epsilon: float = 1e-4, n=3, epoch: int = 2):
        f = self.penalty(objective, constraints, factor)
        X = []
        d = []
        m = []
        mX = []
        X.append(initial_value)
        d.append(-self.grad(f, initial_value))
        for ep in range(epoch):
            for k in range(n):
                if self.nabs(self.grad(f, X[k])) < epsilon:
                    print(f'找到最优值！最优值为{objective(X[k]):.3f}，最优点为{np.around(X[k], 4)}，迭代次数为{ep * n + k}')
                    for j in range(k + 1, n):
                        X.append(np.array([np.nan for _ in range(initial_value.shape[0])]))
                    mX.append(X)
                    return np.array(mX)
                else:
                    print('Searching for λ')
                    lamda = self.wolfe_powell(f, X[k], d[k])
                    if lamda < 1e-6:
                        print(f'λ=0，迭代停止！最优值为{objective(X[k]):.3f}，最优点为{np.around(X[k], 4)}，迭代次数为{ep * n + k}')
                        for j in range(k, n):
                            X.append(np.array([np.nan for _ in range(initial_value.shape[0])]))
                        mX.append(X[:-1])
                        return np.array(mX)
                    X.append(X[k] + lamda * d[k])
                    d.append(-self.grad(f, X[k + 1]) + self.beta(f, X[k], X[k + 1]) * d[k])
                    print(X[k + 1])
            mX.append(X[:-1])
            m.append(objective(X[-2]))
            tmp = X[-1]
            X = [tmp]
            d = [-self.grad(f, X[0])]
            print(f'epoch {ep} is finished, the best result is {m[-1]}')
        m = np.array(m).T
        best_f = np.amin(m)
        best_epoch = int(np.argmin(m))
        mX = np.array(mX)
        best_X = mX[-1, best_epoch]
        print(f'优化终止，最优值为{best_f:.3f}，最优点为{np.around(best_X, 3)}')
        return mX

    @staticmethod
    def plot_process(objective, mX):
        mX = mX.reshape((-1, 2))
        m = []
        for i in range(mX.shape[0]):
            m.append(objective(mX[i]))
        m = np.array(m)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(x, y)
        X_arr = np.array([X, Y])
        Z = objective(X_arr)
        ax.plot_surface(X_arr[0], X_arr[1], Z, cmap='viridis', alpha=0.5, zorder=0)
        xscatter = mX[:, 0]
        yscatter = mX[:, 1]
        zscatter = m
        ax.scatter(xscatter, yscatter, zscatter, c='r', marker='o', zorder=1)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        plt.show()

    @staticmethod
    def minimize_process(objective, mX):
        mX = mX.reshape((-1, 2))
        m = []
        for i in range(mX.shape[0]):
            m.append(objective(mX[i]))
        m = np.array(m)
        plt.figure()
        X = np.linspace(0, m.shape[0], m.shape[0])
        plt.plot(X, m)
        plt.show()
