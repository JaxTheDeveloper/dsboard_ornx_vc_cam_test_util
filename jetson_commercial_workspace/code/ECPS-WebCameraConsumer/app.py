from flask import Flask, render_template, Response, request, jsonify
from camera_producer import CameraProducer
import time

app = Flask(__name__)

# --- global camera object ---
# create and start the camera thread
camera_producer = CameraProducer()
camera_producer.start()


# --- web page routes ---

@app.route('/')
def index():
    # test route
    return "Server is running! Go to /controls to see the app."

@app.route('/controls')
def controls():
    # main page
    return render_template('index.html')


# --- api routes ---

@app.route('/start_camera', methods=['POST'])
def start_camera():
    print("Received /start_camera request")
    camera_producer.start_camera()
    return jsonify({"status": "camera starting"})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    print("Received /stop_camera request")
    camera_producer.stop_camera()
    return jsonify({"status": "camera stopping"})

@app.route('/set_controls', methods=['POST'])
def set_controls():
    data = request.json
    try:
        camera_producer.update_controls(
            data['gain'],
            data['exposure'],
            data['black_level']
        )
        return jsonify({"status": "controls updated"})
    except Exception as e:
        print(f"Error updating controls: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_status')
def get_status():
    status = {
        'controls': camera_producer.get_controls(),
        'gray_level': camera_producer.gray_level,
        'is_running': camera_producer.is_running # <<< FIX 1: Was _running.is_set()
    }
    return jsonify(status)

# --- video streaming ---

def gen(producer):
    print("Starting video stream generator...")
    while True:
        # wait for a new frame
        while producer.jpeg_frame is None:
            if not producer.is_running:
                print("Generator stopping producer is not running")
                return
            time.sleep(0.01)
        
        frame = producer.jpeg_frame # <<< FIX 2: Was get_latest_frame()
        
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        # slow down if not getting new frames
        time.sleep(0.03) # approx 30fps

@app.route('/video_feed')
def video_feed():
    return Response(gen(camera_producer),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# --- main ---

if __name__ == '__main__':
    print("Starting Flask server...")
    # debug=True causes server to restart on code changes
    # host='0.0.0.0' makes it accessible on your network
    app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)

