from __future__ import annotations

import time

import cv2
import imutils
import math
import numpy as np

import twentyxx
from balls import Coords, Circle, Ball
from arc import Arc, Arc_array 

NUM_BALLS = 3
JUMP_Y_LIMIT = 75
JUMP_X_LIMIT = 50
FUZZY_FACTOR = 1.5
#alpha factor for running avg. higher = old values mean more
ALPHA_FACTOR = .4
DRAW_ARCS = False
balls = []
CUTOFF_THROW = 400
REAL_TIME = False
SHOW_MASK = False

Color_Names = { 'A': (255,50,50), 'B': (40,255,100), 'C': (100,100,255) }

for i in range(NUM_BALLS):
    balls.append(Ball(chr(ord('A') + i)))


def trace(picname, startingFrame=0, drawHud=False):
    blueLower = (90, 20, 2)
    blueUpper = (135, 255, 255)

    frameIndex = 1
    catch_index = 0

    vs = cv2.VideoCapture(0 if picname is None else picname)
    time.sleep(1.0)
    A_arc = None
    B_arc = None
    C_arc = None
    Arc_arr = Arc_array("Arc")

    while True:
        frame = vs.read()
        frame = frame[1]
        if frame is None:
            break
        frame = imutils.resize(frame, width=700)
        if picname is not None:
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
                if 5 < radius < 50:
                    foundBall = False
                    blob = Circle(Coords(x, y), radius)
                    # Find a circle from the last frame intersecting with this one.
                    for prevBall in balls:
                        if prevBall.state is Ball.State.UNDECLARED:
                            continue

                        if blob.intersects(prevBall.circle, FUZZY_FACTOR):
                            # We have found the ball corresponding to this circle.

                            # Updates the Ball circle to be the blob found to intersect

                            #Calculates x and y velocity of the intersecting ball
                            x_velocity = blob.coords.x - prevBall.circle.coords.x
                            y_velocity = blob.coords.y - prevBall.circle.coords.y
                            prevBall.movement.average(x_velocity, y_velocity, ALPHA_FACTOR)

                            # Uses calculated velocity to determine throwstate
                            if prevBall.state == Ball.State.AIRBORNE and prevBall.throwstate == Ball.ThrowState.UNRECOGNIZED:
                                if x_velocity > 0:
                                    prevBall.throwstate = Ball.ThrowState.LEFTRISING
                                else:
                                    prevBall.throwstate = Ball.ThrowState.RIGHTRISING
                            if blob.coords.y < CUTOFF_THROW:
                                prevBall.peak = prevBall.movement.is_peak()
                                prevBall.circle = blob
                                if prevBall.peak is True:
                                    prevBall.peaked()
                            elif prevBall.movement.is_peak() and prevBall.is_falling(): 
                               prevBall.state = Ball.State.CAUGHT 
                               prevBall.throwstate = prevBall.ThrowState.UNRECOGNIZED
                               foundBall = True
                               prevBall.found = True
                               break


                            # Log the coords of the ball into the arc trace
                            if prevBall.name == "A" and A_arc is not None:
                                A_arc.add(blob.coords.x,blob.coords.y)
                            if prevBall.name == "B" and B_arc is not None:
                                B_arc.add(blob.coords.x,blob.coords.y)
                            if prevBall.name == "C" and C_arc is not None:
                                C_arc.add(blob.coords.x,blob.coords.y)
                        
                            # Set the ball as found
                            foundBall = True
                            prevBall.found = True
                            
                            # Add the coords to the trail deque
                            prevBall.trail_x.append(blob.coords.x)
                            prevBall.trail_y.append(blob.coords.y)

                            # Recognized Ball is in JUMPSQUAT:
                            if prevBall.state is Ball.State.JUMPSQUAT:
                                if prevBall.jumpPoint.y - blob.coords.y > JUMP_Y_LIMIT \
                                        or abs(blob.coords.x - prevBall.jumpPoint.x > JUMP_X_LIMIT):
                                    prevBall.state = Ball.State.AIRBORNE
                                    #TODO remove this/ make it better
                                    if prevBall.name == "A":
                                       A_arc = Arc("A") 
                                       A_arc.add(blob.coords.x, blob.coords.y)
                                    if prevBall.name == "B":
                                       B_arc = Arc("B") 
                                       B_arc.add(blob.coords.x, blob.coords.y)
                                    if prevBall.name == "C":
                                       C_arc = Arc("C") 
                                       C_arc.add(blob.coords.x, blob.coords.y)
                                    prevBall.jumpPoint = None
                                    # NOTE Maybe move this
                            elif prevBall.state is Ball.State.CAUGHT:
                                prevBall.state = Ball.State.JUMPSQUAT
                                prevBall.jumpPoint = blob.coords
                            break

                    if not foundBall:
                        # TODO set state to jumpsquat, unknown ball
                        closestBall = None
                        closestDist = -1

                        for prevBall in balls:
                            if prevBall.state is Ball.State.UNDECLARED:
                                closestBall = prevBall
                                break

                            if prevBall.found:
                                continue
                            #if prevBall.state is not Ball.State.AIRBORNE:
                            ball_x = prevBall.circle.coords.x
                            blob_x = blob.coords.x
                            ball_y = prevBall.circle.coords.y
                            blob_y = blob.coords.y
                            dist = math.sqrt((ball_x - blob_x)**2 + (ball_y - blob_y)**2)
                            if dist < closestDist or closestDist < 0:
                                closestDist = dist
                                closestBall = prevBall
                        if closestBall is  not None:
                            closestBall.circle = blob

                            if closestBall.state is not Ball.State.AIRBORNE:
                                closestBall.state = Ball.State.JUMPSQUAT

                            closestBall.jumpPoint = closestBall.circle.coords

            for b in balls:
                if not b.found and b.state is Ball.State.AIRBORNE:
                    b.state = Ball.State.CAUGHT
                    if b.is_falling():
                        catch_index += 1
                    b.throwstate = Ball.ThrowState.UNRECOGNIZED
                    #TODO deal with this gross section I made :-(
                    if b.name == "A" and A_arc is not None and DRAW_ARCS is True:
                        A_arc.plot()
                    if A_arc is not None and b.name == "A":
                        print("added ball")
                        Arc_arr.add_arc(A_arc)
                        A_arc = None
                    if b.name == "B" and B_arc is not None and DRAW_ARCS is True:
                        B_arc.plot()
                    if B_arc is not None and b.name == "B":
                        print("added ball")
                        Arc_arr.add_arc(B_arc)
                        B_arc = None
                    if b.name == "C" and C_arc is not None and DRAW_ARCS is True:
                        C_arc.plot()
                    if C_arc is not None and b.name == "C":
                        print("added ball")
                        Arc_arr.add_arc(C_arc)
                        C_arc = None
                    b.movement.caught()
                    b.trail_x.clear()
                    b.trail_y.clear()
                overlay = frame.copy()

                if b.state is not Ball.State.CAUGHT and b.state is not Ball.State.UNDECLARED:
                    # Draw ball overlays
                    if b.peak is True: 
                        cv2.circle(overlay, b.circle.coords.to_tuple(), int(b.circle.radius), (255, 255, 255), -1)
                    elif b.state is Ball.State.AIRBORNE:
                        cv2.circle(overlay, b.circle.coords.to_tuple(), int(b.circle.radius), (0, 255, 0), -1)
                    elif b.state is Ball.State.JUMPSQUAT and b.found:
                        cv2.circle(overlay, b.circle.coords.to_tuple(), int(b.circle.radius), (0, 0, 255), -1)

                    frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

                    # Draw ball trails
                    for i in range(1, len(b.trail_x)):
                        if b.trail_x[i - 1] is None or b.trail_x[i] is None:
                            continue
                        thickness = int(np.sqrt(10 / float(i + 1)) * 2.5)
                        cv2.line(frame, (int(b.trail_x[i-1]), int(b.trail_y[i-1])), (int(b.trail_x[i]), int(b.trail_y[i])), Color_Names[b.name], thickness)

                    if b.found:
                        cv2.putText(frame, b.name, b.circle.coords.to_tuple(), cv2.FONT_HERSHEY_SIMPLEX, 2, Color_Names[b.name],
                                    thickness=2)
                b.found = False

        if drawHud:
            twentyxx.drawHud(frame, balls)

        # TODO Magic numbers
        cv2.putText(frame, str(frameIndex), (0, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        cv2.putText(frame, str("Catch Count:"), (100, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
        cv2.putText(frame, str(catch_index), (325, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))

        cv2.imshow("Frame", frame)
        if SHOW_MASK:
            cv2.imshow("Mask", mask)

        if startingFrame <= 0 or 0 < startingFrame <= frameIndex:
            # If startingFrame is defined, skip to that frame.
            if REAL_TIME:
                key = cv2.waitKey(int((1/60)*1000))
            else:
                key = cv2.waitKey(-1)
            if key == ord("q"):
                break

        frameIndex += 1

    c_per_frame = 60 * catch_index / frameIndex
    Arc_arr.plot_arcs()
    print("Catches per second is about:" + str(c_per_frame))
    cv2.destroyAllWindows()
