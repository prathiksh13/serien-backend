import cv2
import numpy as np
import tensorflow as tf
import keras
import os
import json
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, InputLayer
from keras.models import Sequential

# ---- FIX: Load model with compatibility ----
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "facialemotionmodel.json")
weights_path = os.path.join(script_dir, "facialemotionmodel.h5")

# FIX: Build model from config to avoid deserialization issues
with open(json_path, "r") as json_file:
    config = json.load(json_file)

# Build model from config
model = Sequential()
input_shape = None
for i, layer_config in enumerate(config['config']['layers']):
    layer_name = layer_config['class_name']
    if layer_name == 'InputLayer':
        input_shape = layer_config['config']['batch_input_shape'][1:]  # Get shape without batch
        continue
    
    layer_params = {k: v for k, v in layer_config['config'].items()}
    
    if layer_name == 'Conv2D':
        if input_shape and i == 1:  # First actual layer after input
            model.add(Conv2D(layer_params['filters'], layer_params['kernel_size'], 
                           strides=layer_params['strides'], padding=layer_params['padding'],
                           activation=layer_params['activation'], input_shape=input_shape))
        else:
            model.add(Conv2D(layer_params['filters'], layer_params['kernel_size'], 
                           strides=layer_params['strides'], padding=layer_params['padding'],
                           activation=layer_params['activation']))
    elif layer_name == 'MaxPooling2D':
        model.add(MaxPooling2D(pool_size=layer_params['pool_size'], 
                             strides=layer_params['strides'], padding=layer_params['padding']))
    elif layer_name == 'Dropout':
        model.add(Dropout(layer_params['rate']))
    elif layer_name == 'Flatten':
        model.add(Flatten())
    elif layer_name == 'Dense':
        model.add(Dense(layer_params['units'], activation=layer_params['activation']))

model.load_weights(weights_path)

# ---- Face detector ----
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)

# ---- Feature extraction ----
def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0

# ---- Webcam ----
webcam = cv2.VideoCapture(0)

labels = {
    0: 'angry',
    1: 'disgust',
    2: 'fear',
    3: 'happy',
    4: 'neutral',
    5: 'sad',
    6: 'surprise'
}

while True:
    ret, frame = webcam.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # FIX: detect faces on grayscale
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (48, 48))

        img = extract_features(face)

        # FIX: silence verbose spam
        pred = model.predict(img, verbose=0)
        label = labels[pred.argmax()]

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, label, (x, y-10),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                    2, (0, 0, 255), 2)

    cv2.imshow("Output", frame)

    # ESC key to exit
    if cv2.waitKey(1) == 27:
        break

webcam.release()
cv2.destroyAllWindows()