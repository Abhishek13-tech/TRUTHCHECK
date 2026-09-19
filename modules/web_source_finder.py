from ddgs import DDGS

def search_web_sources(text, max_results=5):
    """
    Search the web for possible sources related to the given text.
    """

    if not text or not text.strip():
        return []

    # Use a shorter query for web search
    query = " ".join(text.strip().split()[:40])

    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=max_results
            )

            for item in search_results:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", "")
                })

    except Exception as error:
        print(f"Web search error: {error}")

    return results


# Test
if __name__ == "__main__":

    sample_text = """
    Artificial intelligence is transforming the way people learn
    and work in the modern world.
    """

    sources = search_web_sources(sample_text)

    for source in sources:
        print("\nTitle:", source["title"])
        print("URL:", source["url"])
        print("Snippet:", source["snippet"])
import requests
from bs4 import BeautifulSoup

def extract_webpage_text(url):
    """
    Extract the main readable content from a webpage.
    """

    if not url:
        return ""

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Try to find the main page content
        main_content = soup.find("main")

        if main_content:
            soup = main_content

        # Remove unnecessary elements
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "form",
            "table"
        ]):
            element.decompose()

        text = soup.get_text(" ", strip=True)

        return text

    except Exception as error:
        print(f"Page extraction error: {error}")
        return ""
from modules.similarity_checker import calculate_web_similarity


def find_best_web_source(user_text, max_results=5):
    """
    Search the web, extract webpage text,
    and find the best matching source.
    """

    search_results = search_web_sources(
        user_text,
        max_results=max_results
    )

    best_match = None

    for source in search_results:

        webpage_text = extract_webpage_text(
            source["url"]
        )

        if not webpage_text:
            continue

        similarity_result = calculate_web_similarity(
            user_text,
            webpage_text
        )

        current_match = {
            "title": source["title"],
            "url": source["url"],
            "similarity": similarity_result["similarity"],
            "status": similarity_result["status"]
        }

        if (
            best_match is None
            or current_match["similarity"]
            > best_match["similarity"]
        ):
            best_match = current_match

    return best_match