import os
import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "image_model",
    "image_model.keras"
)

IMG_SIZE = (224, 224)


# ============================================================
# GLOBAL MODEL
# ============================================================

model = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_image_model():

    global model

    if model is None:

        if not os.path.exists(MODEL_PATH):

            raise FileNotFoundError(
                f"Image model not found: {MODEL_PATH}"
            )

        print("Loading TRUTHCHECK image model...")

        model = tf.keras.models.load_model(
            MODEL_PATH
        )

        print("Image model loaded successfully.")

    return model


# ============================================================
# PREPROCESS IMAGE
# ============================================================

def preprocess_image(image_path):

    # Open image
    image = Image.open(
        image_path
    ).convert("RGB")

    # Resize
    image = image.resize(
        IMG_SIZE
    )

    # Convert to NumPy
    image_array = np.array(
        image,
        dtype=np.float32
    )

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------
    # Pixel range:
    #
    # Before: 0 - 255
    # After : 0 - 1
    # --------------------------------------------------------

    image_array = image_array / 255.0

    # Add batch dimension
    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    return image_array


# ============================================================
# IMAGE AUTHENTICITY DETECTOR
# ============================================================

def detect_image(image_path):

    try:

        # ----------------------------------------------------
        # CHECK IMAGE
        # ----------------------------------------------------

        if not os.path.exists(image_path):

            return {
                "status": "error",
                "label": "Image Not Found",
                "ai_probability": 0,
                "real_probability": 0,
                "message": "Uploaded image could not be found."
            }


        # ----------------------------------------------------
        # LOAD MODEL
        # ----------------------------------------------------

        image_model = load_image_model()


        # ----------------------------------------------------
        # PREPROCESS
        # ----------------------------------------------------

        image_array = preprocess_image(
            image_path
        )


        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        prediction = image_model.predict(
            image_array,
            verbose=0
        )


        prediction = float(
            prediction[0][0]
        )


        # ----------------------------------------------------
        # CIFAKE CLASS MAPPING
        # ----------------------------------------------------
        #
        # Alphabetical class order:
        #
        # FAKE = 0
        # REAL = 1
        #
        # Therefore sigmoid output is treated as:
        #
        # prediction = REAL probability
        #
        # ----------------------------------------------------

        real_probability = prediction * 100

        ai_probability = (
            1.0 - prediction
        ) * 100


        # ----------------------------------------------------
        # LABEL
        # ----------------------------------------------------

        if ai_probability >= 70:

            label = "Likely AI-Generated"

        elif ai_probability >= 50:

            label = "Possibly AI-Generated"

        else:

            label = "Likely Real"


        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

        return {

            "status": "success",

            "label": label,

            "ai_probability": round(
                ai_probability,
                2
            ),

            "real_probability": round(
                real_probability,
                2
            ),

            "message": (
                "Image authenticity is estimated "
                "using the trained AI model. "
                "The result may contain false positives."
            )
        }


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        return {

            "status": "error",

            "label": "Image Analysis Failed",

            "ai_probability": 0,

            "real_probability": 0,

            "message": str(e)
        }