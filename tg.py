import cv2 as cv
import os
import numpy as np
import matplotlib.pyplot as plt
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
# importing this map from a csv file.
# there is a function on imgProcessor()
# that build this for you --> createCSV_withColorsAndIds(memo) -- line 120.
# map will be used in calcTemp.  
map = processor.loadMapCSV('mapColors.csv')

for image in list_files:
    
    img = cv.imread('./images/{}'.format(image))
    #plt.imshow(img)
    rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    # plt.imshow(rgb_img)
    # plt.show()
    # Croping image to ignore the colorbar in bottom and
    # the Flir texts on top
    img = img[70:170,:]
    
    # Converting image domain to HSV.
    hsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)
    
    # Selecting the area with the colorbar
    if colorbar is False:
        # was using 226:227,57:182
        crop_colorbar = rgb_img[226:227,71:182]
        colorbar = True

    # Getting the color interval that we want to study on hsv img.
    # check the colors in: https://i.stack.imgur.com/TSKh8.png
    # The 'count' var tell wich image is, from 0 to 7, zero to the first
    # and seven to the last one.
    if count > 0:
        # This var store the result of filter HSV, for orange-to-red colors
        mask = processor.filterHSVspeficColors(hsv,[0,0,0], [23,255,255], [150,0,0], [180,255,255])
        numberOfOrangetoRed = 'orange-to-red'
    else:
        # This var store the result of filter HSV, for green colors
        mask = processor.filterHSVspeficColors(hsv,[26,0,0],[40,255,255])
        numberofGreen = 'green'
 
    # Checking if mask has pixels nonZero, i.e white pixels
    # Obs: mask is a grayscale image.
    # to see the result uncoment the line below
    #plt.imshow(mask)
    #plt.show()
  
    # Call getContours to find the edge points
    contours = processor.getContours(mask)
    
    # Call find edge to get extreme points.
    # The extreme points will be used to get exactly 
    # the Region of Interest (ROI)
    west,east,top,bot = processor.find_edge_points(contours,count)

    # Building the image only with Colors of Interest (coi)
    rgb_coi, coi = processor.build_coi(mask,img)

    # Cropping img through edge points
    crop_coiImg = coi[top:bot,west:east]
    
    # Converting the image color domain bgr to rgb to show in plt.show()
    rgb_crop_coi = cv.cvtColor(crop_coiImg, cv.COLOR_BGR2RGB)

    # Showing images
    processor.show_images(rgb_crop_coi,rgb_img,count)
    plt.show()
    # Getting only nonBlack pixels and storing in ignore_black       
    ignore_black = processor.ignoreBlackPixels(rgb_crop_coi)
    
    crop_colorbar = list(crop_colorbar)
    
    # Calculating temperature in calcTemp
    # You can give the input: map. If you already have
    # mapped all colors (better perfomance)
    temperature, _ = processor.calcTemp(ignore_black, crop_colorbar, map)
    
    max_temp.append(max(temperature))
    if count > 0:
        print("Number of {} pixels: {}".format(numberOfOrangetoRed,cv.countNonZero(mask)))
    else:
        print("Number of {} pixels: {}".format(numberofGreen,cv.countNonZero(mask)))
    print('The maximum temperature in this image: {}'.format(max(temperature)))
    print('The minimum temperature in this image: {}'.format(min(temperature)))


    if count == 0:
        print("Total pixels: {}".format(int(hsv.size/3)))

     
    ratio_total = cv.countNonZero(mask)/(hsv.size/3)#------- % Against Total Area
    ratio_roi = cv.countNonZero(mask)/(2000) # ----- % Against ROI Area
    # The first img dont have orange to red (o2r) pixels
    # therefore it is unnecessary to append it value to some lists.
    if count > 0:
        list_area_percent_total.append(np.round(ratio_total*100, 3))
        list_o2r_pixels.append(cv.countNonZero(mask))
        list_area_percent_roi.append(np.round(ratio_roi*100, 3))
    else:
        list_area_percent_total.append(0)
    count += 1

# To create a map with all colors just uncoment the code below
# and get the second output from calcTemp function, call it "memo".
# processor.createCSV_withColorsAndIds(memo)

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


