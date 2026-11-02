
from src.search import search_web


def conduct_research(topic, max_results=5):
    """
    Collect research information from internet sources.
    """

    print("\nStarting research...")
    print("Research topic:", topic)

    search_results = search_web(
        query=topic,
        max_results=max_results
    )

    research_data = {
        "topic": topic,
        "total_sources": len(search_results),
        "sources": search_results
    }

    print("\nResearch completed!")
    print("Total sources collected:", len(search_results))

    return research_data


if __name__ == "__main__":

    topic = "Applications of Generative AI in healthcare"

    research = conduct_research(topic)

    print("\n========== RESEARCH SUMMARY ==========")

    print("Topic:", research["topic"])
    print("Total sources:", research["total_sources"])

    for index, source in enumerate(research["sources"], start=1):
        print(f"\nSource {index}")
        print("Title:", source["title"])
        print("URL:", source["url"])
        print("Content:", source["content"][:250])
        print("-" * 50)
