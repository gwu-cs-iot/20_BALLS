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
    squatFrames: int

    def __init__(self, ball: Ball):
        self.ball = ball
        self.state = BallState.UNDECLARED
        self.found = False
        self.squatFrames = 5
        self.circle = Circle(Coords(), 0)


balls = []

for i in range(NUM_BALLS):
    balls.append(BallCircle(Ball(chr(ord('A') + i))))

def trace(picname):
    blueLower = (90,1,20)
    blueUpper = (135,255,255)

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
                        if blob.intersects(prevBall.circle, fuzzy_factor=1.5):
                            # We have found the ball corresponding to this circle.
                            
                            # Updates the Ball circle to be the blob found to intersect
                            prevBall.circle = blob
                            foundBall = True
                            prevBall.found = True
                            if prevBall.state == BallState.JUMPSQUAT:
                                prevBall.squatFrames = prevBall.squatFrames - 1
                                if prevBall.squatFrames == 0:
                                    prevBall.state = BallState.AIRBORNE

                                    # NOTE Maybe move this
                                    prevBall.squatFrames = 5
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
                        closestBall.state = BallState.JUMPSQUAT

            for b in balls:
                if not b.found and b.state is not BallState.JUMPSQUAT:
                    b.state = BallState.CAUGHT
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

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(-1)
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
