from transformers import pipeline

# Load AI text detection model
detector = pipeline(
    "text-classification",
    model="rasbt/ai-text-detector-distilbert"
)


def detect_ai_text(text):
    """
    Detect whether the given text is likely AI-generated or human-written.
    """

    if not text or not text.strip():
        return {
            "label": "Unknown",
            "confidence": 0.0
        }

    result = detector(text[:2000])[0]

    label = result["label"]
    confidence = round(result["score"] * 100, 2)

    if label.upper() == "AI":
        final_label = "AI-generated likely"
    else:
        final_label = "Human-written likely"

    return {
        "label": final_label,
        "confidence": confidence
    }


# Test
if __name__ == "__main__":
    sample_text = """
    Artificial intelligence is transforming the way people work,
    communicate, and learn in the modern world.
    """

    print(detect_ai_text(sample_text))
