import cv2
import numpy as np
import onnxruntime as ort
import os

onnx_model_path = r"D:\EcoVisonAR\Backend\Models\yolov8m.onnx"

if not os.path.exists(onnx_model_path):
    raise FileNotFoundError(f"ONNX model file not found: {onnx_model_path}")

session = ort.InferenceSession(onnx_model_path)

image_path = r"D:\EcoVisonAR\Backend\uploads\xyz.png"
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image file not found: {image_path}")

image = cv2.imread(image_path)
image = cv2.resize(image, (640, 640))
image = image.astype(np.float32) / 255.0
image = np.transpose(image, (2, 0, 1))
image = np.expand_dims(image, axis=0)

input_name = session.get_inputs()[0].name
output = session.run(None, {input_name: image})[0]

print("Inference completed! Output shape:", output.shape)