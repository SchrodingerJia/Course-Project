import numpy as np
import matplotlib.pyplot as plt

def getplot(xlst, ylst, xname='x', yname='y', xunit='', yunit='', title='', getline=True):
    X = np.array(xlst).reshape(-1, 1) if type(xlst) != np.ndarray else xlst
    y = np.array(ylst).reshape(-1, 1) if type(ylst) != np.ndarray else ylst
    plt.scatter(X, y, color='red', zorder=1)
    if getline:
        X = np.concatenate([X, np.full(shape=(len(xlst), 1), fill_value=1)], axis=1)
        theta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)
        plt.plot(X[:, 0], X.dot(theta), color='blue', zorder=0)
    ax1 = plt.gca()
    if float(theta[1]) < 0:
        title += '{0} = {1:.3f}{2}{3:.3f}'.format(yname, float(theta[0]), xname, float(theta[1]))
    else:
        title += '{0} = {1:.3f}{2}+{3:.3f}'.format(yname, float(theta[0]), xname, float(theta[1]))
    ax1.set_title(title)
    ax1.set_ylabel(yname + '/' + yunit)
    ax1.set_xlabel(xname + '/' + xunit)
    plt.show()

def getplots(ifolsts=[], xunit='', yunit='', xlabel='', ylabel='', title='', getline=True):
    defaultcolor = ['red', 'blue', 'green', 'purple', 'black', 'brown']
    defaultmarker = ['.', '^', 'v']
    for i in range(len(ifolsts)):
        X = np.array(ifolsts[i][0]).reshape(-1, 1)
        Y = np.array(ifolsts[i][1]).reshape(-1, 1)
        xname = ifolsts[i][2]
        yname = ifolsts[i][3]
        color = ifolsts[i][4] if len(ifolsts[i]) >= 5 else defaultcolor[i]
        marker = ifolsts[i][5] if len(ifolsts[i]) >= 6 else defaultmarker[i]
        label = ifolsts[i][6] if len(ifolsts[i]) >= 7 else yname + '-' + xname
        plt.scatter(X, Y, color=color, marker=marker, label=label, zorder=1)
        if getline:
            X = np.concatenate([X, np.full(shape=(len(X), 1), fill_value=1)], axis=1)
            theta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(Y)
            plt.plot(X[:, 0], X.dot(theta), color=color, zorder=0)
    ax1 = plt.gca()
    ax1.set_title(title)
    ax1.set_ylabel(ylabel + '/' + yunit)
    ax1.set_xlabel(xlabel + '/' + xunit)
    plt.legend(loc='upper right')
    plt.show()

def getcurves(infolsts=[], xunit='', yunit='', xlabel='', ylabel='', title=''):
    pi = 3.1415927
    defaultcolor = ['red', 'blue', 'green', 'purple', 'black', 'brown']
    for i in range(len(infolsts)):
        xname = infolsts[i][3]
        yname = infolsts[i][4]
        color = infolsts[i][5] if len(infolsts[i]) >= 6 else defaultcolor[i]
        label = infolsts[i][6] if len(infolsts[i]) >= 7 else yname + '-' + xname
        if type(infolsts[i][2]) != str:
            X = np.arange(0, 4 * pi / infolsts[i][1], 0.1 / infolsts[i][1])
            Y = infolsts[i][0] * np.sin(infolsts[i][1] * X + infolsts[i][2] / 180 * pi)
            plt.plot(X, Y, color=color, label=label, zorder=0)
        elif infolsts[i][2] == 'tri':
            k = 2 * infolsts[i][0] / (pi / infolsts[i][1])
            for j in range(4):
                X = np.arange(j * pi / infolsts[i][1], (j + 1.005) * pi / infolsts[i][1], 0.05 / infolsts[i][1])
                Y = (-1) ** j * k * (X - (pi / infolsts[i][1]) * (2 * j + 1) / 2)
                plt.plot(X, Y, color=color, zorder=0)
            plt.plot([], [], color=color, label=label)
        elif infolsts[i][2] == 'sqr':
            for j in range(4):
                X = np.arange((j * pi + 0.05) / infolsts[i][1], (j + 1) * pi / infolsts[i][1], 0.05 / infolsts[i][1])
                Y = (-1) ** j * infolsts[i][0] * np.ones_like(X)
                plt.plot(X, Y, color=color, zorder=0)
                X_ = np.arange((j + 1) * pi / infolsts[i][1], (j + 1) * pi / infolsts[i][1] + 0.05 / infolsts[i][1], 0.0001 / infolsts[i][1])
                Y_ = (-1) ** (j + 1) * ((2 * infolsts[i][0]) / (0.05 / infolsts[i][1])) * (X_ - ((j + 1) * pi / infolsts[i][1] + 0.025 / infolsts[i][1]))
                plt.plot(X_, Y_, color=color, zorder=0)
            plt.plot([], [], color=color, label=label)
    ax1 = plt.gca()
    ax1.set_title(title)
    ax1.set_ylabel(ylabel + '/' + yunit)
    ax1.set_xlabel(xlabel + '/' + xunit)
    plt.legend(loc='upper right')
    plt.show()

def getsubcurves(infolsts=[], xunit='', yunit='', xlabel='', ylabel='', title=''):
    fig, ax = plt.subplots(len(infolsts), 1)
    ax[0].set_title(title)
    pi = 3.1415927
    defaultcolor = ['red', 'blue', 'green', 'purple', 'black', 'brown']
    for i in range(len(infolsts)):
        X = np.arange(0, 4 * pi / infolsts[i][1], 0.1 / infolsts[i][1])
        Y = infolsts[i][0] * np.sin(infolsts[i][1] * X + infolsts[i][2] / 180 * pi)
        xname = infolsts[i][3]
        yname = infolsts[i][4]
        color = infolsts[i][5] if len(infolsts[i]) >= 6 else defaultcolor[i]
        label = infolsts[i][6] if len(infolsts[i]) >= 7 else yname + '-' + xname
        ax[i].plot(X, Y, color=color, label=label, zorder=0)
        ax[i].set_ylabel(ylabel + '/' + yunit)
        ax[i].set_yticks(np.arange(-int(infolsts[0][0]) - 1, int(infolsts[0][0]) + 1.5, (2 * int(infolsts[0][0]) + 2) / 4))
        ax[i].legend(loc='upper right')
        ax[i].set_xlabel(xlabel + '/' + xunit)
    plt.show()