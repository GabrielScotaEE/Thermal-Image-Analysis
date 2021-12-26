import numpy as np
import cv2 as cv
import imutils
import matplotlib.pyplot as plt

from colormath.color_objects import sRGBColor, LabColor, BaseRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# img = cv.imread('./images/IR_0666.jpg')
# img = img[70:71,164:165]
# img_lab = cv.cvtColor(img,cv.COLOR_BGR2LAB)
# print(img_lab)
# # Red Color


# color1_rgb = sRGBColor(1.0, 0.0, 0.0)

# # Blue Color
# color2_rgb = sRGBColor(0.99, 0.0, 0.0)

# # Convert from RGB to Lab Color Space
# color1_lab = convert_color(color1_rgb, LabColor)
# print(color1_lab)
# # Convert from RGB to Lab Color Space
# color2_lab = convert_color(color2_rgb, LabColor)

# # Find the color difference
# delta_e = delta_e_cie2000(color1_lab, color2_lab)

# print ("The difference between the 2 color = {} " .format(delta_e))

# red = np.asarray([255,0,0])
# torange = np.asarray([180,20,0])
# org = np.asarray([180,65,0])
# xx = np.asarray([246, 1, 226])

# distance = (red[0]-xx[0])**2+(red[1]-xx[1])**2+(red[2]-xx[2])**2
# distance = np.sqrt(distance)
# print ("The difference between the 2 color = {} " .format(distance))
import csv

with open('mapColors.csv', encoding="utf8") as f:
    csv_reader = csv.DictReader(f)
    # skip the header
    next(csv_reader)
    # creating map with all colors
    map = {}
    # show the data
    for line in csv_reader:
        color = (line['color'])
        color = (color.replace("'", ""))
        print(color)
        id = line['id']
        id = int(id.replace("'", ""))
        
        map[color] = id
        
        # print(f"The RGB color:{line['color']} has {line['id']} id".join(line))
x = (255,255,255)
print(type(x))
print(str(x))    


# with open('mapColors.csv', encoding="utf8") as f:
#     csv_reader = csv.reader(f, delimiter = ';', skipinitialspace=True)

#     # skip the first row
#     next(csv_reader)
#     map = {}
#     # show the data
#     for line in csv_reader:
#         print (f"The RGB color:{line['color']} has {line['id']} id".join(line))







# memo = {}
# data = []
# infos = []
# memo[(199,200,11)] = 48
# memo[(158,198,24)] = 44
# memo[(144,195,38)] = 40

# for key, value in memo.items():
#     infos = []
#     infos.append(key)
#     infos.append(value)
#     data.append(infos)
#     # print(key, value)
# print(len(data))