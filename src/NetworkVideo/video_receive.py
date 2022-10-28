# import the necessary packages
import numpy as np
import imagezmq
import cv2



imageHub = imagezmq.ImageHub()
#cv2.namedWindow("RS over TCP")

# start looping over all the frames
i = 0
while True:
    # receive RPi name and frame from the RPi and acknowledge
    # the receipt
    (rpiName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    print(f"Received frame n°{i}!")
    frame = cv2.imdecode(frame, 1)
    
    cv2.namedWindow("RS")
    cv2.imshow("RS", frame)
    cv2.waitKey(1)
    i += 1


"""
Without compression:

Network: ~220 MBps
Jetson CPU: 62% (!)

With compression:

Network: 14.4 Mbps
Jetson CPU: 77%
"""