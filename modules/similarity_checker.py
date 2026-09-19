from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re


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

    similarity_percentage = round(float(similarity) * 100, 2)

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


def normalize_words(text):
    """
    Convert text into clean lowercase words.
    """

    text = text.lower()

    words = re.findall(r"\b[a-z0-9]+\b", text)

    # Remove very common words
    stop_words = {
        "the", "is", "a", "an", "and", "or",
        "to", "of", "in", "on", "for", "with",
        "this", "that", "it", "my", "i", "are",
        "was", "were", "be", "as", "by", "from"
    }

    return [
        word for word in words
        if word not in stop_words
    ]


def calculate_lexical_similarity(user_text, webpage_text):
    """
    Calculate actual word overlap between user text
    and webpage text.
    """

    user_words = normalize_words(user_text)
    page_words = normalize_words(webpage_text)

    if not user_words or not page_words:
        return 0.0

    user_set = set(user_words)
    page_set = set(page_words)

    common_words = user_set.intersection(page_set)

    word_overlap = len(common_words) / len(user_set)

    # Create 3-word phrases
    user_ngrams = set(
        zip(user_words, user_words[1:], user_words[2:])
    )

    page_ngrams = set(
        zip(page_words, page_words[1:], page_words[2:])
    )

    if user_ngrams:
        common_ngrams = user_ngrams.intersection(page_ngrams)
        phrase_overlap = len(common_ngrams) / len(user_ngrams)
    else:
        phrase_overlap = 0.0

    # Give more importance to exact phrase overlap
    lexical_score = (
        (word_overlap * 0.4) +
        (phrase_overlap * 0.6)
    )

    return lexical_score


def calculate_web_similarity(user_text, webpage_text):
    """
    Calculate web similarity using both:
    1. Semantic similarity
    2. Actual word/phrase overlap

    This helps reduce false positives.
    """

    if not user_text or not webpage_text:
        return {
            "similarity": 0.0,
            "status": "No match"
        }

    # Split webpage into chunks
    words = webpage_text.split()

    chunk_size = 100
    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        if chunk.strip():
            chunks.append(chunk)

    if not chunks:
        return {
            "similarity": 0.0,
            "status": "No match"
        }

    # Create embeddings
    user_embedding = model.encode(
        [user_text],
        normalize_embeddings=True
    )

    chunk_embeddings = model.encode(
        chunks,
        batch_size=32,
        normalize_embeddings=True
    )

    # Semantic similarity
    semantic_scores = cosine_similarity(
        user_embedding,
        chunk_embeddings
    )[0]

    best_result = None

    for index, semantic_score in enumerate(semantic_scores):

        chunk = chunks[index]

        lexical_score = calculate_lexical_similarity(
            user_text,
            chunk
        )

        # Convert semantic score to percentage
        semantic_percentage = float(semantic_score) * 100

        lexical_percentage = lexical_score * 100

        # Combined score
        combined_score = (
            (semantic_score * 0.6) +
            (lexical_score * 0.4)
        )

        # If there is almost no actual word/phrase overlap,
        # don't allow semantic similarity to create a false match.
        if lexical_score < 0.10:

            final_score = 0.0
            status = "No strong match"

        else:

            final_score = combined_score * 100

            if (
                semantic_percentage >= 80
                and lexical_percentage >= 30
            ):
                status = "Strong match"

            elif (
                semantic_percentage >= 65
                and lexical_percentage >= 15
            ):
                status = "Possible match"

            else:
                status = "No strong match"
            if status == "No strong match":
                final_score = 0.0

        current_result = {
            "similarity": round(final_score, 2),
            "status": status
        }

        # Keep the best result
        if (
            best_result is None
            or current_result["similarity"]
            > best_result["similarity"]
        ):
            best_result = current_result

    return best_result