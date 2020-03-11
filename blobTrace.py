from __future__ import annotations

from balls import Coords, Ball

from imutils.video import VideoStream
from collections import deque
import numpy as np
import imutils
import time
import cv2
import math

class Circle:
    coords: Coords
    radius: float

    def __init__(self, coords, radius):
        self.coords = coords
        self.radius = radius

    def intersects(self, c2: Circle, fuzzy_factor=1.0) -> bool:
        return math.sqrt((self.coords.x - c2.coords.x) ** 2 + (self.coords.y - c2.coords.y) ** 2) \
               <= (self.radius + c2.radius) * fuzzy_factor

def trace(picname, fast=0):
    blueLower = (90,1,20)
    blueUpper = (135,255,255)

    greenLower = (40,55,20)
    greenUpper = (95,255,255)

    ballId = 'A'

    thisFrameCircles = []
    lastFrameCircles = []

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
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        if len(cnts) > 1:
            for cnt in cnts:
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                center = (cX, cY)

                cnt = cnt.astype("int")
                ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                if 10 < radius < 50:
                    foundCircle = False
                    circle = Circle(Coords(x, y), radius)
                    # Find a circle from the last frame intersecting with this one.
                    for c in lastFrameCircles:
                        if circle.intersects(c[0], fuzzy_factor=1.5):
                            # We have found the ball corresponding to this circle.
                            thisFrameCircles.append((circle, c[1]))
                            foundCircle = True
                            break

                    if not foundCircle:
                        thisFrameCircles.append((circle, Ball(ballId)))
                        ballId = chr(ord(ballId) + 1)

                    cv2.circle(frame, center, int(radius), (0, 0, 255), 2)
                    cv2.putText(frame, thisFrameCircles[-1][1].name, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), thickness=2)

        lastFrameCircles = thisFrameCircles
        thisFrameCircles = []

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(-1)
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
