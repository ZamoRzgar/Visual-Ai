document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const webcamElement = document.getElementById('webcam');
    const processedImageElement = document.getElementById('processed-image');
    const startButton = document.getElementById('start-btn');
    const stopButton = document.getElementById('stop-btn');
    const toggleViewButton = document.getElementById('toggle-view-btn');
    const objectDescriptionElement = document.getElementById('object-description');
    const detectionsListElement = document.getElementById('detections-list');
    
    // State variables
    let stream = null;
    let isProcessing = false;
    let showProcessed = false;
    let detectionInterval = null;
    
    // Event listeners
    startButton.addEventListener('click', startWebcam);
    stopButton.addEventListener('click', stopWebcam);
    toggleViewButton.addEventListener('click', toggleView);
    
    // Start webcam and begin object detection
    async function startWebcam() {
        try {
            // Get webcam access
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'environment' // Prefer back camera if available
                } 
            });
            
            // Set up webcam
            webcamElement.srcObject = stream;
            webcamElement.style.display = 'block';
            processedImageElement.style.display = 'none';
            
            // Enable/disable buttons
            startButton.disabled = true;
            stopButton.disabled = false;
            toggleViewButton.disabled = false;
            
            // Update description
            objectDescriptionElement.textContent = 'Starting object detection...';
            
            // Start sending frames for processing
            detectionInterval = setInterval(processFrame, 800); // Process frames every 800ms (less frequent for HTTP)
            
        } catch (error) {
            console.error('Error accessing webcam:', error);
            objectDescriptionElement.textContent = 'Error accessing webcam. Please ensure you have a webcam connected and you\'ve granted permission to use it.';
        }
    }
    
    // Stop webcam and processing
    function stopWebcam() {
        // Clear detection interval
        if (detectionInterval) {
            clearInterval(detectionInterval);
            detectionInterval = null;
        }
        
        // Stop all tracks from webcam stream
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        // Reset UI
        webcamElement.srcObject = null;
        processedImageElement.src = '';
        objectDescriptionElement.textContent = 'Start the webcam to detect objects.';
        detectionsListElement.innerHTML = '<li class="list-group-item text-center">No objects detected yet</li>';
        
        // Update buttons
        startButton.disabled = false;
        stopButton.disabled = true;
        toggleViewButton.disabled = true;
    }
    
    // Process a frame from the webcam using HTTP
    async function processFrame() {
        if (isProcessing || !stream) {
            return;
        }
        
        try {
            // Create a canvas to capture the current frame
            const canvas = document.createElement('canvas');
            canvas.width = webcamElement.videoWidth;
            canvas.height = webcamElement.videoHeight;
            
            // Draw the current frame to the canvas
            const ctx = canvas.getContext('2d');
            ctx.drawImage(webcamElement, 0, 0, canvas.width, canvas.height);
            
            // Convert to base64 data URL
            const dataURL = canvas.toDataURL('image/jpeg', 0.8);
            
            // Mark as processing to prevent sending too many frames
            isProcessing = true;
            
            // Send the frame to the server for processing via HTTP
            console.log('Sending detection request...');
            const response = await fetch('/api/detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: dataURL
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Update processed image
            processedImageElement.src = data.processed_image;
            
            // Show appropriate view based on toggle state
            if (showProcessed) {
                webcamElement.style.display = 'none';
                processedImageElement.style.display = 'block';
            } else {
                webcamElement.style.display = 'block';
                processedImageElement.style.display = 'none';
            }
            
            // Update description
            objectDescriptionElement.textContent = data.description;
            
            // Update detections list
            updateDetectionsList(data.detections);
            
        } catch (error) {
            console.error('Error processing frame:', error);
            objectDescriptionElement.textContent = 'Error processing image. Please try again.';
        } finally {
            // Allow processing next frame regardless of success/failure
            isProcessing = false;
        }
    }
    
    // Toggle between raw webcam and processed view
    function toggleView() {
        showProcessed = !showProcessed;
        
        if (showProcessed) {
            webcamElement.style.display = 'none';
            processedImageElement.style.display = 'block';
            toggleViewButton.textContent = 'Show Webcam';
        } else {
            webcamElement.style.display = 'block';
            processedImageElement.style.display = 'none';
            toggleViewButton.textContent = 'Show Detection';
        }
    }
    
    // Update the detections list
    function updateDetectionsList(detections) {
        if (!detections || detections.length === 0) {
            detectionsListElement.innerHTML = '<li class="list-group-item text-center">No objects detected</li>';
            return;
        }
        
        // Clear the list
        detectionsListElement.innerHTML = '';
        
        // Add each detection to the list
        detections.forEach(detection => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            
            // Create badge for confidence
            const confidenceBadge = document.createElement('span');
            confidenceBadge.className = 'badge bg-primary rounded-pill';
            confidenceBadge.textContent = `${(detection.confidence * 100).toFixed(1)}%`;
            
            // Set list item content
            listItem.innerHTML = `<strong>${detection.name}</strong>`;
            listItem.appendChild(confidenceBadge);
            
            // Add to list
            detectionsListElement.appendChild(listItem);
        });
    }
});
