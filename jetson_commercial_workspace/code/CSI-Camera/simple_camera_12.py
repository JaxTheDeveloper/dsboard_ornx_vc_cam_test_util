# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2



def gstreamer_pipeline(
    sensor_id=0,
    capture_width=3840,
    capture_height=2160,
    display_width=1280,
    display_height=720,
    framerate=15,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d "
        ""
        "exposurecompensation=0.5 "
        "contrast=1.8 "
        "brightness=0.12 "
        "sharpness=1.9 "
        "ee-mode=3 "
        "ee-strength=0.8 "
        "saturation=1.2 "
        "tnr-mode=0 ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=BGR ! appsink"
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
    window_title = "VC-IMX183C - Lightroom Tuned"

    print("Starting camera with Lightroom tuned settings...")
    print("Pipeline: " + gstreamer_pipeline(flip_method=0))
    
    video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    if video_capture.isOpened():
        try:
            window_handle = cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            while True:
                ret_val, frame = video_capture.read()
                if not ret_val:
                    break
                    
                # Check to see if the user closed the window
                # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(window_title, frame)
                else:
                    break 
                
                keyCode = cv2.waitKey(10) & 0xFF
                # Stop the program on the ESC key or 'q'
                if keyCode == 27 or keyCode == ord('q'):
                    break
                    
                # Save image when 's' is pressed
                if keyCode == ord('s'):
                    filename = "vc_imx183_tuned.png"
                    cv2.imwrite(filename, frame)
                    print("Saved: " + filename)
                # Print FPS when 'f' is pressed
                if keyCode == ord('f'):
                    print("Press 'f' again for FPS")
                    
        finally:
            video_capture.release()
            cv2.destroyAllWindows()
    else:
        print("Error: Unable to open camera")


if __name__ == "__main__":
    show_camera()
