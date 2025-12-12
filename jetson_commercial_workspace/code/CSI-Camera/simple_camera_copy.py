# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2
import numpy as np
import subprocess
import time

subprocess.run("v4l2-ctl -d /dev/video0 --set-ctrl=black_level=1", shell=True)

time.sleep(.05)

""" 
gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
Flip the image by setting the flip_method (most common values: 0 and 2)
display_width and display_height determine the size of each camera pane in the window on the screen
Default 1920x1080 displayd in a 1/4 size window
"""

# image adjustment
def adjust_image(image, contrast=1.0, brightness=0, exposure=0, shadows=0, highlights=0, whites=0, blacks=0):
    # scaling image for exposure
    image = np.clip(image * (2 ** exposure), 0, 255).astype(np.uint8)

    # constrast, brightness
    image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

    # # convert img to floar32
    # img_float = np.float32(image) / 255.0
    
    # # shadows
    # img_float = np.clip(img_float - shadows * 0.05, 0, 1)

    # # highlights
    # img_float = np.clip(img_float + highlights * 0.05, 0, 1)

    # # whites
    # img_float = np.clip(img_float + whites * 0.05, 0, 1)

    # # blacks
    # img_float = np.clip(img_float - blacks * 0.05, 0, 1)

    # # revert to uint8
    # adjusted_image = np.uint8(np.clip(img_float * 255, 0, 255))
    
    return image

# Function to adjust Temperature (makes the image warmer or cooler)
def adjust_temperature(image, temp):
    # Blue to Red adjustment (Increase Red and decrease Blue to warm the image)
    temp_image = image.copy()
    if temp > 0:
        temp_image[:, :, 2] = np.clip(temp_image[:, :, 2] + temp * 1.5, 0, 255)  # Increase Red
        temp_image[:, :, 0] = np.clip(temp_image[:, :, 0] - temp * 1.5, 0, 255)  # Decrease Blue
    elif temp < 0:
        temp_image[:, :, 2] = np.clip(temp_image[:, :, 2] + temp * 1.5, 0, 255)  # Increase Red
        temp_image[:, :, 0] = np.clip(temp_image[:, :, 0] + abs(temp) * 1.5, 0, 255)  # Increase Blue
    return temp_image

# Function to adjust Tint (green to magenta)
def adjust_tint(image, tint):
    # Increase or decrease the green/magenta tint
    tint_image = image.copy()
    if tint > 0:
        tint_image[:, :, 1] = np.clip(tint_image[:, :, 1] + tint * 2, 0, 255)  # Increase Green
    elif tint < 0:
        tint_image[:, :, 1] = np.clip(tint_image[:, :, 1] + tint * 2, 0, 255)  # Decrease Green
    return tint_image

# Function to adjust Vibrance (boosts less saturated colors)
def adjust_vibrance(image, vibrance):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    
    # Scale the saturation based on vibrance
    s = np.clip(s + vibrance, 0, 255)
    hsv_image = cv2.merge([h, s, v])
    vibrance_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    return vibrance_image

# Function to adjust Saturation (boosts or reduces all colors equally)
def adjust_saturation(image, saturation):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    
    # Scale the saturation value
    s = np.clip(s * (1 + saturation / 100.0), 0, 255)
    hsv_image = cv2.merge([h, s, v])
    saturation_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    return saturation_image

def adjust_color(image, temp=0, tint=0, vibrance=0, saturation=0):
    # Apply temperature, tint, vibrance, and saturation adjustments
    image = adjust_temperature(image, temp)
    image = adjust_tint(image, tint)
    image = adjust_vibrance(image, vibrance)
    # image = adjust_saturation(image, saturation)
    return image

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=5440,
    capture_height=3648,
    display_width=1920,
    display_height=1080,
    framerate=26,
    flip_method=2,
    exposure_time=10000,  # Exposure time in microseconds
    gain=4.0,  # Gain for the image (higher = brighter)
):
    return (
        "nvarguscamerasrc sensor-id=%d aelock=1 exposuretimerange=\"200, 200\" ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
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
                    
                    # frame = adjust_image(frame, contrast=1, brightness=0, 
                    #                               exposure=0.51, shadows=0, highlights=-0, 
                    #                               whites=0, blacks=-0)
                    
                    # frame = adjust_color(
                    #                     frame, 
                    #                     temp=-5,        # No temperature adjustment (change as needed)
                    #                     tint=0,      # Tint (Green-Magenta) adjustment
                    #                     vibrance=10,   # Vibrance adjustment
                    #                     saturation=49  # Saturation adjustment
                    #                 )

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
