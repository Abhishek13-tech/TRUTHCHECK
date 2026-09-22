from ddgs import DDGS

def search_web_sources(text, max_results=5):
    """
    Search the web using exact phrase and normal context queries.
    """

    if not text or not text.strip():
        return []

    words = text.strip().split()

    if len(words) > 12:
        exact_phrase = " ".join(words[:12])
        normal_query = " ".join(words[:40])
    else:
        exact_phrase = " ".join(words)
        normal_query = " ".join(words)

    exact_query = f'"{exact_phrase}"'
    search_limit = min(max_results, 3)

    results = []
    seen_urls = set()

    try:
        with DDGS() as ddgs:

            # Exact phrase search
            exact_results = ddgs.text(
                exact_query,
                max_results=search_limit
            )

            # Normal context search
            normal_results = ddgs.text(
                normal_query,
                max_results=search_limit
            )

            all_results = list(exact_results) + list(normal_results)

            for item in all_results:

                url = item.get("href", "")

                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)

                results.append({
                    "title": item.get("title", ""),
                    "url": url,
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

        # Limit very large webpages to reduce processing time
        text = text[:30000]

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
            "similarity": float(similarity_result["similarity"]),
            "status": similarity_result["status"]
        }

        if current_match["similarity"] > 0:
            if (
                best_match is None
                or current_match["similarity"]
                > best_match["similarity"]
            ):
                best_match = current_match
    return best_match