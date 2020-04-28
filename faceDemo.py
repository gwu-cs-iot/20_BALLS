import cv2
import time
import imutils

import face

vs = cv2.VideoCapture('test_vids/quarantine_1.mp4')
time.sleep(1.0)
while True:
    frame = vs.read()
    frame = frame[1]
    #cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
    frame = imutils.resize(frame, width = 700)
    frame = imutils.rotate_bound(frame, 90)
    if frame is None: 
        break
    faceImage = face.face(frame)

    cv2.imshow('Frame', faceImage)
    key = cv2.waitKey(-1)
    if key == ord("q"):
        break
