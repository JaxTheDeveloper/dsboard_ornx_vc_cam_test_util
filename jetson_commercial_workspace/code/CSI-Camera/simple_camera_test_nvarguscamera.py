# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2
import numpy as np

""" 
gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
Flip the image by setting the flip_method (most common values: 0 and 2)
display_width and display_height determine the size of each camera pane in the window on the screen
Default 1920x1080 displayd in a 1/4 size window
"""

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=12,
    flip_method=2,
):
    return (
        "nvarguscamerasrc sensor-id=%d  ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1, saturation=20, exposurerange=\"13000,683709000\" ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)NV12 ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGRA ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
    
def gstreamer_pipeline_old(
    sensor_id=0,
    capture_width=5440,
    capture_height=3648,
    display_width=1920,
    display_height=1080,
    framerate=12,
    flip_method=2,
):
    return (
        "nvarguscamerasrc sensor-id=%d wbmode=0 saturation=1.8 constrast=1.5 brightness=0 sharpness=1.2 hue=-0.5 ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=NV12 ! "
        "videoconvert ! "
        "video/x-raw, format=BGRA ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def show_camera():
    window_title = "CSI Camera"
    
    b_gain = 1
    g_gain = 1
    r_gain = 1

    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline())
    video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    if video_capture.isOpened():
        try:
            window_handle = cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            while True:
                ret_val, frame = video_capture.read()
                # Check to see if the user closed the window
                # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    frame[:, :, 0] = frame[:, :, 0] * b_gain
                    frame[:, :, 1] = frame[:, :, 1] * g_gain
                    frame[:, :, 2] = frame[:, :, 2] * r_gain
                    
                    # frame = np.clip(frame, 0, 255)
                    cv2.imshow(window_title, frame)
                else:
                    break 
                keyCode = cv2.waitKey(10) & 0xFF
                # Stop the program on the ESC key or 'q'
                if keyCode == 27 or keyCode == ord('q'):
                    break
                if keyCode == ord('s'):
                    filename = "image.png"
                    cv2.imwrite(filename, frame)
                    print("saved photo")
        finally:
            video_capture.release()
            cv2.destroyAllWindows()
    else:
        print("Error: Unable to open camera")


if __name__ == "__main__":
    show_camera()
