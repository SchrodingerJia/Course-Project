import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.model_selection import ParameterGrid
from utils.data_loader import load_image
from models.cv_model import init_LSF
from models.tcm_model import prior_constraint_active_contour, eliminate_small_regions
from utils.plot_utils import plot_results_tcm

dataset = 'data/images/tcm'
types = ['.png', '.jpg', '.bmp']
images = {}
for file in os.listdir(dataset):
    if '-l' in file:
        name = file.split('-l')[0]
        for type in types:
            if os.path.exists(dataset+'/'+name+type):
                images[name+type] = file
print(images)

param = ParameterGrid({
    'sigma': [5],
    'lambda1': [5.5,],
    'lambda_split': [0.006,],
    'alpha': [0.4],
    'beta': [10],
    'sigma_filter': [1.6],
})

for image_file, label_file in images.items():
    img = load_image('data/images/tcm/'+image_file)
    preLSF = load_image('data/images/tcm/'+label_file)
    preLSF = (1 - preLSF < 1e-6).astype(np.float32)
    # 初始化水平集函数
    iniLSF = init_LSF(img, None)
    # 应用结合先验约束项的活动轮廓模型
    print(f"正在处理 {image_file}...")
    for params in param:
        if 'lambda1' in params:
            params['lambda2'] = params['lambda1'] * 10/11
            params['tol'] = params['lambda1'] * 5e-4
        print(params)
        segmented, final_lsf = prior_constraint_active_contour(
            img, preLSF, iniLSF, **params
        )
        # 绘制结果
        plot_results_tcm(img, iniLSF, preLSF, segmented, final_lsf, filename='results/TCM/'+image_file.split('.')[0]+'_segmented.png')
        a_lsf = eliminate_small_regions(final_lsf, 3e-2*min(np.count_nonzero(segmented), np.count_nonzero(1 - segmented)))
        segmented = a_lsf > 0
        plot_results_tcm(img, iniLSF, preLSF, segmented, a_lsf, filename='results/TCM_a/'+image_file.split('.')[0]+'_segmented.png')