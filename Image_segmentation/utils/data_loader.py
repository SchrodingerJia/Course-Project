import scipy.io as sio
from skimage import io, img_as_float
import numpy as np

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