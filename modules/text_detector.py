from transformers import pipeline
import re


# Load AI text detection model
detector = pipeline(
    "text-classification",
    model="rasbt/ai-text-detector-distilbert",
    top_k=None
)


def split_text(text, max_words=80):
    """
    Split long text into smaller chunks.
    """

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    chunks = []
    current_chunk = []

    for sentence in sentences:

        words = sentence.split()

        if len(current_chunk) + len(words) <= max_words:
            current_chunk.extend(words)
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            current_chunk = words

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def detect_ai_text(text):
    """
    Detect AI-generated and human-written percentages.
    """

    if not text or not text.strip():
        return {
            "ai_percentage": 0.0,
            "human_percentage": 0.0
        }

    chunks = split_text(text)

    total_ai_score = 0.0
    total_human_score = 0.0

    for chunk in chunks:

        results = detector(chunk)

        scores = results[0]

        ai_score = 0.0
        human_score = 0.0

        for result in scores:

            label = result["label"].upper()
            score = float(result["score"])

            if "AI" in label:
                ai_score = score

            elif "HUMAN" in label:
                human_score = score

        # Fallback if only one score is returned
        if ai_score == 0.0 and human_score > 0.0:
            ai_score = 1.0 - human_score

        elif human_score == 0.0 and ai_score > 0.0:
            human_score = 1.0 - ai_score

        total_ai_score += ai_score
        total_human_score += human_score

    number_of_chunks = len(chunks)

    ai_percentage = (
        total_ai_score / number_of_chunks
    ) * 100

    human_percentage = (
        total_human_score / number_of_chunks
    ) * 100

    # Make sure total is exactly 100%
    total = ai_percentage + human_percentage

    if total > 0:
        ai_percentage = (
            ai_percentage / total
        ) * 100

        human_percentage = (
            human_percentage / total
        ) * 100

    return {
        "ai_percentage": round(ai_percentage, 2),
        "human_percentage": round(human_percentage, 2)
    }


# Test
if __name__ == "__main__":

    sample_text = """
    Artificial intelligence is changing the way people learn and work.
    Technology is becoming an important part of modern education.
    Students use digital tools to improve their learning experience.
    """

    result = detect_ai_text(sample_text)

    print("AI Generated:", result["ai_percentage"], "%")
    print("Human Written:", result["human_percentage"], "%")