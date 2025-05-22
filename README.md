# Visual AI: Object Detection Application

A modern web application that detects objects in images using advanced computer vision. The app offers two convenient ways to analyze images: capture directly from your webcam or upload existing images from your device. It provides detailed descriptions and visual annotations of the objects it detects.

## Features

- **Dual Input Methods**:
  - Webcam capture for real-time image analysis
  - Image upload for analyzing existing photos
- Utilizes YOLO v8 (You Only Look Once) model for fast and accurate detection
- Web-based interface with no installation required
- Displays bounding boxes around detected objects with confidence scores
- Provides natural language descriptions of detected objects
- Modern, responsive design that works across devices

## Model Information

### YOLO v8

This application uses the YOLO v8 model from Ultralytics, which is a state-of-the-art object detection system. Key details about the model:

- **Dataset**: The model is pre-trained on the COCO (Common Objects in Context) dataset
- **Object Classes**: Can detect 80 different common object categories including:
  - People: person
  - Animals: dog, cat, bird, horse, sheep, cow, elephant, bear, zebra, giraffe, etc.
  - Vehicles: car, truck, bicycle, motorcycle, bus, train, airplane, boat
  - Everyday items: bottle, cup, chair, couch, bed, dining table, toilet, TV, laptop, cell phone
  - Food items: banana, apple, sandwich, orange, broccoli, carrot, pizza, cake
  - And many more
- **Performance**: YOLO v8 is designed for both speed and accuracy, making it suitable for real-time applications
- **Detection Process**: The model processes the entire image in a single pass (hence "You Only Look Once") and can detect multiple objects simultaneously

### How Detection Works

1. **Image Capture**: The application captures a frame from your webcam
2. **Image Processing**: The captured image is sent to the server for processing
3. **Object Detection**: YOLO v8 analyzes the image and identifies objects with their locations
4. **Bounding Box Generation**: The system draws rectangles around detected objects
5. **Confidence Scoring**: Each detection includes a confidence score (0-100%)
6. **Description Generation**: Based on the detected objects, a natural language description is generated

## Technologies Used

### Backend
- **Django**: Python web framework for the server-side logic
- **Ultralytics YOLO**: Deep learning model for object detection
- **OpenCV**: Computer vision library for image processing
- **NumPy**: Numerical computing library for handling image data

### Frontend
- **HTML5/CSS3**: Modern web standards for structure and styling
- **JavaScript**: For webcam handling and user interface interactions
- **Bootstrap 5**: Frontend framework for responsive design
- **WebRTC**: Web standard for accessing the device camera

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Run the development server: `python manage.py runserver`

## Usage

### Webcam Method
1. Navigate to the detector page
2. Select the "Webcam" tab (selected by default)
3. Click "Start Webcam" and grant camera permissions when prompted
4. Position objects in front of your camera that you want to detect
5. Click the "Capture & Detect" button to process the current frame

### Upload Method
1. Navigate to the detector page
2. Select the "Upload Image" tab
3. Click "Select Image" to choose an image from your device
4. Once your image appears in the preview, click "Detect Objects"

### Results
- View the processed image with detection boxes highlighting identified objects
- Explore the detailed list of detected objects and their confidence scores
- Read the natural language description summarizing what was found
- Click "Detect Another Object" to return to the detector interface

## Project Structure

```
object-detection-app/
├── detector/                 # Main Django app
│   ├── templates/            # HTML templates
│   │   └── detector/         # App-specific templates
│   │       ├── about.html    # About page
│   │       ├── base.html     # Base template with common elements
│   │       ├── index.html    # Detector page with webcam
│   │       ├── landing.html  # Landing/home page
│   │       └── result.html   # Results display page
│   ├── urls.py               # URL routing
│   └── views.py              # View functions
├── object_detector/          # Django project settings
├── static/                   # Static files
│   ├── css/                  # Stylesheets
│   ├── img/                  # Images
│   └── js/                   # JavaScript files
├── venv/                     # Virtual environment (not in repo)
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
└── yolov8n.pt               # YOLO v8 model weights
```

## Performance Considerations

- The application processes images on the server, so detection speed depends on server capabilities
- YOLO v8 is optimized for performance but requires sufficient CPU/GPU resources for real-time processing
- The application is designed for educational and demonstration purposes

## Privacy

- All image processing occurs locally on the server
- No images or detection data are stored permanently
- No personal information is collected during the detection process

## Future Enhancements

- Real-time detection option for continuous processing
- Support for uploaded images in addition to webcam capture
- Mobile-optimized interface for better experience on smartphones
- Additional detection models for specialized use cases
