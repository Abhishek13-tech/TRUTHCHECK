import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2

# CIFAKE dataset
TRAIN_DIR = r"C:\Users\HP\Downloads\archive\train"
TEST_DIR = r"C:\Users\HP\Downloads\archive\test"

MODEL_DIR = r"C:\Users\HP\Downloads\TRUTHCHECK\models\image_model"
MODEL_PATH = os.path.join(MODEL_DIR, "image_model.keras")

os.makedirs(MODEL_DIR, exist_ok=True)

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# Small subset for fast training
TRAIN_SAMPLES = 5000
TEST_SAMPLES = 1000

# Load training dataset
train_data = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=True,
    seed=42
)

# Load test dataset
test_data = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    shuffle=False
)

print("Classes:", train_data.class_names)

# Take only a small number of batches
train_batches = TRAIN_SAMPLES // BATCH_SIZE
test_batches = TEST_SAMPLES // BATCH_SIZE

train_data = train_data.take(train_batches)
test_data = test_data.take(test_batches)

AUTOTUNE = tf.data.AUTOTUNE

train_data = train_data.prefetch(AUTOTUNE)
test_data = test_data.prefetch(AUTOTUNE)

# Data augmentation
augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1)
])

# MobileNetV2
base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False

# Model
model = models.Sequential([
    augmentation,
    layers.Rescaling(1.0 / 127.5, offset=-1),
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# Train
history = model.fit(
    train_data,
    validation_data=test_data,
    epochs=3
)

# Save
model.save(MODEL_PATH)

print("\nTraining completed!")
print("Model saved at:")
print(MODEL_PATH)