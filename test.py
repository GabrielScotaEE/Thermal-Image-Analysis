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

d = set()

d.add((255,255,255))
d.add((255,255,255))
d.add((255,165,7))
print(d)
d = list(d)
for i in d:
    print(i)

