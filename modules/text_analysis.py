from .text_detector import detect_ai_text
from .web_source_finder import find_best_web_source


def analyze_text(user_text):
    """
    Complete text analysis:
    1. AI/Human detection
    2. Web source detection
    """

    if not user_text or not user_text.strip():
        return {
            "ai_detection": {
                "ai_percentage": 0.0,
                "human_percentage": 0.0
            },
            "web_source": None
        }

    # AI detection
    ai_result = detect_ai_text(user_text)

    # Web source detection
    web_source = find_best_web_source(user_text)

    return {
        "ai_detection": ai_result,
        "web_source": web_source
    }