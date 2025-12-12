#!/usr/bin/env python3

import cv2
import subprocess
import time

timenow = time.time()

done = False

#v4l2-ctl -d /dev/video0 --set-ctrl=black_level=1

GAIN = 3016    
EXPOSURE = 50000
BLACK_LEVEL = 1000
# SHARPNESS = 150     # (100=normal)

def setup_camera():
    print("Editing camera...")
    
    # edit color
    # subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=saturation=" + str(SATURATION), shell=True)
    # subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=contrast=" + str(CONTRAST), shell=True)
    # subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=brightness=" + str(BRIGHTNESS), shell=True)
    # subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=sharpness=" + str(SHARPNESS), shell=True)

    subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=gain=" + str(GAIN), shell=True)
    subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=exposure=" + str(EXPOSURE), shell=True)
    subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=black_level=" + str(BLACK_LEVEL), shell=True)
    
    print("Edited done!")
    time.sleep(1)

"""

 return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
"""


def get_camera_pipeline():
    return (
        "nvarguscamerasrc sensor-id=0 aelock=1 ! "
        "video/x-raw(memory:NVMM), width=5440, height=3648, framerate=20/1 ! "
        "nvvidconv ! video/x-raw, width=1920, height=1080, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink"
    )

def main():
    print("Begining camera VC IMX183...")
    
    # Setup camera first
    setup_camera()
    
    # Open camera
    cap = cv2.VideoCapture(get_camera_pipeline(), cv2.CAP_GSTREAMER)

    subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=exposure=" + str(EXPOSURE), shell=True)
    # time.sleep(5)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    print("Camera is running...!")
    print("Press 'q' to exit and 's' to capture image")
    
    while True:
        current_time = time.time()
        # if (3 <= current_time - timenow <= 5):
        #     subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=exposure=" + str(1000), shell=True)
        # if (not done and current_time - timenow >= 6):
        #     subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=exposure=" + str(50000), shell=True)
        #     done = True


        ret, frame = cap.read()
        if not ret:
            break
            

        cv2.imshow("VC IMX183 Camera", frame)
        

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = "test_image.jpg"
            cv2.imwrite(filename, frame)
            print("Capture done: " + filename)
    
    cap.release()
    cv2.destroyAllWindows()
    print("Close camera!")

if __name__ == "__main__":
    main()
