import os
import numpy as np
from sklearn.metrics import classification_report

from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# CONFIG
IMAGE_SIZE = 128
BATCH_SIZE = 20
EPOCHS = 5
TRAIN_DIR = "data/Training"
TEST_DIR = "data/Testing"
MODEL_PATH = "models/brain_tumor_vgg16.h5"

# DATA GENERATORS
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='sparse'
)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMAGE_SIZE, IMAGE_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='sparse',
    shuffle=False
)

class_labels = list(train_generator.class_indices.keys())
print("Class Labels:", class_labels)

# MODEL ARCHITECTURE
base_model = VGG16(weights="imagenet", include_top=False, input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3))

# Freeze all layers
for layer in base_model.layers:
    layer.trainable = False

# Unfreeze last few layers
for layer in base_model.layers[-5:]:
    layer.trainable = True

model = Sequential([
    Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3)),
    base_model,
    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.2),
    Dense(len(class_labels), activation='softmax')
])

model.compile(optimizer=Adam(learning_rate=0.0001),
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])

model.summary()

# TRAINING
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=test_generator
)

# EVALUATION
y_true = test_generator.classes
y_pred = model.predict(test_generator)
y_pred_classes = np.argmax(y_pred, axis=1)

print("\nClassification Report:")
print(classification_report(y_true, y_pred_classes, target_names=class_labels))

# SAVE MODEL
if not os.path.exists("models"):
    os.makedirs("models")

model.save(MODEL_PATH)
print(f"\n Model saved at {MODEL_PATH}")
