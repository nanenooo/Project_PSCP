from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def detect_blink(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        
        if len(eyes) == 0:
            return True
    return False

@app.route('/detect-face', methods=['POST'])
def detect_face_route():
    data = request.json
    frame_data = data['frame']
    
    # Convert base64 image to numpy array
    image_data = base64.b64decode(frame_data.split(',')[1])
    image = np.array(Image.open(BytesIO(image_data)))
    
    # Detect faces
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    face_detected = len(faces) > 0
    
    return jsonify({"face_detected": face_detected})

@app.route('/detect-blink', methods=['POST'])
def detect_blink_route():
    data = request.json
    frame_data = data['frame']
    
    image_data = base64.b64decode(frame_data.split(',')[1])
    image = np.array(Image.open(BytesIO(image_data)))
    
    blink = detect_blink(image)
    
    return jsonify({"blink": blink})

if __name__ == "__main__":
    app.run(debug=True)
