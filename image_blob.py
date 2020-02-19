import numpy as np
import cv2
import imutils

# The range of HSV values we will consider blue, to detect the blue juggling balls
blueLower = (95,90,20)
blueUpper = (120,255,255)

greenLower = (40,55,20)
greenUpper = (95,255,255)

# Load the image, convert it to hsv values from BGR and produce a mask using the upper and lower limits of blue
img = cv2.imread('juggle2.jpg')
img = cv2.GaussianBlur(img, (11,11),0)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv,greenLower,greenUpper)

# Show the image of the mask created
cv2.imshow("blue",mask)
cv2.waitKey()
cv2.destroyAllWindows()

# Filter Mask more and show image again
mask = cv2.erode(mask, None, iterations=2)
mask = cv2.dilate(mask,None, iterations=2)

cv2.imshow("blue",mask)
cv2.waitKey()
cv2.destroyAllWindows()

# Using the mask, determine the contours of each of the BALLS
cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
center = None

if len(cnts)>1:
    for cnt in cnts:
        M = cv2.moments(cnt)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cnt = cnt.astype("int")
        cv2.drawContours(img, [cnt], -1, (0,0,255),2)

cv2.imshow("contours",img)
cv2.waitKey()
cv2.destroyAllWindows()
