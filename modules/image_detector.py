import os
import numpy as np
import tensorflow as tf
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "image_model",
    "image_model.keras"
)

IMG_SIZE = (224, 224)


def detect_image(image_path):

    # Check model
    if not os.path.exists(MODEL_PATH):
        return {
            "status": "error",
            "message": "Image model is not available."
        }

    try:
        # Load model
        model = tf.keras.models.load_model(MODEL_PATH)

        # Open image
        image = Image.open(image_path).convert("RGB")
        image = image.resize(IMG_SIZE)

        # Convert to array
        image_array = np.array(image, dtype=np.float32)

        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)

        # Model prediction
        prediction = float(model.predict(image_array, verbose=0)[0][0])

        # CIFAKE classes:
        # FAKE = 0
        # REAL = 1

        real_probability = prediction * 100
        ai_probability = (1 - prediction) * 100

        if ai_probability >= 50:
            label = "Likely AI-Generated"
        else:
            label = "Likely Real"

        return {
            "status": "success",
            "label": label,
            "ai_probability": round(ai_probability, 2),
            "real_probability": round(real_probability, 2)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }