import os
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from utils import utils
from PIL import Image
from tqdm import tqdm
import torch
import torch.nn.functional as F
import time
from IPython import embed
if __name__ == '__main__':
    opt = TestOptions().parse()  # get test options
    opt.num_threads = 0   # test code only supports num_threads = 1
    opt.batch_size = 1    # test code only supports batch_size = 1
    opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.no_flip = True
    dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
    model = create_model(opt)      # create a model given opt.model and other options
    if len(opt.pretrain_model_path):
        model.load_pretrain_model()
    else:
        model.setup(opt)               # regular setup: load and print networks; create schedulers

    if len(opt.save_as_dir):
        save_dir = opt.save_as_dir
    else:
        save_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch))  
        if opt.load_iter > 0:  # load_iter is 0 by default
            save_dir = '{:s}_iter{:d}'.format(save_dir, opt.load_iter)
    os.makedirs(save_dir, exist_ok=True)

    print('creating result directory', save_dir)

    network = model.netG
    network.eval()

    for i, data in tqdm(enumerate(dataset), total=len(dataset)):
        #embed()
        inp = data['LR']
        
        print(inp.shape)
#        inp = F.interpolate(inp, size=[16, 16], mode="bicubic")

        # print(inp.shape)
        elapsed_time = 0
        with torch.no_grad():
            start_time = time.time()
            output_SR = network(inp)
            elapsed_time += time.time() - start_time
           # print(output_SR.shape)
           
        output_sr_img = utils.tensor_to_img(output_SR, normal=True)

        # Get image path and construct save path
        img_path = data['LR_paths']  # Assumes 'LR_paths' is a list of strings
        save_path = os.path.join(save_dir, os.path.basename(img_path[0]))

        # Ensure save directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the SR image
        save_img = Image.fromarray(output_sr_img)
        save_img.save(save_path)
    print(elapsed_time/1000)


       
