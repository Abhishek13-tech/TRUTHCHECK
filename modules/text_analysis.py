from .text_detector import detect_ai_text
from .similarity_checker import calculate_similarity
from .reference_loader import load_reference_texts


def analyze_text(user_text):
    """
    Analyze text for AI detection and similarity
    against all stored reference texts.
    """

    # AI detection
    ai_result = detect_ai_text(user_text)

    # Load reference texts automatically
    references = load_reference_texts()

    similarity_results = []

    # Compare user text with every reference
    for reference in references:

        result = calculate_similarity(
            user_text,
            reference["text"]
        )

        similarity_results.append({
            "filename": reference["filename"],
            "similarity": result["similarity"],
            "status": result["status"]
        })

    # Find highest similarity
    highest_match = None

    if similarity_results:
        highest_match = max(
            similarity_results,
            key=lambda x: x["similarity"]
        )

    return {
        "ai_detection": ai_result,
        "similarity_results": similarity_results,
        "highest_match": highest_match
    }


# Test
if __name__ == "__main__":

    user_text = """
    Artificial intelligence is changing the way people learn and work.
    """

    result = analyze_text(user_text)

    print("AI Detection:")
    print(result["ai_detection"])

    print("\nSimilarity Results:")

    for item in result["similarity_results"]:
        print(
            f"{item['filename']} -> "
            f"{item['similarity']}% -> "
            f"{item['status']}"
        )

    print("\nHighest Match:")
    print(result["highest_match"])