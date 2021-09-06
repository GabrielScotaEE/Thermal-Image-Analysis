import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import imutils
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


class imgProcessor():
    '''
    Knowing that the scale goes from 19 to 25 the image was cropped
    in the colorbar resulting in 125 corresponding columns. 
    However, in the first 14 columns the colors were not "growing" gradually
    so it was decided to start from the 15th column. 
    Therefore the base of the scale was shifted to 19.72
    '''
    def __init__(self, base_colorbarScale=19.72, maximum_colorbarScale=25, sizeCrop_colorbar=111) :
        self.base_scale = float(base_colorbarScale)
        self.maximum_scale = int(maximum_colorbarScale)
        self.crop_colorbar_columns = int(sizeCrop_colorbar)
        self.memo = {}
        self.voltage_list = [0,13000,15000,17000,19000,21000,23000]

        pass
    
    # This function creates a mask with only 
    # the colors sent by the user in HSV domain.
    def filterHSVspeficColors(self,hsv_image, lowerHSV: list, higherHSV: list, lowerHSV2= None, higherHSV2=None):

        hsv_color1 = np.asarray(lowerHSV)   
        hsv_color2 = np.asarray(higherHSV)   
        

        mask = cv.inRange(hsv_image, hsv_color1, hsv_color2)

        if (lowerHSV2 and higherHSV2) != None:
            hsv_color3 = np.asarray(lowerHSV2)   # white red/pink
            hsv_color4 = np.asarray(higherHSV2)    # darker red
            mask2 = cv.inRange(hsv_image, hsv_color3, hsv_color4)
            mask = cv.bitwise_or(mask,mask2)
            

        return mask
   
    def find_edge_points(self,contours, count):
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

        if count >0:
            extTop = extTop-3
            extLeft = extLeft-3
            extBot = extBot+3
            extRight = extRight+3

        return extLeft, extRight, extTop, extBot

    # This function returns a img only with the colors
    # from the filterHSVspeficColors function.
    # obs: Mask returned in filterHSVspeficColors, is a grayscale img.
    # i.e this function converts to colorspaces.
    def build_coi(self, mask_img, orig_img):

        imask = mask_img>0
        coi = np.zeros_like(orig_img, np.uint8)
        coi[imask] = orig_img[imask]
        rgb_coi = cv.cvtColor(coi, cv.COLOR_BGR2RGB)
        return rgb_coi, coi

    def show_images(self, rgb_crop_img, rgb_original_img, count, maxtemp, crop=False):
       
        fig, _ = plt.subplots(nrows=1, ncols=2)
        fig.canvas.manager.set_window_title('{}V. The Max Temperature is: {}'.format(self.voltage_list[count], maxtemp))
        fig.tight_layout()
        plt.subplot(1,2,1)
        if count > 0:
            plt.title('Colors of Interest')
        else:
            plt.title('Croped original image')
        plt.imshow(rgb_crop_img)
        if crop ==True:
            rgb_img_cropped = rgb_original_img[70:170,:]
        else:
            rgb_img_cropped = rgb_original_img
        plt.subplot(1,2,2)
        plt.title('Original Image')
        plt.imshow(rgb_img_cropped)
        pass
    
    # This function gets the countours using 
    # canny edge detector.
    def getContours(self,mask):

        canny = imutils.auto_canny(mask)
        contours, _ = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = np.array(contours)
        return contours

    # Get croped COI(colors of interest image) that contains black pixels
    # and ignore then. Being left with only colors pixels.
    def ignoreBlackPixels(self, croped_rgbCoiImg):
        # Using set because we only want unique values
        # And we are studying only max and min temperatures
        # So set have the best performance to do this.
        ignore_black = set()
        rows = croped_rgbCoiImg.shape[0]
        columns = croped_rgbCoiImg.shape[1]

        # Appending on ignoreblack set
        # only pixels != [0,0,0] <---  black color
        for row in range(rows):
            for col in range(columns):
                if list(croped_rgbCoiImg[row][col]) != [0, 0, 0]:
                    ignore_black.add(tuple(croped_rgbCoiImg[row][col]))
        # Convert back to list, since sets
        # are unindexable
        ignore_black = list(ignore_black)                    
        
        return (ignore_black)

    # Calculate the temperatura through
    # the similarity of two pixels (colors)
    def calcTemp(self, ignoredBlack, crop_colorbar, map=None):
        
        self.ignoredBlack = ignoredBlack
        self.crop_colorbar = crop_colorbar
        temperature = []
        # This for runs over all elements in ignoredBlack list
        # i.e compare each pixel from then with the colorbar pixels.
        # but if the user gives the map, the function just use the map
        # instead comparing again every single pixel improoving the performance. 
        for self.element in range(len(ignoredBlack)):
            memo = None
           
            init = time.time()
            # Get the RGB color from the img, and convert to string
            # The reason to convert to string is because the map
            # return it map.key() in string.
            imPixel = str(self.ignoredBlack[self.element])
            # Check if the users gives the map and check if
            # this rgb value is on the map, if is not in there, 
            # run over colorbar pixels to compare each other.
            # If map is not given just compare every img pixel
            # with the colorbar pixels.
            if map is not None:
                if imPixel in map:
                    id = map[imPixel]
                else:
                    id, memo = self.__compareTwoColors_similarity()

            # Calculate the similarity of two collors(pixels)
            # one from the image, another from the colorbar    
            else:
                id, memo = self.__compareTwoColors_similarity()
            
            end = time.time()
            #print(end-init)
            '''
            To construct this formula, the maximum value of the scale was subtracted 
            from the smallest value and the result divided by the number of columns. 
            This resulting value shows how many degrees varies from one column to 
            another so to get the maximum of the scale multiply by the 
            total columns and sum the base value of the scale.
            '''
            formula_temp = self.base_scale+((self.maximum_scale-self.base_scale)/self.crop_colorbar_columns)*id
            
            temperature.append(round(formula_temp,3))
        
        # The return memo is usefull only if you
        # need to build a map with colors 
        # using createCSV_withColorsAndIds function
        return temperature, memo
    
    # This functions run over all elements of the colorbar
    # comparing the with the img pixels.
    def __compareTwoColors_similarity(self):
        similarityList = []
        
        # Converting the RGB values from ignoredBlack to tuple
        # to check if this value is in self.memo
        imgPixel_tuple = tuple(self.ignoredBlack[self.element])
        # self.memo is a responsible variable for memorizing
        # unique colors with your respective id. So its function 
        # is to improve performance
        if imgPixel_tuple not in self.memo:
            # Comparing all pixels from img with pixels in colorbar
            # to see wich color is the nearest to it. 
            # And also storing the RGB with the respective id
            # in self.memo
            for index in range (self.crop_colorbar_columns):
                # Getting the pixel from the img.
                pixImg = np.asarray(self.ignoredBlack[self.element])
                # Converting to sRGB -- values from 0 to 1 instead 0 to 255 like commom RGB
                colorSRGB_img = sRGBColor(pixImg[0]/255, pixImg[1]/255, pixImg[2]/255)
                # Getting the pixel from the colorbar.
                pixColorBar = self.crop_colorbar[0][index]
                # Converting to sRGB
                colorSRGB_colorbar = sRGBColor(pixColorBar[0]/255, pixColorBar[1]/255, pixColorBar[2]/255)
                
                # The convertion from sRGB to Lab is made below
                # because the delta_e_cie2000 only accept Lab colors.

                # color1 refers to image
                color1_lab = convert_color(colorSRGB_img, LabColor)
                # colors2 refers to colorbar
                color2_lab = convert_color(colorSRGB_colorbar, LabColor)
                # The convertion from sRGB to Lab is made 
                # because the delta_e_cie2000 only accept Lab colors.

                # Delta return a value. The lowest value means
                # that color is the similarest
                delta_e = delta_e_cie2000(color1_lab, color2_lab)

                '''
                 Here is another way to compare the similarity
                 of two colors using Euclidean Distance.
                 distance = (pixImg[0]-pixColorBar[0])**2+(pixImg[1]-pixColorBar[1])**2+(pixImg[2]-pixColorBar[2])**2
                 distance = np.sqrt(distance)
                '''

                # Append all values from delta result and store 
                # in similarityList
                similarityList.append(delta_e)

            # Get the lowest value from the similarity list
            # the lowest value shows the most similar color
            id = similarityList.index(min(similarityList))
            
            # Saving this RGB value from the img 
            # with it respective id
            self.memo[imgPixel_tuple]=id
            return id, self.memo
        else:
            id = self.memo[imgPixel_tuple]
            return id, self.memo
            
        
    def printLikeaTable(self, list_area_percent_roi, list_o2r_pixels, list_area_percent_total, voltage_list):
        
        pixel_roi_df = pd.DataFrame(list(zip(list_area_percent_roi,list_o2r_pixels)), columns =['%','N° of pixels'])
        print(pixel_roi_df)
        pixel_total_df = pd.DataFrame(list(zip(list_area_percent_total,voltage_list)), columns =['%','Voltage'])
        print(pixel_total_df)

