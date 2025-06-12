# generate_dummy_model.py

import numpy as np
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.utils import to_categorical

# Dummy class labels
class_labels = ["USD_1", "USD_10", "LBP_5000", "EUR_5", "EUR_10"]
num_classes = len(class_labels)

# Generate dummy image data: 50 samples of 224x224 RGB images
X = np.random.rand(50, 224, 224, 3)
y = np.random.randint(0, num_classes, 50)
y = to_categorical(y, num_classes)

# Simple CNN model
model = Sequential([
    Conv2D(16, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model on dummy data
model.fit(X, y, epochs=3, batch_size=10, verbose=1)

# Save the model to models/ directory
save_dir = os.path.join(os.getcwd(), "models")
os.makedirs(save_dir, exist_ok=True)

model_path = os.path.join(save_dir, "currency_model.h5")
model.save(model_path)

print(f"✅ Dummy model saved at: {model_path}")
