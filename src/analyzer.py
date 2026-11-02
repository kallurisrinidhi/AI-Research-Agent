
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from groq import Groq


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------
# 2. GEMINI CONFIGURATION
# --------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-3.8-flash"

gemini_client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY else None
)


# --------------------------------------------------
# 3. GROQ CONFIGURATION
# --------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = "openai/gpt-oss-20b"

groq_client = (
    Groq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY else None
)


# --------------------------------------------------
# 4. GENERATE RESPONSE USING GROQ
# --------------------------------------------------

def generate_groq_response(prompt):
    """
    Generate an AI response using Groq backup provider.
    """

    if not groq_client:

        raise RuntimeError(
            "Groq API key is missing. "
            "Check GROQ_API_KEY in your .env file."
        )

    print("\nSwitching to Groq backup AI provider...")

    response = groq_client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional AI research analyst. "
                    "Follow the user's instructions carefully. "
                    "Do not invent facts or references."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3,

        max_tokens=6000
    )

    answer = response.choices[0].message.content

    if not answer:

        raise RuntimeError(
            "Groq returned an empty response."
        )

    print("Groq response generated successfully!")

    return answer


# --------------------------------------------------
# 5. AUTOMATIC GEMINI TO GROQ FALLBACK
# --------------------------------------------------

def generate_ai_response(prompt):
    """
    Try Gemini first.

    If Gemini fails because of quota, network,
    connection, or server problems, automatically
    switch to Groq.
    """

    if gemini_client:

        for attempt in range(3):

            try:

                print(
                    f"\nSending request to Gemini "
                    f"(attempt {attempt + 1}/3)..."
                )

                response = gemini_client.models.generate_content(

                    model=GEMINI_MODEL,

                    contents=prompt
                )

                if response.text:

                    print(
                        "Gemini response generated successfully!"
                    )

                    return response.text

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            except Exception as error:

                error_message = str(error).upper()

                # ----------------------------------
                # DAILY QUOTA EXHAUSTED
                # ----------------------------------

                if any(word in error_message for word in [
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "QUOTA"
                ]):

                    print("\nGemini quota exhausted.")

                    print("Switching to Groq...")

                    break

                # ----------------------------------
                # NETWORK / CONNECTION ERRORS
                # ----------------------------------

                elif any(word in error_message for word in [
                    "WINERROR 10065",
                    "WINERROR 10060",
                    "WINERROR 10061",
                    "UNREACHABLE HOST",
                    "NETWORK IS UNREACHABLE",
                    "CONNECTION ERROR",
                    "CONNECTION RESET",
                    "CONNECTION REFUSED",
                    "CONNECTION ABORTED",
                    "TIMED OUT",
                    "TIMEOUT"
                ]):

                    print(
                        "\nGemini network connection failed."
                    )

                    print("Switching to Groq...")

                    break

                # ----------------------------------
                # TEMPORARY SERVER ERRORS
                # ----------------------------------

                elif (
                    "503" in error_message
                    or "UNAVAILABLE" in error_message
                ):

                    if attempt < 2:

                        wait_time = 2 ** (attempt + 1)

                        print(
                            f"\nGemini server is busy. "
                            f"Retrying in {wait_time} seconds..."
                        )

                        time.sleep(wait_time)

                    else:

                        print(
                            "\nGemini is still unavailable."
                        )

                        print("Switching to Groq...")

                # ----------------------------------
                # OTHER GEMINI ERRORS
                # ----------------------------------

                else:

                    print(
                        "\nGemini encountered an error:"
                    )

                    print(error)

                    print(
                        "Trying the Groq backup provider..."
                    )

                    break

    else:

        print(
            "\nGemini API key not found."
        )

        print("Trying Groq backup provider...")

    # ----------------------------------
    # GROQ BACKUP
    # ----------------------------------

    try:

        return generate_groq_response(prompt)

    except Exception as groq_error:

        raise RuntimeError(
            "Both AI providers failed.\n"
            f"Groq error: {groq_error}"
        ) from groq_error


# --------------------------------------------------
# 6. BACKWARD COMPATIBILITY
# --------------------------------------------------

def generate_gemini_response(prompt):

    return generate_ai_response(prompt)


# --------------------------------------------------
# 7. RESEARCH ANALYSIS
# --------------------------------------------------

def analyze_research(research_data):
    """
    Analyze research sources and generate
    numbered citations.
    """

    topic = research_data.get(
        "topic",
        "Unknown Topic"
    )

    sources = research_data.get(
        "sources",
        []
    )

    print("\nPreparing research analysis...")

    print("Research topic:", topic)

    print("Total sources:", len(sources))

    if not sources:

        raise ValueError(
            "No research sources available."
        )

    formatted_sources = []

    for index, source in enumerate(
        sources,
        start=1
    ):

        title = source.get(
            "title",
            "Untitled Source"
        )

        url = source.get(
            "url",
            "URL unavailable"
        )

        content = source.get(
            "content",
            ""
        )

        formatted_sources.append(
            f"""
SOURCE [{index}]
Title: {title}
URL: {url}
Content: {content}
"""
        )

    sources_text = "\n".join(
        formatted_sources
    )

    prompt = f"""
You are a professional AI research analyst.

Research Topic: {topic}

Analyze the following research sources carefully.

{sources_text}

INSTRUCTIONS:

1. Use only information supported by the provided sources.
2. Do not invent facts, statistics, or references.
3. Add numbered citations such as [1], [2], and [3]
   immediately after claims supported by those sources.
4. Make sure every citation number matches the source list.
5. If information is missing, clearly mention that.
6. Do not create fake URLs.
7. Write in clear, professional language.

GENERATE THE REPORT USING THIS STRUCTURE:

# Research Analysis: {topic}

## 1. Introduction
Introduce the research topic using supported information.

## 2. Key Findings
Explain the most important findings with numbered citations.

## 3. Important Applications
Describe applications supported by the sources.

## 4. Benefits
Explain the benefits with citations.

## 5. Challenges
Explain documented challenges. If the sources do not discuss them,
state that the available sources provide insufficient information.

## 6. Future Scope
Discuss future possibilities only when supported by the sources.

## 7. Conclusion
Summarize the research findings.

## 8. References

List every provided source in this exact format:

[1] Source Title - URL
[2] Source Title - URL

Include the actual source titles and URLs provided above.
Do not invent or modify them.
"""

    print("\nSending research for AI analysis...")

    analysis = generate_ai_response(prompt)

    return analysis


# --------------------------------------------------
# 8. TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTesting Research Analyzer...")

    sample_data = {

        "topic": "Artificial Intelligence in Healthcare",

        "sources": [

            {
                "title": "AI in Healthcare",

                "url": "https://example.com/ai-healthcare",

                "content": (
                    "Artificial intelligence helps healthcare "
                    "professionals analyze medical images."
                )
            },

            {
                "title": "Machine Learning in Diagnosis",

                "url": "https://example.com/ml-diagnosis",

                "content": (
                    "Machine learning identifies patterns "
                    "in medical data to support diagnosis."
                )
            }

        ]
    }

    try:

        result = analyze_research(sample_data)

        print("\nFINAL RESEARCH ANALYSIS:\n")

        print(result)

    except Exception as error:

        print("\nAnalysis failed:")

        print(error)
