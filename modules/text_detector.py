# AI-text detection module
import re


def detect_text(text):
    """
    Basic text authenticity analysis.
    This is a prototype until a trained NLP model is connected.
    """

    if not text or not text.strip():
        return {
            "status": "success",
            "label": "No Text Provided",
            "ai_probability": 0,
            "original_probability": 0,
            "message": "No caption or text was provided."
        }

    text = text.strip()

    words = re.findall(r"\b[\w']+\b", text)
    word_count = len(words)

    if word_count < 5:
        return {
            "status": "success",
            "label": "Insufficient Text",
            "ai_probability": 0,
            "original_probability": 0,
            "message": "More text is required for reliable analysis."
        }

    score = 0

    # Long, highly structured text
    if word_count > 80:
        score += 15

    # Repeated words
    unique_words = len(set(word.lower() for word in words))
    repetition_ratio = unique_words / word_count

    if repetition_ratio < 0.55:
        score += 20

    # Very regular sentence structure
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) >= 4:
        lengths = [len(s.split()) for s in sentences]
        average_length = sum(lengths) / len(lengths)

        if average_length > 25:
            score += 15

    # Common AI-style phrases
    ai_phrases = [
        "in conclusion",
        "it is important to note",
        "overall",
        "furthermore",
        "moreover",
        "in today's world",
        "plays a crucial role",
        "it is worth noting",
        "as an ai"
    ]

    text_lower = text.lower()

    for phrase in ai_phrases:
        if phrase in text_lower:
            score += 10

    # Excessive punctuation
    if text.count(",") > word_count * 0.15:
        score += 10

    if score > 100:
        score = 100

    ai_probability = score
    original_probability = 100 - ai_probability

    if ai_probability >= 60:
        label = "Likely AI-Generated"
    elif ai_probability >= 40:
        label = "Possibly AI-Generated"
    else:
        label = "Likely Human-Written"

    return {
        "status": "success",
        "label": label,
        "ai_probability": round(ai_probability, 2),
        "original_probability": round(original_probability, 2),
        "message": "Text analyzed using the current prototype."
    }