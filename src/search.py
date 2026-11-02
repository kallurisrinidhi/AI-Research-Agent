
import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# Get Tavily API key
api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise ValueError("Tavily API key is missing!")

# Create Tavily client
tavily_client = TavilyClient(api_key=api_key)


def search_web(query, max_results=5):
    """
    Search the internet for information about a topic.
    """

    print(f"\nSearching for: {query}")

    response = tavily_client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced"
    )

    results = []

    for item in response.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
            "score": item.get("score", 0)
        })

    return results


if __name__ == "__main__":

    topic = "Latest applications of Artificial Intelligence"

    results = search_web(topic)

    print("\n========== SEARCH RESULTS ==========")

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Content:", result["content"][:300])
        print("-" * 50)

