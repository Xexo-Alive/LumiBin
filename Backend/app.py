from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import geocoder
import time
import torch
from ultralytics import YOLO
from threading import Thread
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # ✅ Allow Cross-Origin Requests

# ===========================
# ✅ FOLDER PATHS (Modify Carefully)
# ===========================
MODEL_PATH = r"D:\EcoVisionAR\Backend\Models\yolov8m.pt"
UPLOAD_FOLDER = r"D:\EcoVisionAR\Backend\uploads"
PROCESSED_FOLDER = r"D:\EcoVisionAR\Backend\processed_images"
RESULTS_FOLDER = r"D:\EcoVisionAR\Backend\detection_results"

# ✅ Ensure Folders Exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ===========================
# ✅ Load YOLOv8 Model
# ===========================
model = YOLO(MODEL_PATH)


# ===========================
# ✅ Function to Get Geolocation
# ===========================
def get_geolocation():
    try:
        g = geocoder.ip('me')
        if g and g.latlng:
            return g.latlng
    except Exception as e:
        print(f"Geolocation Error: {e}")
    return [0.0, 0.0]  # Default coordinates if geolocation fails


# ===========================
# ✅ Process Image & Detect Objects
# ===========================
def process_image(file_path, filename):
    results = model(file_path)  # Run YOLOv8 object detection
    detected_objects = []

    for result in results:
        for box in result.boxes:
            detected_objects.append(result.names[int(box.cls)])
    
    # ✅ Save processed image
    processed_path = os.path.join(PROCESSED_FOLDER, filename)
    result_img = results[0].plot()
    cv2_imwrite = getattr(results[0].plot, "imwrite", None)
    if cv2_imwrite:
        cv2_imwrite(processed_path, result_img)
    
    # ✅ Capture Geolocation
    latitude, longitude = get_geolocation()

    # ✅ Save Detection Data to JSON file
    data = {
        'image_path': processed_path,
        'original_path': file_path,
        'latitude': latitude,
        'longitude': longitude,
        'timestamp': time.time(),
        'datetime': datetime.now().isoformat(),
        'detected_objects': detected_objects
    }
    
    # Create a unique filename for the results
    result_filename = f"{os.path.splitext(filename)[0]}_{int(time.time())}.json"
    result_path = os.path.join(RESULTS_FOLDER, result_filename)
    
    # Save results as JSON
    with open(result_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"✅ Processed {filename}: {detected_objects}")  # Debugging log
    return data


# ===========================
# ✅ Root Route
# ===========================
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Eco Vision AR API!"}), 200


# ===========================
# ✅ Upload & Process API Route
# ===========================
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # ✅ Secure & Save File Locally
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # ✅ Start Image Processing in a Separate Thread
    thread = Thread(target=process_image, args=(file_path, filename))
    thread.start()

    return jsonify({
        'message': '✅ File uploaded successfully! Processing started...',
        'filename': filename
    }), 200


# ===========================
# ✅ Get Results API Route
# ===========================
@app.route('/results', methods=['GET'])
def get_results():
    results = []
    for filename in os.listdir(RESULTS_FOLDER):
        if filename.endswith('.json'):
            file_path = os.path.join(RESULTS_FOLDER, filename)
            with open(file_path, 'r') as f:
                results.append(json.load(f))
    
    return jsonify(results), 200


# ===========================
# ✅ Get Specific Result API Route
# ===========================
@app.route('/results/<result_id>', methods=['GET'])
def get_result(result_id):
    for filename in os.listdir(RESULTS_FOLDER):
        if filename.startswith(result_id) and filename.endswith('.json'):
            file_path = os.path.join(RESULTS_FOLDER, filename)
            with open(file_path, 'r') as f:
                return jsonify(json.load(f)), 200
    
    return jsonify({'error': 'Result not found'}), 404


# ===========================
# ✅ Monitor Folder for New Images
# ===========================
def monitor_folder():
    print("✅ Monitoring upload folder for new images...")
    processed_files = set()

    while True:
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if filename not in processed_files and os.path.isfile(file_path):
                print(f"🟢 New image detected: {filename}")
                process_image(file_path, filename)
                processed_files.add(filename)
        time.sleep(5)  # ✅ Check every 5 seconds


# ===========================
# ✅ Handle 404 Route
# ===========================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404


# ===========================
# ✅ Run Flask App & Start Monitoring Thread
# ===========================
if __name__ == '__main__':
    Thread(target=monitor_folder).start()
    app.run(debug=True, port=5000)