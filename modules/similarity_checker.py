from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load sentence embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(text1, text2):
    """
    Calculate semantic similarity between two texts.
    """

    if not text1 or not text2:
        return {
            "similarity": 0.0,
            "status": "No text provided"
        }

    embeddings = model.encode([text1, text2])

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    similarity_percentage = round(float(similarity )* 100, 2)

    # Classify similarity level
    if similarity_percentage >= 80:
        status = "High similarity"
    elif similarity_percentage >= 50:
        status = "Moderate similarity"
    else:
        status = "Low similarity"

    return {
        "similarity": similarity_percentage,
        "status": status
    }


# Test
if __name__ == "__main__":

    original_text = """
    Artificial intelligence is changing the way people learn and work.
    """

    copied_text = """
    AI is changing how people work and learn.
    """

    result = calculate_similarity(original_text, copied_text)

    print(f"Similarity: {result['similarity']}%")
    print(f"Status: {result['status']}")