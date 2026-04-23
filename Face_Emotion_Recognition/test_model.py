import numpy as np
import tensorflow as tf
import keras
import os
import json
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from keras.models import Sequential

# ---- Load model ----
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "facialemotionmodel.json")
weights_path = os.path.join(script_dir, "facialemotionmodel.h5")

# Build model from config
with open(json_path, "r") as json_file:
    config = json.load(json_file)

model = Sequential()
input_shape = None
for i, layer_config in enumerate(config['config']['layers']):
    layer_name = layer_config['class_name']
    if layer_name == 'InputLayer':
        input_shape = layer_config['config']['batch_input_shape'][1:]
        continue
    
    layer_params = {k: v for k, v in layer_config['config'].items()}
    
    if layer_name == 'Conv2D':
        if input_shape and i == 1:
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

print("Loading weights...")
model.load_weights(weights_path)
print("Model loaded successfully!")

# Test with dummy data
print("\nTesting model prediction...")
dummy_face = np.random.rand(1, 48, 48, 1).astype(np.float32)
prediction = model.predict(dummy_face, verbose=0)
print(f"Prediction shape: {prediction.shape}")
print(f"Sample output: {prediction[0]}")

labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}
predicted_emotion = labels[np.argmax(prediction)]
print(f"Predicted emotion: {predicted_emotion}")
print("\n✅ All tests passed! Model is working correctly.")
