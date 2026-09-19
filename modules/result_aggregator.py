# Combine image and text analysis results
def aggregate_results(image_result=None, text_result=None):
    """
    Combine image and text analysis results into one final result.
    """

    image_result = image_result or {}
    text_result = text_result or {}

    # ---------------- IMAGE RESULT ----------------

    image_label = str(
        image_result.get("label", "")
    ).lower()

    image_probability = image_result.get(
        "ai_probability",
        image_result.get("confidence", 0)
    )

    try:
        image_probability = float(image_probability)
    except (TypeError, ValueError):
        image_probability = 0.0

    # ---------------- TEXT RESULT ----------------

    text_ai = text_result.get(
        "ai_detection",
        text_result
    )

    if not isinstance(text_ai, dict):
        text_ai = {}

    text_label = str(
        text_ai.get("label", "")
    ).lower()

    text_probability = text_ai.get(
        "ai_probability",
        text_ai.get("confidence", 0)
    )

    try:
        text_probability = float(text_probability)
    except (TypeError, ValueError):
        text_probability = 0.0

    # ---------------- FINAL DECISION ----------------

    probabilities = []

    if image_result:
        probabilities.append(image_probability)

    if text_result and text_label not in (
        "",
        "no text provided",
        "unknown"
    ):
        probabilities.append(text_probability)

    if probabilities:
        final_probability = round(
            sum(probabilities) / len(probabilities),
            2
        )
    else:
        final_probability = 0.0

    # Decide final label
    if final_probability >= 70:
        final_label = "AI-generated likely"

    elif final_probability >= 40:
        final_label = "Possibly AI-generated"

    else:
        final_label = "Human-written likely"

    return {
        "label": final_label,
        "ai_probability": final_probability,
        "image_result": image_result,
        "text_result": text_result
    }


# ---------------- TEST ----------------

if __name__ == "__main__":

    image = {
        "label": "AI-generated",
        "ai_probability": 80
    }

    text = {
        "ai_detection": {
            "label": "AI-generated likely",
            "confidence": 75
        }
    }

    result = aggregate_results(image, text)

    print(result)