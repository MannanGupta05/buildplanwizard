from ultralytics import YOLO
import numpy as np
import cv2
import json
from typing import Union

# Load model once at import

class YoloInference:
    def __init__(self, model_path, box_conf):
        self.model_path = model_path
        self.box_conf = box_conf

    def detect_yolo_objects(self, image):
        """
        Detect objects using YOLO and return results as a dictionary.
        
        Parameters:
            image_input: bytes, np.ndarray, or file path to an image.
        
        Returns:
            Dictionary of detections.
        """
        #j = 0
        model = YOLO(self.model_path)
        img = np.array(image)
        results = model(img)[0]
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            if conf >= self.box_conf:
                detections.append({
                    "class_id": cls,
                    "class_name": model.names[cls],
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]  # [left, top, right, bottom]
                })
                '''
                cropped_img = image.crop((x1, y1, x2, y2))
                name = str(j) + "cropped.jpg"
                cropped_img.save(name)
                j += 1
                '''




        return detections
