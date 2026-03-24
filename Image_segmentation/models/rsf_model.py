import numpy as np
import cv2
import math
from skimage.filters import gaussian
from models.cv_model import mat_math

def _rsf_iteration(LSF, img, mu=0.08, nu=0.003 * 255 * 255, epison=1,
                    step=0.1, lambda1=1, lambda2=0.9, sig=16):
    kernel = np.ones((sig*4+1,sig*4+1),np.float64)/(sig*4+1)**2
    Drc = (epison / math.pi) / (epison*epison+ LSF*LSF)
    Hea = 0.5*(1 + (2 / math.pi)*mat_math(img,LSF/epison,"atan"))
    Iy, Ix = np.gradient(LSF)
    s = mat_math(img,Ix*Ix+Iy*Iy,"sqrt")
    Nx = Ix / (s+0.000001)
    Ny = Iy / (s+0.000001)
    Mxx,Nxx =np.gradient(Nx)
    Nyy,Myy =np.gradient(Ny)
    cur = Nxx + Nyy
    Length = nu*Drc*cur
    Lap = cv2.Laplacian(LSF,-1)
    Penalty = mu*(Lap - cur)
    KIH = cv2.filter2D(Hea*img,-1,kernel)
    KH = cv2.filter2D(Hea,-1,kernel)
    f1 = KIH / KH
    KIH1 = cv2.filter2D((1-Hea)*img,-1,kernel)
    KH1 = cv2.filter2D(1-Hea,-1,kernel)
    f2 = KIH1 / KH1
    R1 = (lambda1- lambda2)*img*img
    R2 = cv2.filter2D(lambda1*f1 - lambda2*f2,-1,kernel)
    R3 = cv2.filter2D(lambda1*f1*f1 - lambda2*f2*f2,-1,kernel)
    RSFterm = -Drc*(R1-2*R2*img+R3)
    LSF = LSF + step*(Length + Penalty + RSFterm)
    #plt.imshow(s, cmap ='gray'),plt.show()
    return LSF

def rsf_segmentation(img, IniLSF, n=300):
    img = gaussian(img, sigma=1)
    LSF = IniLSF
    img = np.uint8(img * 255)
    for i in range(1,n):
        LSF = _rsf_iteration(LSF, img)
    segmented = LSF > 0
    return segmented.astype(np.int32), LSF, None