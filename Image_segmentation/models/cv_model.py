from skimage.segmentation import chan_vese
from skimage.filters import gaussian
from skimage import io, img_as_float
import scipy.io as sio
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import math

def load_image(path):
    if path.endswith('.mat'):
        mat = sio.loadmat(path)
        # assume the image is the first non-meta variable
        for k in mat:
            if not k.startswith('__'):
                img = mat[k]
                break
        img = img.astype(np.float64)
    else:
        img = img_as_float(io.imread(path, as_gray=True))
    img = (img - img.min()) / (img.max() - img.min() + 1e-8)
    return img

def init_LSF(img, SEED=None):
    IniLSF = np.ones((img.shape[0],img.shape[1]),img.dtype)
    if SEED is None:
        centre = (img.shape[0]//2,img.shape[1]//2)
    elif isinstance(SEED, int):
        np.random.seed(SEED)
        random_x = np.random.randint(img.shape[0]//4, img.shape[0]-img.shape[0]//4)
        random_y = np.random.randint(img.shape[1]//4, img.shape[1]-img.shape[1]//4)
        centre = (random_x, random_y)
    elif isinstance(SEED, tuple):
        centre = SEED
    else:
        raise ValueError("SEED must be an integer or a tuple of (x, y) coordinates")
    IniLSF[centre[0]-img.shape[0]//4:centre[0]+img.shape[0]//4,
           centre[1]-img.shape[1]//4:centre[1]+img.shape[1]//4] = -1
    IniLSF=-IniLSF
    return IniLSF

def cv_segmentation(img, IniLSF='chekerboard'):
    img_smooth = gaussian(img, sigma=1)
    cv_result = chan_vese(img_smooth, mu=0.08, lambda1=1, lambda2=1, tol=1e-6,
                          dt=0.5, init_level_set=IniLSF, extended_output=True)
    segmented, phi, energies = cv_result
    return segmented, phi, energies

def cv_segmentation_multiphase_adaptive(img, IniLSF='chekerboard', intensity_threshold=0.1):
    # 预处理：高斯平滑
    img_smooth = gaussian(img, sigma=1)
    # 初始分割
    cv_result = chan_vese(
        img_smooth,
        mu=0.07,
        lambda1=0.6,
        lambda2=1,
        tol=1e-5,
        dt=0.5,
        init_level_set=IniLSF,
        extended_output=True
    )
    segmented, phi, energies = cv_result
    # 分析分割区域的强度分布
    foreground_intensity = img[segmented > 0]
    # 检查是否需要进行多相分割
    fg_std = np.std(foreground_intensity) if len(foreground_intensity) > 0 else 0
    segmented_multi = np.zeros_like(img, dtype=np.int32)
    phis = [phi]
    energies_list = [energies]
    current_phase = 1
    fg_seg = segmented
    while fg_std > intensity_threshold and len(foreground_intensity) > 10 and current_phase < 5:
        mask = fg_seg > 0
        # 取亮的为前景
        fg_mask = mask if np.mean(img[mask]) > np.mean(img[~mask]) else ~mask
        fg_img = img.copy()
        # 前景轮廓处的均值代替背景值
        foreground_contour = np.logical_and(fg_mask, np.logical_xor(phi > 0, np.roll(phi, 1, axis=0) > 0))
        fg_img[~fg_mask] = np.mean(img[foreground_contour])
        # 重新归一化
        fg_img = (fg_img - fg_img.min()) / (fg_img.max() - fg_img.min() + 1e-8)
        cv_fg = chan_vese(
            fg_img,
            mu=0.02,
            lambda1=0.8,
            lambda2=1,
            tol=2e-6,
            dt=0.3,
            init_level_set=IniLSF,
            extended_output=True
        )
        fg_seg, fg_phi, fg_energies = cv_fg
        mask = fg_seg > 0
        # 取亮的为前景
        new_mask = mask if np.mean(img[mask]) > np.mean(img[~mask]) else ~mask
        segmented_multi[fg_mask & ~new_mask] = current_phase
        current_phase += 1
        segmented_multi[fg_mask & new_mask] = current_phase
        current_phase += 1
        phis.append(fg_phi)
        energies_list.append(fg_energies)
        foreground_intensity = img[new_mask]
        fg_std = np.std(foreground_intensity) if len(foreground_intensity) > 0 else 0
        phi = fg_phi
    if current_phase == 1:
        # 如果不需要多相分割，返回二值结果
        segmented_multi = segmented.astype(np.int32)
    return segmented_multi, phis, energies_list

def mat_math(img, intput, type):
    output=intput
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if type=="atan":
                output[i,j] = math.atan(intput[i,j])
            if type=="sqrt":
                output[i,j] = math.sqrt(intput[i,j])
    return output