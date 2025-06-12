# services/currency_recognition.py

import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

# Load the trained dummy model
model = tf.keras.models.load_model("models/currency_model.h5")

# Class labels must match training order
class_labels = ["USD_1", "USD_10", "LBP_5000", "EUR_5", "EUR_10"]

def recognize_currency(img_path):
    # Load image and preprocess
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # Predict
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions[0])
    return class_labels[predicted_class]
