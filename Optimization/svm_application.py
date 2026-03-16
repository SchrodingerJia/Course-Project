import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from optimization_methods import OptimizationSolver

def linear_svm(X, y):
    from cvxopt import matrix, solvers
    n_samples, n_features = X.shape
    P = matrix(np.outer(y, y) * np.dot(X, X.T).astype(np.float64))
    q = matrix(-np.ones(n_samples).astype(np.float64))
    A = matrix(y.reshape(1, -1).astype(np.float64))
    b = matrix(0.0)
    G = matrix(np.vstack((-np.eye(n_samples), np.eye(n_samples))).astype(np.float64))
    h = matrix(np.hstack((np.zeros(n_samples), np.ones(n_samples))).astype(np.float64))
    sol = solvers.qp(P, q, G, h, A, b)
    alpha = np.array(sol['x'])
    w = np.dot(X.T, alpha * y)
    b = y[0] - np.dot(X[0], w)
    return w, b

def SVM(X_train, y_train):
    def objective(Lamda: np.ndarray):
        return np.sum(Lamda)
    cons_list = []
    for i in range(y_train.shape[0]):
        cons_list.append(lambda omega_b: -y_train[i] * (omega_b[0] * X_train[i][0] + omega_b[1] * X_train[i][1] + omega_b[-1]) + 1)
    constraints = {'el': tuple(cons_list)}
    X0 = np.array([0.0, 1.0, 1.0])
    return objective, constraints, X0

if __name__ == '__main__':
    X, y = make_classification(n_samples=100, n_features=2, n_informative=2, n_redundant=0, n_clusters_per_class=1, flip_y=0, class_sep=1.6)
    y = -(2 * y - 1)
    plt.scatter(X[:, 0], X[:, 1], c=y, s=50, cmap='autumn')
    plt.show()
    w, b = linear_svm(X, y)
    print("权重向量w:", w)
    print("偏置项b:", b)
    solver = OptimizationSolver()
    objective, constraints, X0 = SVM(X, y)
    mX = solver.PRP(objective, constraints, X0)
    omega_b = mX[-1, -1]
    plt.scatter(X[:, 0], X[:, 1], c=y, s=50, cmap='autumn')
    def g(omega_b, x):
        return (-omega_b[-1] - omega_b[0] * x) / omega_b[1]
    x = np.arange(-4, 1, 0.1)
    plt.plot(x, g(omega_b, x))
    plt.show()
