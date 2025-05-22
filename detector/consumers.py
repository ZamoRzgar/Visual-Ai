import json
import base64
import numpy as np
import cv2
from channels.generic.websocket import AsyncWebsocketConsumer
from ultralytics import YOLO
import asyncio
import threading
import os
from django.conf import settings
import time

# Global model instance to avoid reloading for each connection
model = None

def load_yolo_model():
    global model
    if model is None:
        # Load the YOLO model
        model = YOLO("yolov8n.pt")  # Use smaller model for faster inference
    return model

# Load model in background thread to not block startup
threading.Thread(target=load_yolo_model).start()

class ObjectDetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connection attempt")
        await self.accept()
        self.active = True
        print("WebSocket connection accepted")
        
    async def disconnect(self, close_code):
        self.active = False
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'frame':
            # Process the frame for object detection
            image_data = data['frame'].split(',')[1]
            image_bytes = base64.b64decode(image_data)
            
            # Convert to numpy array for OpenCV processing
            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            # Ensure the YOLO model is loaded
            if model is None:
                load_yolo_model()
            
            # Run inference on the frame
            results = model(frame)
            result = results[0]  # Get the first result
            
            # Process detections
            detections = []
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                name = result.names[cls]
                
                # Only include detections with confidence > 0.5
                if conf > 0.5:
                    # Draw bounding box on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{name} {conf:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Add to detections list
                    detections.append({
                        "name": name,
                        "confidence": conf,
                        "box": [x1, y1, x2, y2]
                    })
            
            # Convert the processed frame back to base64 for sending to client
            _, buffer = cv2.imencode('.jpg', frame)
            processed_frame = base64.b64encode(buffer).decode('utf-8')
            
            # Generate description based on detections
            description = self.generate_description(detections)
            
            # Send the processed frame and detections back to the client
            await self.send(text_data=json.dumps({
                'type': 'processed_frame',
                'frame': f'data:image/jpeg;base64,{processed_frame}',
                'detections': detections,
                'description': description
            }))
    
    def generate_description(self, detections):
        """Generate a description of the detected objects"""
        if not detections:
            return "No objects detected."
        
        # Get the most confident detection
        most_confident = max(detections, key=lambda x: x["confidence"])
        
        # Count occurrences of each object type
        object_counts = {}
        for det in detections:
            name = det["name"]
            if name in object_counts:
                object_counts[name] += 1
            else:
                object_counts[name] = 1
        
        # Generate description text
        description = "I can see "
        object_phrases = []
        for obj_name, count in object_counts.items():
            if count > 1:
                object_phrases.append(f"{count} {obj_name}s")
            else:
                object_phrases.append(f"a {obj_name}")
        
        if len(object_phrases) == 1:
            description += object_phrases[0]
        elif len(object_phrases) == 2:
            description += f"{object_phrases[0]} and {object_phrases[1]}"
        else:
            description += ", ".join(object_phrases[:-1]) + f", and {object_phrases[-1]}"
        
        # Add information about the most confident object
        description += f". I'm most confident about the {most_confident['name']} " \
                      f"({most_confident['confidence']:.1%} sure)."
        
        return description
