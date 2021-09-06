import cv2 as cv
import os
import numpy as np
import matplotlib.pyplot as plt
import math
import time
from imgProcessor import *
from colorMapper import *

list_files = os.listdir('./images')
list_o2r_pixels = []
list_area_percent_roi = []
list_area_percent_total = []
data = []
colorbar = False
average_temp = []
max_temp = []
count = 0

mapper = ColorMapper()

# Creating processor object
processor = imgProcessor()

# Using a map with all colors and ids to improove the performance.
# importing this map from a csv file.
# there is a function on imgProcessor()
# that build this for you --> createCSV_withColorsAndIds(memo) -- line 124.
# map will be used in calcTemp().  
map = mapper.loadMapCSV('mapColors.csv')

# This for runs over all elements (image name files)
# in list_files
for image in list_files:
    
    originalImg = cv.imread('./images/{}'.format(image))
    #plt.imshow(originalImg) # -- uncomment to see original image.
    rgb_img = cv.cvtColor(originalImg, cv.COLOR_BGR2RGB)
    # plt.imshow(rgb_img)
    # plt.show()
    # Croping image to ignore the colorbar in bottom and
    # the Flir texts on top
    originalImg = originalImg[70:170,:]
    
    # Converting image domain to HSV.
    hsv = cv.cvtColor(originalImg,cv.COLOR_BGR2HSV)
    
    # Selecting the area with the colorbar
    if colorbar is False:
        # was using 226:227,57:182
        crop_colorbar = rgb_img[226:227,71:182]
        colorbar = True

    # Getting the color interval that we want to study on hsv img.
    # check the colors in: https://i.stack.imgur.com/TSKh8.png
    # The 'count' var tell wich image is, from 0 to 7, zero to the first
    # and seven to the last one, 0 dont have orange-to-red pixels.
    if count > 0:
        # This var store the result of filter HSV, for orange-to-red colors
        mask = processor.filterHSVspeficColors(hsv,[0,0,0], [23,255,255], [150,0,0], [180,255,255])
        numberOfOrangetoRed = 'orange-to-red'
    else:
        # This var store the result of filter HSV, for green colors
        mask = processor.filterHSVspeficColors(hsv,[24,0,0],[40,255,255])
        numberofGreen = 'green'
 
    # Obs: mask is a grayscale image.
    # To see the result uncoment the line below
    #plt.imshow(mask)
    #plt.show()
  
    # Call getContours to find the edge points
    contours = processor.getContours(mask)
    
    # Call find edge to get extreme points.
    # The extreme points will be used to get exactly 
    # the Region of Interest (ROI)
    west,east,top,bot = processor.find_edge_points(contours,count)

    # Building the image only with Colors of Interest (coi)
    rgb_coi, coi = processor.build_coi(mask,originalImg)

    # Cropping img through edge points
    crop_coiImg = coi[top:bot,west:east]
    
    # Converting the image color domain bgr to rgb to show in plt.show()
    rgb_crop_coi = cv.cvtColor(crop_coiImg, cv.COLOR_BGR2RGB)

    # Getting only nonBlack pixels and storing in ignore_black       
    ignore_black = processor.ignoreBlackPixels(rgb_crop_coi)
    
    crop_colorbar = list(crop_colorbar)
    # Calculating temperature in calcTemp
    # You can give the input: map. If you already have
    # mapped all colors (better perfomance)
    temperature, _ = processor.calcTemp(ignore_black, crop_colorbar, map)
    max_temp.append(max(temperature))
    # Showing images
    processor.show_images(rgb_crop_coi,rgb_img,count, max(temperature))
    plt.show()
    
    if count > 0:
        print("Number of pixels:",numberOfOrangetoRed,cv.countNonZero(mask))
    else:
        print("Number of pixels:",numberofGreen,cv.countNonZero(mask))
    print('The maximum temperature in this image:',max(temperature))
    print('The minimum temperature in this image:',min(temperature))


    if count == 0:
        print("Total pixels:",int(hsv.size/3))

     
    ratio_total = cv.countNonZero(mask)/(hsv.size/3)#------- % Against Total Area
    ratio_roi = cv.countNonZero(mask)/(2000) #------ % Against ROI Area
    # The first img dont have orange to red (o2r) pixels
    # therefore it is unnecessary to append it value to some lists.
    if count > 0:
        list_area_percent_total.append(np.round(ratio_total*100, 3))
        list_o2r_pixels.append(cv.countNonZero(mask))
        list_area_percent_roi.append(np.round(ratio_roi*100, 3))
    else:
        list_area_percent_total.append(0)
    # Add 1 to count to change the index of files.
    count += 1

# To create a map with all colors just uncoment the code below
# and get the second output from calcTemp function, call it "memo".
# mapper.createCSV_withColorsAndIds(memo)

print('The max temperature in each image:',max_temp)


fig, axes = plt.subplots(nrows=1, ncols=3)
fig.tight_layout()
voltage_list = [0,13000,15000,17000,19000,21000,23000]
# N° of pixels x area percent (ratio)
plt.subplot(131)
plt.plot(list_o2r_pixels,list_area_percent_roi, color='red', marker='o', linestyle='dashed')
plt.xlabel('Number of pixels orange to red')
plt.ylabel('Area Percent  (%)')
plt.axis([0, 2000, 0, 100])

# Ratio x Voltage
plt.subplot(132)
plt.plot(voltage_list,list_area_percent_total, color='blue', marker='o', linestyle='dashed')
plt.xlabel('Voltage (V)')
plt.ylabel('Area Percent Full Image (%)')
plt.axis([0, 25000, 0, math.ceil(list_area_percent_total[-1])])

# Max temp x Voltage
plt.subplot(133)
plt.plot(voltage_list,max_temp,color='green', marker='o', linestyle='dashed')
plt.xlabel('Voltage (V)')
plt.ylabel('Max Temp (C°)')
plt.axis([0, 25000, 20, 26])


plt.show()


