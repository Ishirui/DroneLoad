# import the necessary packages
import numpy as np
import imagezmq
import cv2



imageHub = imagezmq.ImageHub()
#cv2.namedWindow("RS over TCP")

# start looping over all the frames
while True:
    # receive RPi name and frame from the RPi and acknowledge
    # the receipt
    (rpiName, frame) = imageHub.recv_image()
    imageHub.send_reply(b'OK')
    print("Received frame !")
    cv2.namedWindow("RS")
    cv2.imshow("RS", frame)
    cv2.waitKey(1)