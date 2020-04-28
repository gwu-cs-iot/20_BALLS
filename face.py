import cv2
import numpy as np

protoPath = 'models/deploy.prototxt.txt'
modelPath = 'models/res10_300x300_ssd_iter_140000.caffemodel'


def face(image):
    net = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    
    maxConfidence = 0
    # Loop over the detections
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.9:
            maxConfidence = confidence
            box = detections [0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        

    return image
