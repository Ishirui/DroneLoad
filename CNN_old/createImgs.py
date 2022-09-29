import cv2
import pyrealsense2 as rs
import numpy as np

yellow = [np.array([20, 80, 80]), np.array([30, 255, 255])]
i = 0


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

    yellows = isolate_color_squares(frameMatrix, yellow)
    
    yellowExtracts = [extract_from_image(rect, frameMatrix) for rect in yellows]
    yellowExtracts = [x if x.size != 0 else None for x in yellowExtracts]

    cv2.namedWindow("View")
    cv2.namedWindow("Extracted")


    cv2.imshow("View", frameMatrix)
    if len(yellowExtracts) > 0:
        try:
            cv2.imshow("Extracted", yellowExtracts[0])
        except cv2.error:
            pass

    for x in yellowExtracts:
        
        if rgb.get_frame_number()%10 == 0:
            try:
                cv2.imwrite("C:\\Users\\pierr\\Desktop\\Extra_data\\"+str(i)+".png", x)
                i += 1
                print(i)
            except:
                pass
    cv2.waitKey(1)