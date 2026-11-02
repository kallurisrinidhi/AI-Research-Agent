import os
from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient

load_dotenv("D:/ai agent/AI-Research-Agent/.env")

gemini_key = os.getenv("GEMINI_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

if not gemini_key or not tavily_key:
    print("API keys missing. Check your .env file.")
    exit()

try:
    print("Testing Gemini...")
    client = genai.Client(api_key=gemini_key)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Explain AI in one sentence."
    )
    print("Gemini connected successfully!")
    print(response.text)

except Exception as e:
    print("Gemini error:", e)

try:
    print("\nTesting Tavily...")
    tavily = TavilyClient(api_key=tavily_key)

    results = tavily.search(
        query="Artificial Intelligence",
        max_results=2
    )

    print("Tavily connected successfully!")

    for result in results["results"]:
        print(result["title"])
        print(result["url"])

except Exception as e:
    print("Tavily error:", e)

