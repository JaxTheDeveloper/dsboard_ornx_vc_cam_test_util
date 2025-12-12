#!/usr/bin/env python3
"""
VC-IMX183C Camera Controller with v4l2 Controls
Adjustable parameters for color and exposure tuning
"""

import cv2
import subprocess
import time
import signal
import sys

class V4L2CameraController:
    def __init__(self, device="/dev/video0", sensor_id=0):
        self.device = device
        self.sensor_id = sensor_id
        self.cap = None
        
        # ========================
        # 🎨 ADJUSTABLE PARAMETERS
        # ========================
        
        # 📈 Exposure & Gain
        self.exposure_auto = 1           # 0=auto, 1=manual, 2=shutter priority, 3=aperture priority
        self.exposure_absolute = 10000     # Exposure time (1-10000)
        self.gain = 1                    # Analog gain (1-16)
        
        # 🎨 Color Settings
        self.saturation = 180            # Saturation (0-200, 100=normal)
        self.contrast = 160              # Contrast (0-200, 100=normal)
        self.brightness = 20             # Brightness (-100 to 100, 0=normal)
        self.sharpness = 150             # Sharpness (0-200, 100=normal)
        self.hue = 0                     # Hue (-180 to 180, 0=normal)
        
        # ⚖️ White Balance
        self.white_balance_auto = 0      # 0=manual, 1=auto
        self.white_balance_temperature = 5000  # Color temperature (2800-10000)
        
        # 🔇 Noise Reduction
        self.denoise = 0                 # Denoise (0-100, 0=off)
        
        print("🎛️  V4L2 Camera Controller Initialized")
        print("💡 Adjust parameters in the code and restart")
    
    def set_v4l2_control(self, control, value):
        """Set individual v4l2 control"""
        cmd = f"v4l2-ctl -d {self.device} --set-ctrl={control}={value}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {control:30} = {value}")
                return True
            else:
                print(f"❌ {control:30} failed: {result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"❌ Error setting {control}: {e}")
            return False
    
    def get_v4l2_control(self, control):
        """Get current v4l2 control value"""
        cmd = f"v4l2-ctl -d {self.device} --get-ctrl={control}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"❌ Error getting {control}: {e}")
            return None
    
    def list_all_controls(self):
        """List all available v4l2 controls"""
        print("\n📋 Available v4l2 controls:")
        cmd = f"v4l2-ctl -d {self.device} --list-ctrls"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Failed to list controls")
    
    def apply_camera_settings(self):
        """Apply all camera settings via v4l2"""
        print("\n⚙️ Applying camera settings...")
        
        settings = [
            # Exposure & Gain
            ("exposure_auto", self.exposure_auto),
            ("exposure_absolute", self.exposure_absolute),
            ("gain", self.gain),
            
            # Color & Image Quality
            ("saturation", self.saturation),
            ("contrast", self.contrast),
            ("brightness", self.brightness),
            ("sharpness", self.sharpness),
            ("hue", self.hue),
            
            # White Balance
            ("white_balance_auto", self.white_balance_auto),
            ("white_balance_temperature", self.white_balance_temperature),
            
            # Noise Reduction
            ("denoise", self.denoise),
        ]
        
        success_count = 0
        for control, value in settings:
            if self.set_v4l2_control(control, value):
                success_count += 1
        
        print(f"✅ Applied {success_count}/{len(settings)} settings")
        return success_count > 0
    
    def create_gstreamer_pipeline(self):
        """Create simple GStreamer pipeline (no override)"""
        return (
            f"nvarguscamerasrc sensor-id={self.sensor_id} ! "
            "video/x-raw(memory:NVMM), width=1920, height=1080, framerate=20/1 ! "
            "nvvidconv ! video/x-raw, width=1280, height=720 ! "
            "videoconvert ! video/x-raw, format=BGR ! appsink"
        )
    
    def start_camera(self):
        """Start camera with applied settings"""
        # Apply v4l2 settings first
        if not self.apply_camera_settings():
            print("⚠️  Some settings failed to apply, continuing anyway...")
        
        # Wait for settings to take effect
        time.sleep(1)
        
        # Start GStreamer pipeline
        pipeline = self.create_gstreamer_pipeline()
        print(f"\n📹 Starting camera pipeline...")
        print(f"Pipeline: {pipeline}")
        
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            print("❌ Failed to open camera")
            return False
        
        print("✅ Camera started successfully")
        return True
    
    def read_frame(self):
        """Read frame from camera"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            return ret, frame
        return False, None
    
    def stop_camera(self):
        """Stop camera and cleanup"""
        if self.cap:
            self.cap.release()
            print("✅ Camera stopped")
    
    def print_current_settings(self):
        """Print current camera settings"""
        print("\n📊 Current Camera Settings:")
        print("=" * 50)
        
        controls_to_check = [
            "exposure_auto", "exposure_absolute", "gain",
            "saturation", "contrast", "brightness", "sharpness", "hue",
            "white_balance_auto", "white_balance_temperature", "denoise"
        ]
        
        for control in controls_to_check:
            value = self.get_v4l2_control(control)
            if value:
                print(f"  {control:25}: {value}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n\n🛑 Shutting down...')
    if camera:
        camera.stop_camera()
    sys.exit(0)

# ========================
# 🎯 USAGE EXAMPLES
# ========================

def apply_preset_daytime():
    """Preset for daytime outdoor"""
    camera.exposure_auto = 1
    camera.exposure_absolute = 50      # Shorter exposure
    camera.gain = 2                    # Lower gain
    camera.saturation = 160
    camera.contrast = 150
    camera.brightness = 10
    camera.white_balance_temperature = 5500  # Daylight
    print("✅ Applied daytime preset")

def apply_preset_nighttime():
    """Preset for nighttime"""
    camera.exposure_auto = 1
    camera.exposure_absolute = 500     # Longer exposure
    camera.gain = 12                   # Higher gain
    camera.saturation = 180
    camera.contrast = 140
    camera.brightness = 30
    camera.white_balance_temperature = 4000  # Warmer
    print("✅ Applied nighttime preset")

def apply_preset_vivid():
    """Preset for vivid colors"""
    camera.saturation = 200
    camera.contrast = 180
    camera.sharpness = 180
    camera.brightness = 15
    print("✅ Applied vivid preset")

# ========================
# 🚀 MAIN EXECUTION
# ========================

if __name__ == "__main__":
    # Initialize camera controller
    camera = V4L2CameraController(device="/dev/video0", sensor_id=0)
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 60)
    print("📷 VC-IMX183C Camera Controller with v4l2 Controls")
    print("=" * 60)
    
    # List available controls (optional)
    # camera.list_all_controls()
    
    # Apply preset (uncomment one)
    # apply_preset_daytime()
    # apply_preset_nighttime()
    # apply_preset_vivid()
    
    # Start camera
    if camera.start_camera():
        camera.print_current_settings()
        
        print("\n🎮 Controls:")
        print("  • Press 'q' to quit")
        print("  • Press 's' to save current frame")
        print("  • Press 'p' to print current settings")
        print("  • Press '1' for Daytime preset")
        print("  • Press '2' for Nighttime preset") 
        print("  • Press '3' for Vivid preset")
        print("  • Adjust parameters in code and restart")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = camera.read_frame()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            # Display frame
            cv2.imshow("VC-IMX183C Camera", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"capture_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"💾 Saved: {filename}")
            elif key == ord('p'):
                camera.print_current_settings()
            elif key == ord('1'):
                apply_preset_daytime()
                camera.apply_camera_settings()
            elif key == ord('2'):
                apply_preset_nighttime()
                camera.apply_camera_settings()
            elif key == ord('3'):
                apply_preset_vivid()
                camera.apply_camera_settings()
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                fps = frame_count / (time.time() - start_time)
                print(f"📊 FPS: {fps:.1f}")
        
        # Cleanup
        camera.stop_camera()
        cv2.destroyAllWindows()
        print("👋 Bye!")