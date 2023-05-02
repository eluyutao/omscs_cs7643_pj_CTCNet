import numpy as np
from skimage.metrics import structural_similarity as compare_ssim
from PIL import Image
import os
from IPython import embed

def rgb2y_matlab(x):
    """Convert RGB image to illumination Y in Ycbcr space in matlab way.
    -------------
    # Args
        - Input: x, byte RGB image, value range [0, 255]
        - Ouput: byte gray image, value range [16, 235] 

    # Shape
        - Input: (H, W, C)
        - Output: (H, W) 
    """
    K = np.array([65.481, 128.553, 24.966]) / 255.0
    Y = 16 + np.matmul(x, K)
    return Y.astype(np.uint8)


def PSNR(im1, im2, use_y_channel=True):
    """Calculate PSNR score between im1 and im2
    --------------
    # Args
        - im1, im2: input byte RGB image, value range [0, 255]
        - use_y_channel: if convert im1 and im2 to illumination channel first
    """
    if use_y_channel:
        im1 = rgb2y_matlab(im1)
        im2 = rgb2y_matlab(im2)
    im1 = im1.astype(np.float)
    im2 = im2.astype(np.float)
    mse = np.mean(np.square(im1 - im2)) 
    return 10 * np.log10(255**2 / mse) 


def write_log(log_file, log_str):
    f = open(log_file, 'a')
    f.write(log_str + '\n')
    f.close()

def SSIM(gt_img, noise_img):
    """Calculate SSIM score between im1 and im2 in Y space
    -------------
    # Args
        - gt_img: ground truth image, byte RGB image
        - noise_img: image with noise, byte RGB image
    """
    gt_img = rgb2y_matlab(gt_img)
    noise_img = rgb2y_matlab(noise_img)
     
    ssim_score = compare_ssim(gt_img, noise_img, gaussian_weights=True, 
            sigma=1.5, use_sample_covariance=False)
    return ssim_score

def psnr_ssim_dir(gt_dir, test_dir):
    gt_img_list = sorted([x for x in sorted(os.listdir(gt_dir))])
    test_img_list = sorted([x for x in sorted(os.listdir(test_dir))])
    #  assert gt_img_list == test_img_list, 'Test image names are different from gt images.' 

    psnr_score = 0
    ssim_score = 0
    for gt_name, test_name in zip(gt_img_list, test_img_list):
        gt_img = Image.open(os.path.join(gt_dir, gt_name))
        test_img = Image.open(os.path.join(test_dir, test_name))
        gt_img = np.array(gt_img)
        test_img = np.array(test_img)
        psnr_score += PSNR(gt_img, test_img)
        ssim_score += SSIM(gt_img, test_img)
    return psnr_score / len(gt_img_list), ssim_score / len(gt_img_list)

if __name__ == '__main__':

    gt_dir = "/home2/ZiXiangXu/DataSets/spation_test_1000/"
    
    test_dirs = []
    input_txt = "/home2/ZiXiangXu/Last_ding/res4_jiu/list.txt"
    f = open(input_txt)
    for line in f:
        line = line.strip('\n')
        line = line.split(' ')
        test_dirs.append(line[0])
    f.close
   
    output_dir = "/home2/ZiXiangXu/Last_ding/res4_jiu/log_test/"
    logtxt_dir = os.path.join(output_dir, 'log.txt')

    for td in test_dirs:
        result = psnr_ssim_dir(td, gt_dir)
        
        log_str = '%.4f' % (result[0])
        write_log(logtxt_dir, log_str)
        
        print(td, result)


