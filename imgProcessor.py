import cv2 as cv
import os
import numpy as np
import matplotlib.pyplot as plt
from numpy.core.numeric import count_nonzero
from numpy.lib.function_base import average
import pandas as pd
import math
import time
import imutils
from functools import lru_cache
from colormath.color_objects import sRGBColor, LabColor, BaseRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import csv

class imgProcessor():

    def __init__(self, base_colorbarScale=19.96, maximum_colorbarScale=25, sizeCrop_colorbar=111) :
        self.base_scale = base_colorbarScale
        self.maximum_scale = maximum_colorbarScale
        self.crop_colorbar_columns = sizeCrop_colorbar
        self.memo = {}

        pass

    def filter_hsv_colors(self,hsv_image):

        hsv_color1 = np.asarray([0,0,0])   # white red
        hsv_color2 = np.asarray([23,255,255])   # dark orange
        hsv_color3 = np.asarray([150,0,0])   # white red/pink
        hsv_color4 = np.asarray([180,255,255])    # darker red

        mask1 = cv.inRange(hsv_image, hsv_color1, hsv_color2)
        mask2 = cv.inRange(hsv_image, hsv_color3, hsv_color4)
        mask = cv.bitwise_or(mask1,mask2)
        return mask
    
    def filterHSVThresholdConfigurable(self,hsv_image, lowerHSV: list, higherHSV: list, lowerHSV2= None, higherHSV2=None):

        hsv_color1 = np.asarray(lowerHSV)   
        hsv_color2 = np.asarray(higherHSV)   
        

        mask = cv.inRange(hsv_image, hsv_color1, hsv_color2)

        if (lowerHSV2 and higherHSV2) != None:
            hsv_color3 = np.asarray(lowerHSV2)   # white red/pink
            hsv_color4 = np.asarray(higherHSV2)    # darker red
            mask2 = cv.inRange(hsv_image, hsv_color3, hsv_color4)
            mask = cv.bitwise_or(mask,mask2)
            return mask

        return mask
   
    def find_edge_points(self,contours):
        list_coord_y =[]
        list_coord_x =[]
        
        for cnt in contours:
            for ct in cnt:
                for c in ct:
                    list_coord_x.append(c[0])
                    list_coord_y.append(c[1])
            
        extLeft = min(list_coord_x)
        extRight = max(list_coord_x)
        extTop = min(list_coord_y)
        extBot = max(list_coord_y)

        
        extTop = extTop-3
        extLeft = extLeft-3
        extBot = extBot+3
        extRight = extRight + 3

        return extLeft, extRight, extTop, extBot

    def build_coi(self, mask_img, orig_img):

        imask = mask_img>0
        coi = np.zeros_like(orig_img, np.uint8)
        coi[imask] = orig_img[imask]
        rgb_coi = cv.cvtColor(coi, cv.COLOR_BGR2RGB)
        return rgb_coi, coi

    def show_images(self, rgb_crop_img, rgb_original_img,count):

        fig, _ = plt.subplots(nrows=1, ncols=2)
        fig.tight_layout()
        plt.subplot(1,2,1)
        if count > 0:
            plt.title('Colors of Interest')
        else:
            plt.title('Croped original image')
        plt.imshow(rgb_crop_img)
        rgb_img_cropped = rgb_original_img[70:170,:]
        plt.subplot(1,2,2)
        plt.title('Original Image')
        plt.imshow(rgb_img_cropped)
        pass
    
    def getContours(self,mask):

        canny = imutils.auto_canny(mask)
        contours, _ = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        contours = np.array(contours)

        return contours

   
    def ignoreBlackPixels(self, croped_rgbCoiImg):
        ignore_black = set()
        rows = croped_rgbCoiImg.shape[0]
        columns = croped_rgbCoiImg.shape[1]

        # Appending only pixels != [0,0,0] <---  black color
        for row in range(rows):
            for col in range(columns):
                if list(croped_rgbCoiImg[row][col]) != [0, 0, 0]:
                    ignore_black.add(tuple(croped_rgbCoiImg[row][col]))
        ignore_black = list(ignore_black)                    
        
        return (ignore_black)

   
    def calcTemp(self, ignoredBlack, crop_colorbar, map=None):
        
        self.ignoredBlack = ignoredBlack
        self.crop_colorbar = crop_colorbar
        temperature = []
        #init = time.time()
        
            
        for self.element in range(len(ignoredBlack)):
            memo = None
            # Calculate the similarity of two collors
            # one from the image, another from the colorbar
            init = time.time()
            imPixel = str(self.ignoredBlack[self.element])
            
            if imPixel in map:
                id = map[imPixel]
                    
            else:
                id, memo = self.__compareTwoColors_similarity()
            
            end = time.time()
            #print(end-init)
            formula_temp = self.base_scale+((self.maximum_scale-self.base_scale)/self.crop_colorbar_columns)*id
            
            temperature.append(round(formula_temp,3))
        #end = time.time()
        if memo is not None:
            return temperature, memo
        else:
            return temperature
    
    
    def __compareTwoColors_similarity(self):
        similarityList = []
        
        # Comparing all pixels from img with pixels in colorbar
        # to see wich color is the nearest to it.
        imgPixel_tuple = tuple(self.ignoredBlack[self.element])
            
        if imgPixel_tuple in self.memo:
            return self.memo[imgPixel_tuple], self.memo
        else: 
            for index in range (self.crop_colorbar_columns):

                pixImg = np.asarray(self.ignoredBlack[self.element])
                colorSRGB_img = sRGBColor(pixImg[0]/255, pixImg[1]/255, pixImg[2]/255)

                pixColorBar = self.crop_colorbar[0][index]
                colorSRGB_colorbar = sRGBColor(pixColorBar[0]/255, pixColorBar[1]/255, pixColorBar[2]/255)
                
                # color1 refers to image
                color1_lab = convert_color(colorSRGB_img, LabColor)

                # # colors2 refers to colorbar
                color2_lab = convert_color(colorSRGB_colorbar, LabColor)
                
                delta_e = delta_e_cie2000(color1_lab, color2_lab)
                
                # distance = (pixImg[0]-pixColorBar[0])**2+(pixImg[1]-pixColorBar[1])**2+(pixImg[2]-pixColorBar[2])**2
                # distance = np.sqrt(distance)

                similarityList.append(delta_e)

            # Get the lowest value from the similarity list
            id = similarityList.index(min(similarityList))
            
            
            self.memo[imgPixel_tuple]=id
            return id, self.memo
        
    def printLikeaTable(self, list_area_percent_roi, list_o2r_pixels, list_area_percent_total, voltage_list):
        
        pixel_roi_df = pd.DataFrame(list(zip(list_area_percent_roi,list_o2r_pixels)), columns =['%','N° of pixels'])
        print(pixel_roi_df)
        pixel_total_df = pd.DataFrame(list(zip(list_area_percent_total,voltage_list)), columns =['%','Voltage'])
        print(pixel_total_df)

    def createCSV_withColorsAndIds(self, memo):
        data = []
        for key, value in memo.items():
            infos = []
            infos.append(key)
            infos.append(value)
            data.append(infos)
    
        header = ['color', 'id']
        with open('mapColors.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            # write multiple rows
            writer.writerows(data)
    
    def loadMapCSV(self, CSVnameFile):
        with open(CSVnameFile, encoding="utf8") as f:
            csv_reader = csv.DictReader(f)
            # skip the header
            next(csv_reader)
            # creating map with all colors
            map = {}
            # show the data
            for line in csv_reader:
                id = line['id']
                id = int(id.replace("'", ""))
                map[line['color']] = id
        return map