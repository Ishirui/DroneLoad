# https://pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/

server_ip = "192.168.137.1" #TO EDIT

# import the necessary packages
import pyrealsense2 as rs
import imagezmq
import numpy as np
import socket
# construct the argument parser and parse the arguments

# initialize the ImageSender object with the socket address of the
# server
sender = imagezmq.ImageSender(connect_to=f"tcp://{server_ip}:5555")
hostname = socket.gethostname()


#Setup realsense video import
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)


 
while True:
    # read the frame from the camera and send it to the server
    frames = pipeline.wait_for_frames()
    rgb = frames.get_color_frame()
    frameMatrix = np.asanyarray(rgb.get_data(), dtype=np.uint8)
    sender.send_image(hostname, frameMatrix)