import os
import time
import cv2
import onnxruntime as ort
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
from PIL.ExifTags import TAGS

MODEL_PATH = "D:\\EcoVisonAR\\Backend\\Models\\yolov8m.onnx"
IMAGE_FOLDER = r"D:\EcoVisonAR\Backend\uploads" 
CONFIDENCE_THRESHOLD = 0.5

CLASS_NAMES = {
    0: 'person',
    1: 'bicycle',
    2: 'car',
    3: 'motorbike',
    4: 'aeroplane',
    5: 'bus',
    6: 'train',
    7: 'truck',
    8: 'boat',
    9: 'plastic_bottle',
    10: 'cardboard_box',
    11: 'plastic_bag',
    12: 'can',
}

try:
    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
    print("ONNX Model Loaded Successfully.")
except Exception as e:
    print(f"Error Loading Model: {e}")
    exit(1)

def preprocess_image(image_path):
    """Loads and preprocesses an image for YOLO inference."""
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} not found.")
        return None

    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to read {image_path}. File may be corrupted or in an unsupported format.")
        return None

    img = cv2.resize(img, (640, 640))
    img = img / 255.0
    img = np.transpose(img, (2, 0, 1)).astype(np.float32)
    img = np.expand_dims(img, axis=0)
    return img

def post_process_yolo(output, image_path):
    """Parses YOLO output to extract bounding boxes and class predictions."""
    detections = output[0]
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Unable to read {image_path}.")
        return [], [], []

    height, width, _ = image.shape
    boxes, scores, class_ids = [], [], []

    for detection in detections:
        x, y, w, h, conf, cls_id = detection[:6]
        if conf > CONFIDENCE_THRESHOLD:
            x1, y1 = int((x - w / 2) * width), int((y - h / 2) * height)
            x2, y2 = int((x + w / 2) * width), int((y + h / 2) * height)

            boxes.append([x1, y1, x2, y2])
            scores.append(float(conf))
            class_ids.append(int(cls_id))

    return boxes, scores, class_ids

def format_detection_results(boxes, scores, class_ids):
    """Formats detection results into a readable text."""
    if not boxes:
        return "No objects detected."

    result_text = "Detection Results:\n"
    for i in range(len(boxes)):
        box = boxes[i]
        score = scores[i]
        class_id = class_ids[i]

        object_name = CLASS_NAMES.get(class_id, 'Unknown')
        
        if object_name == 'Unknown':
            if class_id == 9:
                object_name = 'Plastic Bottle'
            elif class_id == 10:
                object_name = 'Cardboard Box'
            elif class_id == 11:
                object_name = 'Plastic Bag'
            elif class_id == 12:
                object_name = 'Can'
            else:
                object_name = 'Other Waste'

        result_text += f"Object: {object_name}, Bounding Box: {box}, Confidence: {score:.2f}\n"

    return result_text

def run_yolo(image_path):
    """Runs YOLO inference on the image and converts the results to text."""
    img = preprocess_image(image_path)
    if img is None:
        return "Error in processing image."

    try:
        outputs = session.run(None, {"images": img})
    except Exception as e:
        print(f"Error during inference: {e}")
        return "Error during inference."

    boxes, scores, class_ids = post_process_yolo(outputs[0], image_path)

    result_text = format_detection_results(boxes, scores, class_ids)

    print(f"Detection Results for {image_path}: \n{result_text}")
    return result_text

def wait_for_file(image_path, retries=10, delay=1):
    """Waits until the file is available or the retries run out."""
    for i in range(retries):
        if os.path.exists(image_path) and not image_path.lower().endswith(".crdownload"):
            return True
        print(f"Waiting for file {image_path}... Retry {i + 1}")
        time.sleep(delay)
    return False

def get_geotagged_location(image_path):
    """Extracts geotagged location from the image (if available)."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data is None:
            return None
        
        gps_info = None
        for tag, value in exif_data.items():
            if TAGS.get(tag, tag) == 'GPSInfo':
                gps_info = value
                break

        if gps_info is None:
            return None
        
        # GPS data is usually in the format (latitude, longitude)
        lat = gps_info.get(2)  # Latitude (degrees, minutes, seconds)
        lon = gps_info.get(4)  # Longitude (degrees, minutes, seconds)

        if lat and lon:
            lat_decimal = lat[0] + lat[1] / 60 + lat[2] / 3600
            lon_decimal = lon[0] + lon[1] / 60 + lon[2] / 3600
            return lat_decimal, lon_decimal
        return None
    except Exception as e:
        print(f"Error extracting geotag: {e}")
        return None

def save_geotag_location(image_path, lat_lon):
    """Saves the geotag location into a text file in the image's folder."""
    if lat_lon is None:
        print(f"No geotag found for {image_path}.")
        return

    folder_path = os.path.dirname(image_path)
    geo_tag_file = os.path.join(folder_path, "geotag.txt")

    with open(geo_tag_file, "w") as file:
        file.write(f"Latitude: {lat_lon[0]}, Longitude: {lat_lon[1]}\n")
    print(f"Geotag saved at: {geo_tag_file}")

class ImageHandler(FileSystemEventHandler):
    """Handles new image files detected in the uploads folder."""
    def on_created(self, event):
        image_path = os.path.abspath(event.src_path)

        if image_path.lower().endswith((".jpg", ".png", ".jpeg")):
            print(f"New Image Detected: {image_path}")

            if not wait_for_file(image_path):
                print(f"Error: File {image_path} not available after waiting.")
                return

            lat_lon = get_geotagged_location(image_path)
            save_geotag_location(image_path, lat_lon)

            result_text = run_yolo(image_path)
            print(f"Results: \n{result_text}")

observer = Observer(timeout=1)  
event_handler = ImageHandler()
observer.schedule(event_handler, path=IMAGE_FOLDER, recursive=False)

try:
    observer.start()
    print(f"Monitoring folder: {IMAGE_FOLDER} for new images... Press Ctrl+C to stop.")
    
    while True:
        time.sleep(10)  
except KeyboardInterrupt:
    print("\nStopping folder monitoring...")
    observer.stop()
observer.join()
print("Monitoring stopped successfully.")
