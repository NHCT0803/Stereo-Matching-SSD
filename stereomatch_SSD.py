#!/usr/bin/env python
# --------------------------------------------------------------------
# Simple sum of squared differences (SSD) stereo-matching using Numpy
# --------------------------------------------------------------------

# Copyright (c) 2016 David Christian
# Licensed under the MIT License
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
#plt.ion()

def stereo_match(left_img, right_img, kernel_half, max_offset):
    # Load in both images, assumed to be RGBA 8bit per channel images
    left_img = Image.open(left_img).convert('L')
    left = np.asarray(left_img)
    right_img = Image.open(right_img).convert('L')
    right = np.asarray(right_img)    
    w, h = left_img.size  # assume that both images are same size   
    
    # Depth (or disparity) map
    depth = np.zeros((w, h), np.uint8)
    depth.shape = h, w
       
    kernel_half = int(kernel_half)    
    offset_adjust = 255 / max_offset  # this is used to map depth map output to 0-255 range
      
    f, axarr = plt.subplots(2,2)
    axarr[0,0].title.set_text('left')
    axarr[0,1].title.set_text('right')
    axarr[1,0].title.set_text('disparity map')
    axarr[1,1].axis('off')
    axarr[0,0].imshow(left,'gray')
    axarr[0,1].imshow(right,'gray')
    
    for y in range(kernel_half, h - kernel_half):      #iterate rows
        print(".", end="", flush=True)  # let the user know that something is happening (slowly!)
        
        for x in range(kernel_half, w - kernel_half):   #iterate collumns
            #rgb_left = np.stack((left,)*3, axis=-1)
            #rgb_right = np.stack((right,)*3, axis=-1)
            best_offset = 0
            prev_ssd = 65534    #256 squared
            
            for offset in range(max_offset):        #iterate disparities
                ssd = 0
                ssd_temp = 0                            
                
                # v and u are the x,y of our local window search, used to ensure a good 
                # match- going by the squared differences of two pixels alone is insufficient, 
                # we want to go by the squared differences of the neighbouring pixels too
                for v in range(-kernel_half, kernel_half):
                    for u in range(-kernel_half, kernel_half):
                        # iteratively sum the sum of squared differences value for this block
                        # left[] and right[] are arrays of uint8, so converting them to int saves
                        # potential overflow, and executes a lot faster 
                        ssd_temp = int(left[y+v, x+u]) - int(right[y+v, (x+u) - offset])  
                        ssd += ssd_temp * ssd_temp              
                
                # if this value is smaller than the previous ssd at this block
                # then it's theoretically a closer match. Store this value against
                # this block..
                if ssd < prev_ssd:
                    prev_ssd = ssd
                    best_offset = offset

            #rgb_left[y-kernel_half:y+kernel_half, x-kernel_half:x+kernel_half] = [255,0,0]
            #rgb_right[y-kernel_half:y+kernel_half, x-best_offset-kernel_half:x-best_offset+kernel_half] = [0,255,0]
            # set depth output for this x,y location to the best match
            depth[y, x] = best_offset * offset_adjust
            
        axarr[1,0].imshow(depth, 'gray')
        plt.pause(0.0001)

    # Convert to PIL and save it
    plt.show()
    Image.fromarray(depth).save('depth.png')

if __name__ == '__main__':
    stereo_match("view0.png", "view1.png", 3, 40) 

