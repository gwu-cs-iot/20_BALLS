from imutils.video import VideoStream
from collections import deque
import numpy as np
import imutils
import time
import cv2


def trace(picname):
    blueLower = (90,1,20)
    blueUpper = (135,255,255)

    greenLower = (40,55,20)
    greenUpper = (95,255,255)

    pts = deque(maxlen=20)

    vs = cv2.VideoCapture(picname)
    time.sleep(1.0)

    while True:
        frame = vs.read()
        frame = frame[1]
        if frame is None:
            break
        frame = imutils.resize(frame, width=700)
        frame = imutils.rotate_bound(frame,90)
        blur = cv2.GaussianBlur(frame, (11,11), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, blueLower, blueUpper)
        mask = cv2.erode(mask,None,iterations=2)
        mask = cv2.dilate(mask,None,iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        if len(cnts)>1:
            for cnt in cnts:
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                center=(cX,cY)

                cnt = cnt.astype("int")
                #cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
                ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                if radius > 10:
                    cv2.circle(frame,center,int(radius),(0,0,255),2)
                pts.appendleft(center)

        cv2.imshow("Frame",frame)
        #cv2.imshow("Mask",mask)
        key = cv2.waitKey(32) & 0xFF
        if key == ord("q"):
            break
    cv2.destroyAllWindows()






