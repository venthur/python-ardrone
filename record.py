
# !/usr/bin/env python

import cv2
import time
import libardrone
running = True
flying = False
path = 'tcp://192.168.1.1:5555'

drone = libardrone.ARDrone()
drone.speed = 0.5

W, H = 640, 360
stream = cv2.VideoCapture(path)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter("output.avi", fourcc, 20.0, (W, H))

time = time.time()
while stream.isOpened():
    ret, frame = stream.read()
    if ret:
        #frame = cv2.flip(frame, 0)
        out.write(frame)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

stream.release()
out.release()
cv2.destroyAllWindows()