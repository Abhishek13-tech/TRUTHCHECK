from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import re


# ==========================================
# Load our trained AI/Human detection model
# ==========================================

MODEL_PATH = "models/ai_detector/final"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)

detector = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    top_k=None,
    truncation=True,
    max_length=256
)


# ==========================================
# Split long text into smaller chunks
# ==========================================

def split_text(text, max_words=80):

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text.strip()
    )

    chunks = []
    current_chunk = []

    for sentence in sentences:

        words = sentence.split()

        if len(current_chunk) + len(words) <= max_words:

            current_chunk.extend(words)

        else:

            if current_chunk:
                chunks.append(
                    " ".join(current_chunk)
                )

            current_chunk = words

    if current_chunk:
        chunks.append(
            " ".join(current_chunk)
        )

    return chunks


# ==========================================
# AI Text Detection
# ==========================================

def detect_ai_text(text):

    if not text or not text.strip():

        return {
            "ai_percentage": 0.0,
            "human_percentage": 0.0
        }

    chunks = split_text(text)

    total_ai_score = 0.0
    total_human_score = 0.0

    # Get the labels from our trained model
    human_label = model.config.id2label[0].upper()
    ai_label = model.config.id2label[1].upper()

    for chunk in chunks:

        results = detector(chunk)

        scores = results[0]

        ai_score = 0.0
        human_score = 0.0

        for result in scores:

            label = result["label"].upper()
            score = float(result["score"])

            if label == ai_label:
                ai_score = score

            elif label == human_label:
                human_score = score

        total_ai_score += ai_score
        total_human_score += human_score

    number_of_chunks = len(chunks)

    ai_percentage = (
        total_ai_score / number_of_chunks
    ) * 100

    human_percentage = (
        total_human_score / number_of_chunks
    ) * 100

    # Normalize to exactly 100%
    total = ai_percentage + human_percentage

    if total > 0:

        ai_percentage = (
            ai_percentage / total
        ) * 100

        human_percentage = (
            human_percentage / total
        ) * 100

    # ==========================================
# Final Classification
# ==========================================

    if ai_percentage >= 75:
        classification = "Likely AI-generated"

    elif ai_percentage <= 25:
        classification = "Likely Human-written"

    else:
        classification = "Uncertain"


    return {
        "ai_percentage": round(ai_percentage, 2),
    "human_percentage": round(human_percentage, 2),
    "classification": classification
}


# ==========================================
# Local Test
# ==========================================

if __name__ == "__main__":

    sample_text = """
    Artificial intelligence is changing the way
    people learn and work. Technology is becoming
    an important part of modern education.
    Students use digital tools to improve their
    learning experience.
    """

    result = detect_ai_text(sample_text)

    print(
        "AI Generated:",
        result["ai_percentage"],
        "%"
    )

    print(
        "Human Written:",
        result["human_percentage"],
        "%"
    )