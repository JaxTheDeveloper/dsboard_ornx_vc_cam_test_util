import cv2
import time
import threading
import subprocess
import numpy as np
import os

# this class runs in its own thread
class CameraProducer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True # die when main thread dies
        
        # camera pipeline
        self.pipeline = (
            "nvarguscamerasrc sensor-id=0 aelock=1 ! "
            "video/x-raw(memory:NVMM), width=5440, height=3648, framerate=10/1 ! "
            "nvvidconv ! video/x-raw, width=1920, height=1080, format=(string)BGRx ! "
            "videoconvert ! video/x-raw, format=BGR ! appsink"
        )
        
        # camera object
        self.cap = None
        self.latest_frame = None
        self.jpeg_frame = None
        self.gray_level = 0

        # control values updated from your v4l2-ctl image
        self.gain = 0
        self.exposure = 10000
        self.black_level = 0
        self.is_running = False
        
        # threading events
        self.start_signal = threading.Event()
        self.stop_signal = threading.Event()

    # main thread signals camera to start
    def start_camera(self):
        self.start_signal.set()

    # main thread signals camera to stop
    def stop_camera(self):
        self.stop_signal.set()

    # this is the main function of the thread
    def run(self):
        print("Camera thread started and waiting for signal...")
        while True:
            # wait here until start_camera() is called
            self.start_signal.wait()
            self.start_signal.clear() # reset signal
            
            print("Connecting to camera...")
            self.is_running = True
            
            # based on v4l2_01.py
            # apply v4l2 controls
            try:
                self.update_controls(self.gain, self.exposure, self.black_level)
            except Exception as e:
                print(f"Error applying controls before open: {e}")
                self.is_running = False
                continue # stop and wait for new signal
                
            print("Controls set opening camera...")

            # set gstreamer debug level right before opening
            print("Setting GStreamer debug level...")
            os.environ["GST_DEBUG"] = "3"

            # opn camera 
            print(self.pipeline)
            self.cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)
            
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                self.is_running = False
                continue # wait for new signal
            
            print("Camera is running")

            # main camera loop
            while self.is_running:
                # check for stop signal
                if self.stop_signal.is_set():
                    self.stop_signal.clear()
                    self.is_running = False
                    break
                    
                ret, frame = self.cap.read()
                
                if not ret:
                    print("Frame read error skipping")
                    time.sleep(0.1)
                    continue
                
                # store frame for web server
                self.latest_frame = frame
                
                # frame process
                # calculate gray level
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self.gray_level = int(np.mean(gray))
                
                # pre-encode jpeg
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                if ret:
                    self.jpeg_frame = buffer.tobytes()

                # slow down loop
                time.sleep(0.03) # approx 30fps

            # cleanup
            if self.cap:
                self.cap.release()
            self.cap = None
            self.latest_frame = None
            self.jpeg_frame = None
            self.gray_level = 0
            print("Camera hardware stopped")

    # get latest controls
    def get_controls(self):
        return {
            "gain": self.gain,
            "exposure": self.exposure,
            "black_level": self.black_level
        }

    # update v4l2 hardware controls
    def update_controls(self, gain, exposure, black_level):
        # store values
        self.gain = gain
        self.exposure = exposure
        self.black_level = black_level
        
        # update hardware
        try:
            base_cmd = "v4l2-ctl -d /dev/video0"
            
            # removed capture_output=True to let logs print to terminal
            print("Setting gain...")
            subprocess.run(base_cmd + " --set-ctrl=gain=" + str(gain), 
                                shell=True, check=True)

            print("Setting exposure...")
            subprocess.run(base_cmd + " --set-ctrl=exposure=" + str(exposure), 
                                shell=True, check=True)

            print("Setting black_level...")
            subprocess.run(base_cmd + " --set-ctrl=black_level=" + str(black_level), 
                                shell=True, check=True)
                                
            print("Controls updated successfully")
            
        except subprocess.CalledProcessError as e:
            # this will now print the *exact* error
            print(f"V4L2-CTL FAILED Command: '{e.cmd}'")
            print(f"VS4L2-CTL FAILED Returncode: {e.returncode}")
            # error message from v4l2-ctl should print directly to terminal
            raise e
        except FileNotFoundError as e:
            print("V4L2-CTL FAILED 'v4l2-ctl' command not found. Is it installed?")
            raise e

