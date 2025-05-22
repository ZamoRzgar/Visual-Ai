from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from ultralytics import YOLO
import os
import threading
import json
import base64
import numpy as np
import cv2
from io import BytesIO

# Load YOLO model globally
model = None
def load_model():
    global model
    if model is None:
        model = YOLO('yolov8n.pt')
    return model

# Start loading the model in a background thread
threading.Thread(target=load_model).start()

def landing(request):
    """Render the landing page"""
    return render(request, 'detector/landing.html')

def index(request):
    """Render the detector page with webcam interface"""
    return render(request, 'detector/index.html')

def about(request):
    """Render the about page with information about the app"""
    return render(request, 'detector/about.html')

@csrf_exempt
def detect_objects(request):
    """Process image from form submission and display results"""
    if request.method != 'POST':
        return redirect('index')
    
    context = {}
    print("Processing detection request...")
    
    try:
        # Ensure model is loaded
        if model is None:
            print("Model not loaded, loading now...")
            load_model()
            if model is None:
                context['error'] = 'Failed to load detection model'
                return render(request, 'detector/index.html', context)
        
        # Check for the source of the image (webcam or file upload)
        frame = None
        
        # Method 1: Get image data from webcam capture (base64 data)
        image_data = request.POST.get('image_data', '')
        if image_data and image_data.startswith('data:image'):
            print(f"Processing webcam image: {len(image_data)} characters")
            # Extract the base64 data
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            print(f"Decoded image bytes: {len(image_bytes)} bytes")
            
            # Convert to numpy array for OpenCV processing
            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            print(f"Frame shape from webcam: {frame.shape if frame is not None else 'None'}")
        
        # Method 2: Get image from file upload
        elif 'image_upload' in request.FILES:
            uploaded_file = request.FILES['image_upload']
            print(f"Processing uploaded image: {uploaded_file.name}, size: {uploaded_file.size} bytes")
            
            # Read the file content
            file_bytes = uploaded_file.read()
            
            # Convert to numpy array for OpenCV processing
            np_arr = np.frombuffer(file_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            print(f"Frame shape from upload: {frame.shape if frame is not None else 'None'}")
        
        else:
            context['error'] = 'No image data received. Please either capture an image or upload a file.'
            print("No image data received")
            return render(request, 'detector/index.html', context)
        
        if frame is None:
            context['error'] = 'Failed to decode image data. Please try a different image.'
            return render(request, 'detector/index.html', context)
        
        # Run inference
        print("Running YOLO inference...")
        results = model(frame)
        result = results[0]
        
        # Process detections
        detections = []
        print(f"Found {len(result.boxes)} potential objects")
        
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            name = result.names[cls]
            
            # Only include detections with confidence > 0.4
            if conf > 0.4:
                # Draw bounding box on the frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{name} {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Add to detections list
                detections.append({
                    "name": name,
                    "confidence": conf * 100,  # Convert to percentage
                    "box": [x1, y1, x2, y2]
                })
                print(f"Detected {name} with confidence {conf:.2f}")
        
        # Generate description
        description = generate_description(detections)
        print(f"Generated description: {description}")
        
        # Convert processed frame back to base64
        print("Converting processed frame to base64...")
        _, buffer = cv2.imencode('.jpg', frame)
        processed_frame = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare context for template
        data_url = f'data:image/jpeg;base64,{processed_frame}'
        print(f"Generated data URL length: {len(data_url)} characters")
        
        context = {
            'processed_image': data_url,
            'detections': detections,
            'description': description,
            'detection_complete': True
        }
        
        print("Rendering result template...")
        return render(request, 'detector/result.html', context)
    
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Error in detect_objects: {str(e)}")
        print(traceback_str)
        context['error'] = f"Error processing image: {str(e)}"
        return render(request, 'detector/index.html', context)

def generate_description(detections):
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
                  f"({most_confident['confidence']:.1f}% sure)."
    
    return description
