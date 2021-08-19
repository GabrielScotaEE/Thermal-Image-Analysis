import cv2 as cv
import os
import numpy as np
import matplotlib.pyplot as plt
from numpy.core.numeric import count_nonzero
from numpy.lib.function_base import average
import math
import time
from imgProcessor import *


list_files = os.listdir('./images')
list_o2r_pixels = []
list_area_percent_roi = []
list_area_percent_total = []
data = []
colorbar = False
average_temp = []
max_temp = []
count = 0

# Creating processor object
processor = imgProcessor()

# Creating map with all colors
map = processor.loadMapCSV('mapColors.csv')

for image in list_files:
    
    img = cv.imread('./images/{}'.format(image))
    
    rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    # Croping image to ignore the colorbar in bottom and
    # the Flir texts
    img = img[70:170,:]
    
    # Converting image domain to HSV.
    hsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)
    
    # Selecting the area with the colorbar
    if colorbar is False:
        crop_colorbar = rgb_img[226:227,71:182]
        
        colorbar = True

    # Getting the color interval that we want to study on hsv img.
    mask = processor.filter_hsv_colors(hsv)
    
    # Checking if mask has pixels nonZero, i.e white pixels
    # Obs: mask is a grayscale image.
    if cv.countNonZero(mask)>0:

        # Call getContours 
        contours = processor.getContours(mask)
        
        # Call find edge to get extreme points
        west,east,top,bot = processor.find_edge_points(contours)

        # Building image only with Color of Interest (coi)
        rgb_coi, coi = processor.build_coi(mask,img)
        crop_coiImg = coi[top:bot,west:east]
        
        # Converting the image color domain bgr to rgb to show in plt.show()
        rgb_crop_coi = cv.cvtColor(crop_coiImg, cv.COLOR_BGR2RGB)

        # Showing images
        processor.show_images(rgb_crop_coi,rgb_img,count)

        # Getting only nonBlack pixels and storing in ignore_black       
        ignore_black = processor.ignoreBlackPixels(rgb_crop_coi)
        
        crop_colorbar = list(crop_colorbar)
        

        # Calculating temperature in calcTemp
        temperature = processor.calcTemp(ignore_black, crop_colorbar, map)
            
        plt.show()
        
        max_temp.append(max(temperature))

        print("Number of orange-to-red pixels: {}".format(cv.countNonZero(mask)))
        print('The maximum temperature in this image: {}'.format(max(temperature)))
        print('The minimum temperature in this image: {}'.format(min(temperature)))
    else:
        mask_green = processor.filterHSVThresholdConfigurable(hsv,[30,0,0],[40,255,255])
        contours = processor.getContours(mask_green)
        
        west,east,top,bot = processor.find_edge_points(contours)

        # Building image only with Color of Interest (coi)
        rgb_coi, coi = processor.build_coi(mask_green,img)
       
        crop_coiImg = coi[:,105:165]
        rgb_crop_coi = cv.cvtColor(crop_coiImg, cv.COLOR_BGR2RGB)

        # Showing images
        processor.show_images(rgb_crop_coi,rgb_img,count)

        # Getting only nonBlack pixels and storing in ignore_black       
        ignore_black = processor.ignoreBlackPixels(rgb_crop_coi)
        
        crop_colorbar = list(crop_colorbar)
        

        # Calculating temperature in calcTemp
        temperature = processor.calcTemp(ignore_black, crop_colorbar, map)
        
        plt.show()
        max_temp.append(max(temperature))
        print("Number of green pixels: {}".format(cv.countNonZero(mask_green)))
        print('The maximum temperature in this image: {}'.format(max(temperature)))
        print('The minimum temperature in this image: {}'.format(min(temperature)))

    print("Total pixels: {}".format(int(hsv.size/3)))

   
    # plt.imshow(mask, cmap='gray')   # this colormap will display in black / white
    # plt.show()
    ratio_total = cv.countNonZero(mask)/(hsv.size/3)#------- % Against Total Area
    ratio_roi = cv.countNonZero(mask)/(2000) # ----- % Against ROI Area
    list_o2r_pixels.append(cv.countNonZero(mask))
    list_area_percent_roi.append(np.round(ratio_roi*100, 3))
    list_area_percent_total.append(np.round(ratio_total*100, 3))
    count += 1



print('The max temperature in each image: {}'.format(max_temp))


fig, axes = plt.subplots(nrows=1, ncols=3)
fig.tight_layout()
voltage_list = [0,13000,15000,17000,19000,21000,23000]
# N° of pixels x area percent (ratio)
plt.subplot(131)
plt.plot(list_area_percent_roi,list_o2r_pixels, 'k')
plt.ylabel('Number of pixels orange to red')
plt.xlabel('Area Percent  (%)')
plt.axis([0, 100, 0, 2000])

# Ratio x Voltage
plt.subplot(132)
plt.plot(list_area_percent_total,voltage_list)
plt.ylabel('Voltage (V)')
plt.xlabel('Area Percent Full Image (%)')
plt.axis([0, math.ceil(list_area_percent_total[-1]), 0, 25000])

# Max temp x Voltage
plt.subplot(133)
plt.plot(voltage_list,max_temp,'ro')
plt.xlabel('Voltage (V)')
plt.ylabel('Max Temp (C°)')
plt.axis([0, 25000, 20, 26])


plt.show()


