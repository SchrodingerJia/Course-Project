import numpy as np
import scipy.ndimage as ndi
from scipy import signal
import matplotlib.pyplot as plt
from models.lgac_model import heaviside, edge_detection_function, compute_gradient_magnitude, vector_shrinkage, gaussian_kernel

def compute_rsf_data_term(img, phi, sigma=3.0, lambda1=1e-5, lambda2=1e-5):
    """
    计算RSF模型的数据项T(x) = p1(x) + p2(x)（式4-3）
    参数:
        img: 输入图像
        phi: 当前水平集函数
        sigma: 高斯核标准差
        lambda1, lambda2: 权重参数
    返回:
        T: 数据项
        f1, f2: 局部强度近似函数
    """
    # 计算Heaviside函数和掩模
    H_phi = heaviside(phi)
    M1 = H_phi
    M2 = 1.0 - H_phi
    # 创建高斯核
    kernel_size = int(2 * np.ceil(3 * sigma) + 1)
    K_sigma = gaussian_kernel(sigma, kernel_size)
    # 计算局部强度近似函数f1和f2（RSF模型）
    # f1 = (Kσ * (M1 * I)) / (Kσ * M1)
    numerator_f1 = signal.convolve2d(M1 * img, K_sigma, mode='same', boundary='symm')
    denominator_f1 = signal.convolve2d(M1, K_sigma, mode='same', boundary='symm')
    f1 = numerator_f1 / (denominator_f1 + 1e-8)
    # f2 = (Kσ * (M2 * I)) / (Kσ * M2)
    numerator_f2 = signal.convolve2d(M2 * img, K_sigma, mode='same', boundary='symm')
    denominator_f2 = signal.convolve2d(M2, K_sigma, mode='same', boundary='symm')
    f2 = numerator_f2 / (denominator_f2 + 1e-8)
    # 计算p1(x)和p2(x)（式4-3）
    # p1(x) = λ1 ∫ Kσ(y-x) |I(x) - f1(y)|^2 dy
    # p2(x) = -λ2 ∫ Kσ(y-x) |I(x) - f2(y)|^2 dy
    rows, cols = img.shape
    p1 = np.zeros_like(img)
    p2 = np.zeros_like(img)
    # 为了高效计算，我们可以将双重积分简化为卷积运算
    # 注意：这是一个近似，精确计算需要双重积分
    # 在实际应用中，这种近似通常足够好
    # 计算局部窗口大小
    local_window = max(1, kernel_size // 2)
    for i in range(rows):
        for j in range(cols):
            # 提取局部窗口
            i_min = max(0, i - local_window)
            i_max = min(rows, i + local_window + 1)
            j_min = max(0, j - local_window)
            j_max = min(cols, j + local_window + 1)
            # 创建局部坐标网格
            y_coords = np.arange(i_min, i_max)
            x_coords = np.arange(j_min, j_max)
            YY, XX = np.meshgrid(y_coords, x_coords, indexing='ij')
            # 计算高斯核权重
            distances = np.sqrt((YY - i)**2 + (XX - j)**2)
            kernel_weights = np.exp(-0.5 * (distances / sigma)**2)
            kernel_weights = kernel_weights / np.sum(kernel_weights)
            # 当前像素强度
            I_x = img[i, j]
            # 计算p1(x)
            f1_vals = f1[YY, XX]
            p1_val = np.sum(kernel_weights * (I_x - f1_vals)**2)
            p1[i, j] = lambda1 * p1_val
            # 计算p2(x)
            f2_vals = f2[YY, XX]
            p2_val = np.sum(kernel_weights * (I_x - f2_vals)**2)
            p2[i, j] = -lambda2 * p2_val
    # 计算数据项T(x)
    T = p1 + p2
    return T, f1, f2

def prior_constraint_active_contour(img, preLSF, iniLSF, max_iter=20, tol=1e-2,
                                   sigma=20, lambda1=16.5, lambda2=15,
                                   lambda_split=0.05, alpha=10, beta=100, sigma_filter=3.4):
    """
    结合先验约束项的图像分割模型
    参数:
        img: 归一化的输入图像 (0-1范围)
        preLSF: 预分割的水平集函数（先验约束项Φ_pre）
        iniLSF: 初始化水平集函数
        max_iter: 最大迭代次数
        tol: 收敛容差
        sigma: 高斯核标准差
        lambda1, lambda2: RSF数据项权重
        lambda_split: Split Bregman参数λ
        alpha: 先验约束项权重
        beta: 边缘检测函数参数
    返回:
        segmented: 二值分割结果
        LSF: 最终水平集函数
    """
    # 初始化变量
    phi = iniLSF.copy()
    phi_pre = preLSF.copy()
    u0 = img.copy()
    # 高斯滤波
    u0 = ndi.gaussian_filter(u0, sigma=sigma_filter)
    # 图像尺寸
    rows, cols = img.shape
    # 初始化辅助变量
    s = np.zeros((2, rows, cols))  # s = (s_x, s_y)
    h = np.zeros((2, rows, cols))  # h = (h_x, h_y)
    # 计算图像梯度幅值
    grad_mag = compute_gradient_magnitude(u0)
    # 计算边缘检测函数g
    g = edge_detection_function(grad_mag, beta)
    # 迭代计数器
    iter_count = 0
    phi_change_history = 0
    phi_old = phi.copy()
    # Split Bregman迭代
    while iter_count < max_iter:
        # 1. 计算数据项T(x)（式4-3）
        T, f1, f2 = compute_rsf_data_term(u0, phi, sigma, lambda1, lambda2)
        # 2. Split Bregman迭代
        # 2.1 固定s，求解Φ的子问题（式4-6）
        # 根据PDF第7页的离散化公式
        phi_new = np.zeros_like(phi)
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                # 计算v1: s_x(i-1,j) - s_x(i,j) + s_y(i,j-1) - s_y(i,j)
                v1 = (s[0, i-1, j] - s[0, i, j] +
                      s[1, i, j-1] - s[1, i, j])
                # 计算v2: h_x(i-1,j) - h_x(i,j) + h_y(i,j-1) - h_y(i,j)
                v2 = (h[0, i-1, j] - h[0, i, j] +
                      h[1, i, j-1] - h[1, i, j])
                # 计算v3: φ(i-1,j) + φ(i+1,j) + φ(i,j-1) + φ(i,j+1)
                v3 = (phi[i-1, j] + phi[i+1, j] +
                      phi[i, j-1] + phi[i, j+1])
                # 计算ξ = v1 - v2
                xi = v1 - v2
                # 计算β = (λ * v3 - T(i,j) + λ * ξ) + α * Φ_pre(i,j)
                beta_val = (lambda_split * v3 - T[i, j] +
                           lambda_split * xi + alpha * phi_pre[i, j])
                # 计算φ_new(i,j) = β / (α + 4λ)
                phi_new[i, j] = beta_val / (alpha + 4 * lambda_split)
        # 处理边界（使用边界复制）
        phi_new[0, :] = phi_new[1, :]
        phi_new[-1, :] = phi_new[-2, :]
        phi_new[:, 0] = phi_new[:, 1]
        phi_new[:, -1] = phi_new[:, -2]
        # 2.2 固定Φ，求解s的子问题（式4-7）
        # 计算∇φ_new
        phi_grad_y, phi_grad_x = np.gradient(phi_new)
        phi_grad = np.stack([phi_grad_x, phi_grad_y])
        # shrink_g(h^k + ∇φ^{k+1}, 1/λ) = shrink(h^k + ∇φ^{k+1}, g/λ)
        s = vector_shrinkage(h + phi_grad, 1.0/lambda_split, g)
        # 2.3 更新Bregman变量h（式4-6最后一行）
        h = h + phi_grad - s
        # 3. 更新水平集函数
        phi = phi_new
        # 4. 检查收敛条件
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
    segmented = np.zeros_like(img, dtype=np.uint8)
    segmented[phi > 0] = 1
    # segmented = eliminate_small_regions(segmented, 100)
    return segmented, phi

def eliminate_small_regions(matrix: np.ndarray,
                           area_threshold: int,
                           connectivity: int = 4) -> np.ndarray:
    """
    消除矩阵中面积不大于阈值的连续区域
    参数:
        matrix: 浮点数矩阵
        area_threshold: 面积阈值，小于等于此值的区域将被消除
        connectivity: 连通性定义，4或8连通（默认4）
    返回:
        处理后的矩阵
    """
    # 创建二值掩码：0值区域为0，非0值区域为1
    binary_mask = (matrix > 0).astype(np.uint8)
    # 获取连通组件
    if connectivity == 4:
        structure = ndi.generate_binary_structure(2, 1)
    elif connectivity == 8:
        structure = ndi.generate_binary_structure(2, 2)
    else:
        raise ValueError("connectivity必须是4或8")
    # 标记0区域（背景）
    zero_mask = (matrix <= 0).astype(np.uint8)
    labeled_zero, num_zero_regions = ndi.label(zero_mask, structure=structure)
    # 标记1区域（前景）
    one_mask = (matrix > 0).astype(np.uint8)
    labeled_one, num_one_regions = ndi.label(one_mask, structure=structure)
    # 创建结果矩阵的副本
    result = matrix.copy()
    # 处理0区域：小面积0区域变为1
    zero_sizes = ndi.sum(zero_mask, labeled_zero, range(num_zero_regions + 1))
    for label in range(1, num_zero_regions + 1):
        if zero_sizes[label] <= area_threshold:
            # 找到该区域的位置并设置为1（使用矩阵均值或1.0）
            region_mask = (labeled_zero == label)
            # 使用周围非0值的均值，如果没有则使用1.0
            if np.any(~region_mask):
                # 获取区域边界值
                result[region_mask] = np.mean(matrix[~region_mask & (matrix > 0)]) if np.any(matrix[~region_mask] > 0) else 1.0
            else:
                result[region_mask] = 1.0
    # 处理1区域：小面积1区域变为0
    one_sizes = ndi.sum(one_mask, labeled_one, range(num_one_regions + 1))
    for label in range(1, num_one_regions + 1):
        if one_sizes[label] <= area_threshold:
            # 找到该区域的位置并设置为0
            region_mask = (labeled_one == label)
            result[region_mask] = 0.0
    return result