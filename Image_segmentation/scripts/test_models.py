import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skimage.segmentation import chan_vese
from utils.data_loader import load_image
from models.cv_model import init_LSF, cv_segmentation, cv_segmentation_multiphase_adaptive
from models.rsf_model import rsf_segmentation
from models.lgac_model import automatic_local_global_active_contour
from utils.plot_utils import plot_results

# 测试图像
test_images = [
    'special_image.bmp',
    '4.bmp',
    'synthetic_test.png',
    '2.bmp',
    '3.bmp',
    '1.bmp',
    '5.bmp',
    '6.png',
    'brain_img75.mat',
    'myBrain_axial.bmp',
]
# 模型
models = {
    'CV': cv_segmentation,
    'multi_CV': cv_segmentation_multiphase_adaptive,
    'RSF': rsf_segmentation,
    'LGAC': automatic_local_global_active_contour,
}

def test(model_name, init='chekerboard'):
    model_func = models[model_name]
    for img_file in test_images:
        print(f'Running {model_name} on {img_file}...')
        img = load_image('data/images/cv_rsf/'+img_file)
        if init=='chekerboard':
            _, IniLSF, _ = chan_vese(img, max_num_iter=0, extended_output=True)
        else:
            IniLSF = init_LSF(img, init)
        segmented, phi, energies = model_func(img, IniLSF=IniLSF)
        init_type = init if init is not None else 'centre'
        plot_results(img, IniLSF, segmented, phi, filename = f'results/{model_name}/{init_type}/'+img_file.split('.')[0]+'_segmented.png')

def test_all():
    for init in ['chekerboard', None]:
        for model_name, model_func in models.items():
            print(f'Running {model_name}...')
            for img_file in test_images:
                img = load_image('data/images/cv_rsf/'+img_file)
                if init=='chekerboard':
                    _, IniLSF, _ = chan_vese(img, max_num_iter=0, extended_output=True)
                else:
                    IniLSF = init_LSF(img, init)
                segmented, phi, energies = model_func(img, IniLSF=IniLSF)
                init_type = init if init is not None else 'centre'
                plot_results(img, IniLSF, segmented, phi, filename = f'results/{model_name}/{init_type}/'+img_file.split('.')[0]+'_segmented.png')

if __name__ == '__main__':
    # 示例：测试RSF模型，使用中心初始化
    test('RSF', None)