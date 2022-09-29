import pyrealsense2 as rs
import cv2
import numpy as np
from tensorflow import keras


## Color Definitions
# HSV (Hue Saturation Value) Format
blue = [np.array([90, 50, 70]), np.array([128, 255, 255])]
green = [np.array([36, 25, 25]), np.array([70, 255, 255])]
yellow = [np.array([20, 80, 80]), np.array([30, 255, 255])]
white = [np.array([0, 0, 200]), np.array([255, 20, 255])]
red1 = [np.array([0, 150, 50]), np.array([10, 255, 255])]
red2 = [np.array([170, 150, 50]), np.array([180, 255, 255])]

model = keras.models.load_model("CNN détection d'objets\\model")
ratio = 0.7 #How many times bigger the prob of object must be bigger than the prob of NObj

def infer(matrix):
    if matrix is None:
        return None
    
    converted = np.expand_dims(cv2.cvtColor(cv2.resize(matrix, (256,256), interpolation=cv2.INTER_NEAREST),cv2.COLOR_BGR2GRAY),axis=0)
    
    res = model.predict(converted, verbose = 0)[0]
    print(res)
    return res[0] > ratio*res[1] and res[0] > 0.5
    
def extract_from_image(rect, img):
    xmin,ymin = rect[0]
    xmax,ymax = rect[-1]
    

    #The arrays are, for some reason, y/x not x/y
    return img[ymin:ymax,xmin:xmax]

def isolate_color_squares(img, color):
    
    # Define kernel size for noise removal
    kernel = np.ones((7,7),np.uint8)

    # Convert to hsv colorspace
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Lower bound and upper bound for color 
    lower_bound = color[0]    
    upper_bound = color[1]

    # Find the colors within the boundaries
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Remove unnecessary noise from mask

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Segment only the detected region
    # Segmented_img = cv2.bitwise_and(img, img, mask=mask)

    # Find contours from the mask

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output = []
    for cntr in contours:
        x,y,w,h = cv2.boundingRect(cntr)
        
        if w < 50 or h < 50:
            continue #Remove boxes smaller than 50 pixels wide


        xc,yc = x+w//2, y+h//2
        halfDim = max(w,h)//2

        p1 = xc-halfDim,yc-halfDim
        p2 = xc+halfDim,yc-halfDim
        p3 = xc-halfDim,yc+halfDim
        p4 = xc+halfDim,yc+halfDim
        output.append( (p1,p2,p3,p4) )
    
    return output

# Create a context object. This object owns the handles to all connected realsense devices
pipeline = rs.pipeline()

# Configure streams
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

# Start streaming
pipeline.start(config)

while True:
    # This call waits until a new coherent set of frames is available on a device
    # Calls to get_frame_data(...) and get_frame_timestamp(...) on a device will return stable values until wait_for_frames(...) is called
    frames = pipeline.wait_for_frames()
    rgb = frames.get_color_frame()
    frameMatrix = np.asanyarray(rgb.get_data(), dtype=np.uint8)

    #blues = isolate_color_squares(frameMatrix, blue)
    yellows = isolate_color_squares(frameMatrix, yellow)
    
    #blueExtracts = [extract_from_image(rect, frameMatrix) for rect in blues]
    #yellowExtracts = [x if x.size != 0 else None for x in blueExtracts ]
    yellowExtracts = [extract_from_image(rect, frameMatrix) for rect in yellows]
    yellowExtracts = [x if x.size != 0 else None for x in yellowExtracts]

    #blueInfers = [infer(x) for x in blueExtracts]
    yellowInfers = [infer(x) for x in yellowExtracts]

    #toDisplayBlue = [x for i,x in enumerate(blues) if blueInfers[i]]
    toDisplayYellow = [x for i,x in enumerate(yellows) if yellowInfers[i]]

    #for rect in toDisplayBlue:
        #cv2.rectangle(frameMatrix, rect[0], rect[-1], (255,0,0), 2)

    for rect in toDisplayYellow:
        cv2.rectangle(frameMatrix, rect[0], rect[-1], (0,255,255), 2)

    cv2.namedWindow("RS")
    cv2.imshow("RS", frameMatrix)
    cv2.waitKey(1)