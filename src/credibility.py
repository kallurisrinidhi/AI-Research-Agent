
from urllib.parse import urlparse
import re


def calculate_credibility(topic, source):
    """
    Calculate a heuristic source-quality score.
    This score is not a verification of factual accuracy.
    """

    score = 0
    reasons = []

    url = source.get("url", "")
    content = source.get("content", "")
    title = source.get("title", "")

    # 1. Check domain type
    domain = urlparse(url).netloc.lower()
    domain = domain.replace("www.", "")

    if domain.endswith(".gov") or ".gov." in domain:
        score += 30
        reasons.append("Government domain")

    elif domain.endswith(".edu") or ".edu." in domain:
        score += 30
        reasons.append("Educational domain")

    elif domain.endswith(".org"):
        score += 20
        reasons.append("Organization domain")

    elif domain.endswith(".com"):
        score += 15
        reasons.append("Commercial domain")

    else:
        score += 10
        reasons.append("Other domain type")

    # 2. Check topic relevance using keyword overlap
    topic_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", topic.lower()))
    source_text = f"{title} {content}".lower()

    matched_words = [
        word for word in topic_words if word in source_text
    ]

    if topic_words:
        relevance = len(matched_words) / len(topic_words)
    else:
        relevance = 0

    relevance_points = int(relevance * 40)
    score += relevance_points

    reasons.append(
        f"Topic keyword match: {relevance_points}/40"
    )

    # 3. Check content availability
    content_length = len(content.strip())

    if content_length >= 1000:
        score += 20
        reasons.append("Detailed content available")

    elif content_length >= 300:
        score += 15
        reasons.append("Moderate content available")

    elif content_length >= 100:
        score += 10
        reasons.append("Limited content available")

    else:
        score += 5
        reasons.append("Very limited content available")

    # 4. Check source information completeness
    if title.strip():
        score += 5
        reasons.append("Title available")

    if url.startswith("https://"):
        score += 5
        reasons.append("HTTPS connection")

    score = min(score, 100)

    # Assign quality labels
    if score >= 75:
        label = "Higher Quality Signals"

    elif score >= 50:
        label = "Moderate Quality Signals"

    else:
        label = "Limited Quality Signals"

    return {
        "score": score,
        "label": label,
        "domain": domain,
        "reasons": reasons
    }


def evaluate_sources(topic, sources):
    """
    Evaluate all research sources and return updated results.
    """

    evaluated_sources = []

    for source in sources:
        result = source.copy()

        credibility = calculate_credibility(topic, source)

        result["credibility_score"] = credibility["score"]
        result["credibility_label"] = credibility["label"]
        result["credibility_domain"] = credibility["domain"]
        result["credibility_reasons"] = credibility["reasons"]

        evaluated_sources.append(result)

    return evaluated_sources


if __name__ == "__main__":

    sample_topic = "Artificial Intelligence in Healthcare"

    sample_sources = [
        {
            "title": "AI in Healthcare",
            "url": "https://example.edu/ai-healthcare",
            "content": (
                "Artificial intelligence is transforming healthcare "
                "through medical imaging, diagnosis and patient care."
                * 15
            )
        }
    ]

    results = evaluate_sources(sample_topic, sample_sources)

    for source in results:
        print("Source:", source["title"])
        print("Score:", source["credibility_score"])
        print("Label:", source["credibility_label"])
        print("Reasons:", source["credibility_reasons"])
