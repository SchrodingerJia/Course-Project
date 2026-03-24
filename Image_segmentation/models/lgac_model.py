import numpy as np
import scipy.ndimage as ndi
from scipy import signal
import matplotlib.pyplot as plt

def heaviside(x, epsilon=1.0):
    """光滑的Heaviside函数"""
    return 0.5 * (1 + (2 / np.pi) * np.arctan(x / epsilon))

def dirac_delta(x, epsilon=1.0):
    """光滑的Dirac delta函数"""
    return epsilon / (np.pi * (epsilon**2 + x**2))

def gaussian_kernel(sigma, size=None):
    """创建高斯核"""
    if size is None:
        size = int(2 * np.ceil(3 * sigma) + 1)
    kernel_1d = np.linspace(-(size // 2), size // 2, size)
    kernel_1d = np.exp(-0.5 * (kernel_1d / sigma) ** 2)
    kernel_2d = np.outer(kernel_1d, kernel_1d)
    return kernel_2d / np.sum(kernel_2d)

def edge_detection_function(grad_u0, beta=100):
    """边缘检测函数g"""
    return 1.0 / (1.0 + beta * grad_u0 ** 2)

def compute_gradient_magnitude(img):
    """计算图像梯度幅值"""
    grad_y, grad_x = np.gradient(img)
    return np.sqrt(grad_x**2 + grad_y**2)

def compute_local_contrast(img, window_size=3):
    """计算局部对比度 LCR_W"""
    from scipy.ndimage import maximum_filter, minimum_filter
    V_max = maximum_filter(img, size=window_size)
    V_min = minimum_filter(img, size=window_size)
    V_g = 1.0  # 对于归一化图像，最大强度为1.0
    LCR_W = (V_max - V_min) / V_g
    return LCR_W

def vector_shrinkage(x, y, g=None):
    """向量值shrinkage算子"""
    if g is not None:
        y = g / y
    norm = np.maximum(np.sqrt(x[0]**2 + x[1]**2), 1e-8)
    shrink = np.maximum(1.0 - y / norm, 0.0)
    result = np.zeros_like(x)
    result[0] = shrink * x[0]
    result[1] = shrink * x[1]
    return result

def gauss_seidel_step(s, d, b, lamda, phi_shape, bound_min=-2, bound_max=2):
    """Gauss-Seidel迭代更新水平集函数"""
    phi = np.zeros(phi_shape)
    d_x = d[0]
    d_y = d[1]
    b_x = b[0]
    b_y = b[1]
    # 扩展数组边界以便处理边界像素
    phi_ext = np.zeros((phi_shape[0]+2, phi_shape[1]+2))
    d_x_ext = np.pad(d_x, 1, mode='edge')
    d_y_ext = np.pad(d_y, 1, mode='edge')
    b_x_ext = np.pad(b_x, 1, mode='edge')
    b_y_ext = np.pad(b_y, 1, mode='edge')
    s_ext = np.pad(s, 1, mode='edge')
    for i in range(1, phi_shape[0]+1):
        for j in range(1, phi_shape[1]+1):
            # 计算 alpha
            alpha = (d_x_ext[i-1, j] - d_x_ext[i, j] +
                     d_y_ext[i, j-1] - d_y_ext[i, j] -
                     (b_x_ext[i-1, j] - b_x_ext[i, j] +
                      b_y_ext[i, j-1] - b_y_ext[i, j]))
            # 计算 beta
            beta = 0.25 * (phi_ext[i-1, j] + phi_ext[i+1, j] +
                           phi_ext[i, j-1] + phi_ext[i, j+1] -
                           (1.0/lamda) * s_ext[i, j] + alpha)
            # 限制在[-2, 2]范围内
            phi_ext[i, j] = np.clip(beta, bound_min, bound_max)
    # 提取内部区域
    phi = phi_ext[1:-1, 1:-1]
    return phi

def automatic_local_global_active_contour(img, IniLSF, max_iter=50, tol=1e-3,
                                         sigma=18, lamda1=15.4, lamda2=14,
                                         lamda_split=0.04, gamma=1e-2,
                                         beta=100, window_size=3, filter_sigma=1):
    """
    自动结合局部与全局信息的活动轮廓模型
    参数:
        img: 归一化的输入图像 (0-1范围)
        iniLSF: 初始化水平集函数 (在初始轮廓内为2，外部为-2)
        max_iter: 最大迭代次数
        tol: 收敛容差
        sigma: 高斯核标准差
        lamda1, lamda2: 拟合能量权重参数
        lamda_split: Split Bregman参数
        gamma: 权函数参数
        beta: 边缘检测函数参数
        window_size: 局部对比度窗口大小
    返回:
        segmented: 二值分割结果
        LSF: 最终水平集函数
    """
    # 高斯滤波
    img = ndi.gaussian_filter(img, sigma=filter_sigma)
    # 初始化变量
    phi = IniLSF.copy()
    u0 = img.copy()
    # 图像尺寸
    rows, cols = img.shape
    # 初始化辅助变量
    d = np.zeros((2, rows, cols))  # d = (d_x, d_y)
    b = np.zeros((2, rows, cols))  # b = (b_x, b_y)
    # 创建高斯核
    kernel_size = int(2 * np.ceil(3 * sigma) + 1)
    K_sigma = gaussian_kernel(sigma, kernel_size)
    # 计算图像梯度幅值
    grad_mag = compute_gradient_magnitude(u0)
    # 计算边缘检测函数g
    g = edge_detection_function(grad_mag, beta)
    # 计算局部对比度
    LCR_W = compute_local_contrast(u0, window_size)
    avg_LCR_W = np.mean(LCR_W)
    # 迭代计数器
    iter_count = 0
    phi_old = phi.copy()
    phi_change_history = 0.0
    while iter_count < max_iter:
        # 1. 计算M1和M2
        M1 = heaviside(phi)
        M2 = 1.0 - M1
        # 2. 更新拟合函数f1, f2和均值常量c1, c2
        # f1 = (Kσ * (M1 * u0)) / (Kσ * M1)
        numerator_f1 = signal.convolve2d(M1 * u0, K_sigma, mode='same', boundary='symm')
        denominator_f1 = signal.convolve2d(M1, K_sigma, mode='same', boundary='symm')
        f1 = numerator_f1 / (denominator_f1 + 1e-8)
        # f2 = (Kσ * (M2 * u0)) / (Kσ * M2)
        numerator_f2 = signal.convolve2d(M2 * u0, K_sigma, mode='same', boundary='symm')
        denominator_f2 = signal.convolve2d(M2, K_sigma, mode='same', boundary='symm')
        f2 = numerator_f2 / (denominator_f2 + 1e-8)
        # c1 = ∫(u0 * M1) / ∫M1
        c1 = np.sum(u0 * M1) / (np.sum(M1) + 1e-8)
        # c2 = ∫(u0 * M2) / ∫M2
        c2 = np.sum(u0 * M2) / (np.sum(M2) + 1e-8)
        # 3. 计算权函数ω (根据式3-18)
        # ω = γ * average(LCR_W) * (1 - LCR_W)
        omega = gamma * avg_LCR_W * (1 - LCR_W)
        # 4. 计算局部强度拟合力F1和全局强度拟合力F2 (式3-7)
        # 预先计算一些项
        # 对于每个位置x，我们需要计算卷积项
        # 由于这涉及到双重积分，我们使用卷积来高效计算
        # 计算局部项
        term1_local = np.zeros_like(u0)
        term2_local = np.zeros_like(u0)
        for i in range(rows):
            for j in range(cols):
                # 局部窗口（简化实现）
                x = u0[i, j]
                # 局部拟合项
                # ∫ Kσ(y-x) |u0(x) - f1(y)|^2 dy
                local_window = max(1, kernel_size // 2)
                i_min = max(0, i - local_window)
                i_max = min(rows, i + local_window + 1)
                j_min = max(0, j - local_window)
                j_max = min(cols, j + local_window + 1)
                # 提取局部区域
                y_coords = np.arange(i_min, i_max)
                x_coords = np.arange(j_min, j_max)
                YY, XX = np.meshgrid(y_coords, x_coords, indexing='ij')
                # 计算核权重
                distances = np.sqrt((YY - i)**2 + (XX - j)**2)
                kernel_weights = np.exp(-0.5 * (distances / sigma)**2)
                kernel_weights = kernel_weights / np.sum(kernel_weights)
                # 计算局部积分
                term1_val = np.sum(kernel_weights * (x - f1[YY, XX])**2)
                term2_val = np.sum(kernel_weights * (x - f2[YY, XX])**2)
                term1_local[i, j] = term1_val
                term2_local[i, j] = term2_val
        # 计算全局项
        term1_global = (u0 - c1)**2
        term2_global = (u0 - c2)**2
        # 计算F1和F2
        F1 = (1 - omega) * (-lamda1 * term1_local + lamda2 * term2_local)
        F2 = omega * (-lamda1 * term1_global + lamda2 * term2_global)
        # 5. 计算s(x) = -(F1 + F2)
        s = -(F1 + F2)
        # 6. Split Bregman迭代
        # 6.1 更新水平集函数φ
        phi = gauss_seidel_step(s, d, b, lamda_split, phi.shape)
        # 6.2 更新辅助变量d
        # 计算∇φ
        phi_grad_y, phi_grad_x = np.gradient(phi)
        phi_grad = np.stack([phi_grad_x, phi_grad_y])
        # shrink_g(b^k + ∇φ^{k+1}, 1/λ)
        d = vector_shrinkage(b + phi_grad, 1.0/lamda_split, g)
        # 6.3 更新Bregman变量b
        b = b + phi_grad - d
        # 7. 检查收敛条件
        phi_change = np.linalg.norm(phi - phi_old) / np.sqrt(rows * cols)
        if phi_change < tol or abs(phi_change_history - phi_change) < 1e-2*tol:
            print(f"收敛于迭代 {iter_count}, 变化: {phi_change}")
            break
        phi_old = phi.copy()
        phi_change_history = phi_change
        iter_count += 1
        if iter_count % 10 == 0:
            print(f"迭代 {iter_count}, 变化: {phi_change}")
    print(f"完成 {iter_count} 次迭代")
    # 根据水平集函数生成分割结果
    if img[phi > 0].mean() > img[phi <= 0].mean():
        segmented = np.zeros_like(img, dtype=np.uint8)
        segmented[phi > 0] = 1
    else:
        segmented = np.zeros_like(img, dtype=np.uint8)
        segmented[phi <= 0] = 1
    return segmented, phi, None