import matplotlib.pyplot as plt
import os
import numpy as np

def plot_results(img, iniLSF, segmented, phis, filename = None):
    plt.rcParams['font.sans-serif']=['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(13, 5))
    plt.rcParams['font.size'] = 20
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    # 初始轮廓线
    plt.subplot(1, 3, 1)
    plt.imshow(img, cmap='gray')
    if isinstance(iniLSF, list):
        for i, phi in enumerate(iniLSF):
            plt.contour(phi, [0], colors=colors[i])
    else:
        plt.contour(iniLSF, [0], colors='r')
    plt.title('初始轮廓线')
    plt.axis('off')
    # 分割结果
    plt.subplot(1, 3, 2)
    plt.imshow(segmented, cmap='gray')
    plt.title('分割结果')
    plt.axis('off')
    # 轮廓曲线与原始图像
    plt.subplot(1, 3, 3)
    plt.imshow(img, cmap='gray')
    if isinstance(phis, list):
        for i, phi in enumerate(phis):
            plt.contour(phi, [0], colors=colors[i])
    else:
        plt.contour(phis, [0], colors='r')
    plt.title('最终轮廓线')
    plt.axis('off')
    # plt.tight_layout()
    if filename is not None:
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        plt.savefig(filename)
    else:
        plt.savefig('segmented.png')
    plt.show()

def plot_results_tcm(img, iniLSF, preLSF, segmented, phis, filename = None):
    plt.rcParams['font.sans-serif']=['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(13, 5))
    plt.rcParams['font.size'] = 20
    # 初始轮廓线
    plt.subplot(1, 3, 1)
    plt.imshow(img, cmap='gray')
    plt.contour(iniLSF, [0], colors='r')
    plt.contour(preLSF, [0], colors='b')
    plt.title('初始轮廓线与先验约束项')
    plt.axis('off')
    # 分割结果
    plt.subplot(1, 3, 2)
    plt.imshow(segmented, cmap='gray')
    plt.title('分割结果')
    plt.axis('off')
    # 轮廓曲线与原始图像
    plt.subplot(1, 3, 3)
    plt.imshow(img, cmap='gray')
    plt.contour(phis, [0], colors='r')
    plt.title('最终轮廓线')
    plt.axis('off')
    # plt.tight_layout()
    if filename is not None:
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        plt.savefig(filename)
    else:
        plt.savefig('segmented.png')
    plt.show()