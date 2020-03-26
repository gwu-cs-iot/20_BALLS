from __future__ import annotations
from typing import Optional

from enum import Enum, auto

from dataclasses import dataclass

from balls import Coords, Ball

import twentyxx

import imutils
import time
import cv2
import math

NUM_BALLS = 3
JUMP_Y_LIMIT = 75
JUMP_X_LIMIT = 50
FUZZY_FACTOR = 1.5

class BallState(Enum):
    JUMPSQUAT = auto()
    AIRBORNE = auto()
    CAUGHT = auto()
    UNDECLARED = auto()

class Circle:
    coords: Coords
    radius: float

    def __init__(self, coords, radius):
        self.coords = coords
        self.radius = radius

    def intersects(self, c2: Circle, fuzzy_factor=1.0) -> bool:
        return math.sqrt((self.coords.x - c2.coords.x) ** 2 + (self.coords.y - c2.coords.y) ** 2) \
               <= (self.radius + c2.radius) * fuzzy_factor

@dataclass
class BallCircle:
    ball: Ball
    circle: Optional[Circle]
    state: BallState
    found: bool
    jumpPoint: Optional[Coords] = None

    def __init__(self, ball: Ball):
        self.ball = ball
        self.state = BallState.UNDECLARED
        self.found = False
        self.circle = Circle(Coords(), 0)

balls = []

for i in range(NUM_BALLS):
    balls.append(BallCircle(Ball(chr(ord('A') + i))))

def trace(picname, startingFrame=0):
    blueLower = (90,20,2)
    blueUpper = (135,255,255)

    frameIndex = 1
    catch_index = 0

    vs = cv2.VideoCapture(picname)
    time.sleep(1.0)

    while True:
        frame = vs.read()
        frame = frame[1]
        if frame is None:
            break
        frame = imutils.resize(frame, width=700)
        frame = imutils.rotate_bound(frame, 90)
        blur = cv2.GaussianBlur(frame, (11, 11), 0)
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
                center = Coords(cX, cY)

                cnt = cnt.astype("int")
                ((x, y), radius) = cv2.minEnclosingCircle(cnt)

                # TODO remove upper bound?
                if 10 < radius < 50:
                    foundBall = False
                    blob = Circle(Coords(x, y), radius)
                    # Find a circle from the last frame intersecting with this one.
                    for prevBall in balls:
                        if prevBall.state is BallState.UNDECLARED:
                            continue
                        if blob.intersects(prevBall.circle, FUZZY_FACTOR):
                            # We have found the ball corresponding to this circle.
                            
                            # Updates the Ball circle to be the blob found to intersect
                            prevBall.circle = blob
                            foundBall = True
                            prevBall.found = True
                            if prevBall.state == BallState.JUMPSQUAT:
                                if (prevBall.jumpPoint.y -blob.coords.y  > JUMP_Y_LIMIT) or (abs(blob.coords.x - prevBall.jumpPoint.x > JUMP_X_LIMIT)):
                                    prevBall.state = BallState.AIRBORNE
                                    prevBall.jumpPoint = None
                                    # NOTE Maybe move this
                            if prevBall.state is BallState.CAUGHT:
                                prevBall.state = BallState.JUMPSQUAT
                                prevBall.jumpPoint = blob.coords
                            break

                    if not foundBall:
                        # TODO set state to jumpsquat, unknown ball
                        closestBall = None
                        closestDist = -1
                        for prevBall in balls:
                            if prevBall.state is BallState.UNDECLARED:
                                closestBall = prevBall
                                
                                break
                            if prevBall.state is not BallState.AIRBORNE:
                                ball_x = prevBall.circle.coords.x
                                blob_x = blob.coords.x
                                dist = abs(ball_x - blob_x)
                                if dist < closestDist or closestDist < 0:
                                    closestDist = dist
                                    closestBall = prevBall
                        closestBall.circle = blob
                        if closestBall.state is not BallState.AIRBORNE:
                            closestBall.state = BallState.JUMPSQUAT
                        closestBall.jumpPoint = closestBall.circle.coords

            for b in balls:
                if not b.found and b.state is BallState.AIRBORNE:
                    b.state = BallState.CAUGHT
                    catch_index += 1
                b.found = False
                overlay = frame.copy()
                if b.state is not BallState.CAUGHT:
                    if b.state is BallState.AIRBORNE:
                        cv2.circle(overlay, b.circle.coords.to_tuple(), int(b.circle.radius), (0, 255, 0), -1)
                    if b.state is BallState.JUMPSQUAT: 
                        cv2.circle(overlay, b.circle.coords.to_tuple(), int(b.circle.radius), (0, 0, 255), -1)
                    frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
                    cv2.putText(frame, b.ball.name, (int(b.circle.coords.x), int(b.circle.coords.y)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), thickness=2)

        twentyxx.drawHud(frame, balls)

        # TODO Magic numbers
        cv2.putText(frame, str(frameIndex), (0, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        cv2.putText(frame, str("Catch Count:"), (100, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        cv2.putText(frame, str(catch_index), (325, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))

        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)
        if startingFrame <= 0 or 0 < startingFrame <= frameIndex:
            # If startingFrame is defined, skip to that frame.
            key = cv2.waitKey(-1)
            if key == ord("q"):
                break

        frameIndex += 1

    c_per_frame = 60*catch_index/frameIndex
    print("Catches per second is about:" + str(c_per_frame))
    cv2.destroyAllWindows()
