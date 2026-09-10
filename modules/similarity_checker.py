# Text similarity / plagiarism checking module
import re
from difflib import SequenceMatcher


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_similarity(text1, text2):
    text1 = clean_text(text1)
    text2 = clean_text(text2)

    if not text1 or not text2:
        return 0.0

    similarity = SequenceMatcher(
        None,
        text1,
        text2
    ).ratio()

    return round(similarity * 100, 2)


def check_similarity(text, reference_texts):

    if not text or not text.strip():
        return {
            "status": "success",
            "label": "No Text Provided",
            "similarity": 0.0
        }

    if not reference_texts:
        return {
            "status": "success",
            "label": "No Reference Available",
            "similarity": 0.0
        }

    scores = []

    for reference in reference_texts:
        score = calculate_similarity(text, reference)
        scores.append(score)

    max_similarity = max(scores)

    if max_similarity >= 80:
        label = "Possibly Copied"
    elif max_similarity >= 50:
        label = "Possibly Similar"
    else:
        label = "Likely Original"

    return {
        "status": "success",
        "label": label,
        "similarity": max_similarity
    }