"""import cv2
import torch
import os
import requests  # For accurate geolocation
import time
from ultralytics import YOLO

# Path to your YOLOv8 model
model_path = r"D:\ObjectDetectionWithGeoLocation\model\yolov8m.pt"

# Load the model
model = YOLO(model_path)
model.model.eval()

# Open the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Create folders to save data
save_folder_images = 'images'
save_folder_data = 'data'
os.makedirs(save_folder_images, exist_ok=True)
os.makedirs(save_folder_data, exist_ok=True)

last_capture_time = 0
capture_delay = 1  # Capture every 1 second

# Exclude class ID 0 (human)
EXCLUDE_CLASS_ID = 0

# Function to get accurate geolocation using IPinfo API
API_URL = "https://ipinfo.io/json"
def get_accurate_geolocation():
    try:
        response = requests.get(API_URL)
        data = response.json()
        loc = data.get('loc', None)
        if loc:
            latitude, longitude = loc.split(',')
            return f"Latitude: {latitude}, Longitude: {longitude}"
        else:
            return "Geo-location not available"
    except Exception as e:
        return "Geo-location not available"

print("🚀 Camera is ON! Detecting objects... Press 'ESC' to exit.")

# Class names mapping (can be expanded as needed)
class_names = model.model.names

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame.")
        break

    # Run the YOLOv8 model
    results = model(frame)

    # Extract results
    boxes = results[0].boxes.xyxy.cpu().numpy()
    confidences = results[0].boxes.conf.cpu().numpy()
    class_ids = results[0].boxes.cls.cpu().numpy()

    # Process detections
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        confidence = confidences[i]
        class_id = int(class_ids[i])

        # Skip capturing humans
        if class_id == EXCLUDE_CLASS_ID:
            continue

        if confidence > 0.6:
            object_name = class_names[class_id]
            label = f"{object_name} - Confidence: {confidence:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Capture data every second
            current_time = time.time()
            if current_time - last_capture_time >= capture_delay:
                timestamp = int(time.time() * 1000)

                # Save the image
                image_filename = f"{save_folder_images}/detected_object_{timestamp}.jpg"
                cv2.imwrite(image_filename, frame[y1:y2, x1:x2])
                print(f"✅ Image saved: {image_filename}")

                # Get accurate geolocation
                geo_location = get_accurate_geolocation()

                # Save data
                data_filename = f"{save_folder_data}/data_{timestamp}.txt"
                with open(data_filename, 'w') as f:
                    f.write(f"Object Name: {object_name}\n")
                    f.write(f"Object ID: {class_id}\n")
                    f.write(f"Confidence: {confidence:.2f}\n")
                    f.write(f"Bounding Box: ({x1}, {y1}, {x2}, {y2})\n")
                    f.write(f"Geo-location: {geo_location}\n")
                print(f"✅ Data saved: {data_filename}")

                last_capture_time = current_time

    # Show camera feed
    cv2.imshow("🎥 Object Detection (Press 'ESC' to exit)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release camera and close all windows
cap.release()
cv2.destroyAllWindows()
print("📸 Camera closed. All data saved.") """

import cv2
import torch
import os
import requests
import time
import geocoder
from ultralytics import YOLO

# Path to your YOLOv8 model
model_path = r"D:\ObjectDetectionWithGeoLocation\model\yolov8m.pt"

# Load the model
model = YOLO(model_path)
model.model.eval()

# Open the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Create folders to save data
save_folder_images = 'images'
save_folder_data = 'data'
os.makedirs(save_folder_images, exist_ok=True)
os.makedirs(save_folder_data, exist_ok=True)

last_capture_time = 0
capture_delay = 1  # Capture every 1 second

# Exclude class ID 0 (human)
EXCLUDE_CLASS_ID = 0

# Function to get accurate geolocation using GPS-based IP Geolocation

def get_accurate_geolocation():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            latitude, longitude = g.latlng
            return f"Latitude: {latitude}, Longitude: {longitude}"
        else:
            return "Geo-location not available"
    except Exception as e:
        return "Geo-location not available"

print("🚀 Camera is ON! Detecting objects... Press 'ESC' to exit.")

# Class names mapping (can be expanded as needed)
class_names = model.model.names

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame.")
        break

    # Run the YOLOv8 model
    results = model(frame)

    # Extract results
    boxes = results[0].boxes.xyxy.cpu().numpy()
    confidences = results[0].boxes.conf.cpu().numpy()
    class_ids = results[0].boxes.cls.cpu().numpy()

    # Process detections
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        confidence = confidences[i]
        class_id = int(class_ids[i])

        # Skip capturing humans
        if class_id == EXCLUDE_CLASS_ID:
            continue

        if confidence > 0.6:
            object_name = class_names[class_id]
            label = f"{object_name} - Confidence: {confidence:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Capture data every second
            current_time = time.time()
            if current_time - last_capture_time >= capture_delay:
                timestamp = int(time.time() * 1000)

                # Save the image
                image_filename = f"{save_folder_images}/detected_object_{timestamp}.jpg"
                cv2.imwrite(image_filename, frame[y1:y2, x1:x2])
                print(f"✅ Image saved: {image_filename}")

                # Get accurate geolocation
                geo_location = get_accurate_geolocation()

                # Save data
                data_filename = f"{save_folder_data}/data_{timestamp}.txt"
                with open(data_filename, 'w') as f:
                    f.write(f"Object Name: {object_name}\n")
                    f.write(f"Object ID: {class_id}\n")
                    f.write(f"Confidence: {confidence:.2f}\n")
                    f.write(f"Bounding Box: ({x1}, {y1}, {x2}, {y2})\n")
                    f.write(f"Geo-location: {geo_location}\n")
                print(f"✅ Data saved: {data_filename}")

                last_capture_time = current_time

    # Show camera feed
    cv2.imshow("🎥 Object Detection (Press 'ESC' to exit)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release camera and close all windows
cap.release()
cv2.destroyAllWindows()
print("📸 Camera closed. All data saved.")


