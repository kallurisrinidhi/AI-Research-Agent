
import os
import re
import json

import faiss
import numpy as np

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Import automatic Gemini-to-Groq fallback
from src.analyzer import generate_ai_response


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(os.path.join(BASE_DIR, ".env"))

STORE_DIR = os.path.join(BASE_DIR, "vector_store")

os.makedirs(STORE_DIR, exist_ok=True)


# --------------------------------------------------
# 2. LOAD EMBEDDING MODEL
# --------------------------------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully!")


# --------------------------------------------------
# 3. GLOBAL VARIABLES
# --------------------------------------------------

faiss_index = None

research_documents = []

current_topic = None

last_retrieved_sources = []


# --------------------------------------------------
# 4. TOPIC FOLDER
# --------------------------------------------------

def get_topic_folder(topic):

    folder_name = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        topic.lower()
    ).strip("_")

    folder_name = folder_name[:80] or "research"

    return os.path.join(STORE_DIR, folder_name)


# --------------------------------------------------
# 5. BUILD KNOWLEDGE BASE
# --------------------------------------------------

def build_knowledge_base(sources, topic="general"):

    global faiss_index
    global research_documents
    global current_topic
    global last_retrieved_sources

    research_documents = []

    last_retrieved_sources = []

    print("\nPreparing research documents...")

    for source in sources:

        title = source.get("title", "")

        content = source.get("content", "")

        url = source.get("url", "")

        if content and content.strip():

            document = (
                f"Title: {title}\n"
                f"Content: {content}\n"
                f"Source URL: {url}"
            )

            research_documents.append(document)

    if not research_documents:

        raise ValueError(
            "No research documents available."
        )

    print("Total documents:", len(research_documents))

    print("\nGenerating embeddings...")

    embeddings = embedding_model.encode(
        research_documents,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    faiss_index = faiss.IndexFlatIP(
        embeddings.shape[1]
    )

    faiss_index.add(embeddings)

    current_topic = topic

    topic_folder = get_topic_folder(topic)

    os.makedirs(topic_folder, exist_ok=True)

    index_path = os.path.join(
        topic_folder,
        "research.index"
    )

    documents_path = os.path.join(
        topic_folder,
        "documents.json"
    )

    faiss.write_index(
        faiss_index,
        index_path
    )

    with open(
        documents_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            research_documents,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\nKnowledge base created successfully!")

    print("Research topic:", topic)

    print("FAISS index saved:", index_path)

    print("Documents saved:", documents_path)


# --------------------------------------------------
# 6. LOAD KNOWLEDGE BASE
# --------------------------------------------------

def load_knowledge_base(topic="general"):

    global faiss_index
    global research_documents
    global current_topic
    global last_retrieved_sources

    topic_folder = get_topic_folder(topic)

    index_path = os.path.join(
        topic_folder,
        "research.index"
    )

    documents_path = os.path.join(
        topic_folder,
        "documents.json"
    )

    if not os.path.exists(index_path):

        print("Saved FAISS index not found.")

        return False

    if not os.path.exists(documents_path):

        print("Saved documents not found.")

        return False

    print("\nLoading knowledge base:", topic)

    loaded_index = faiss.read_index(index_path)

    with open(
        documents_path,
        "r",
        encoding="utf-8"
    ) as file:

        loaded_documents = json.load(file)

    if loaded_index.ntotal != len(loaded_documents):

        print("Index and document count mismatch.")

        return False

    faiss_index = loaded_index

    research_documents = loaded_documents

    current_topic = topic

    last_retrieved_sources = []

    print("Knowledge base loaded successfully!")

    print("Total documents:", len(research_documents))

    return True


# --------------------------------------------------
# 7. LIST SAVED TOPICS
# --------------------------------------------------

def get_saved_topics():

    topics = []

    if not os.path.exists(STORE_DIR):

        return topics

    for folder in os.listdir(STORE_DIR):

        folder_path = os.path.join(
            STORE_DIR,
            folder
        )

        if not os.path.isdir(folder_path):

            continue

        index_path = os.path.join(
            folder_path,
            "research.index"
        )

        documents_path = os.path.join(
            folder_path,
            "documents.json"
        )

        if (
            os.path.exists(index_path)
            and os.path.exists(documents_path)
        ):

            topics.append(folder)

    return sorted(topics)


# --------------------------------------------------
# 8. RETRIEVE DOCUMENTS WITH SCORES
# --------------------------------------------------

def retrieve_with_scores(question, top_k=3):

    if faiss_index is None:

        raise ValueError(
            "Load a knowledge base first."
        )

    if not research_documents:

        return []

    print("\nRetrieving relevant information...")

    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    question_embedding = np.asarray(
        question_embedding,
        dtype="float32"
    )

    k = min(
        top_k,
        len(research_documents)
    )

    scores, indices = faiss_index.search(
        question_embedding,
        k
    )

    results = []

    for score, index in zip(
        scores[0],
        indices[0]
    ):

        if index < 0:

            continue

        document = research_documents[index]

        title_match = re.search(
            r"Title:\s*(.*)",
            document
        )

        url_match = re.search(
            r"Source URL:\s*(.*)",
            document
        )

        title = (
            title_match.group(1).strip()
            if title_match
            else "Unknown Source"
        )

        url = (
            url_match.group(1).strip()
            if url_match
            else "URL unavailable"
        )

        results.append({

            "citation_id": len(results) + 1,

            "title": title,

            "url": url,

            "content": document,

            "similarity_score": float(score)

        })

    return results


# --------------------------------------------------
# 9. GET LAST RETRIEVED SOURCES
# --------------------------------------------------

def get_last_retrieved_sources():

    return last_retrieved_sources


# --------------------------------------------------
# 10. RETRIEVE INFORMATION
# --------------------------------------------------

def retrieve_information(question, top_k=3):

    results = retrieve_with_scores(
        question,
        top_k
    )

    return [
        result["content"]
        for result in results
    ]


# --------------------------------------------------
# 11. GENERATE ANSWER WITH CITATIONS
# --------------------------------------------------

def answer_question(question):

    global last_retrieved_sources

    try:

        # Retrieve relevant documents from FAISS
        retrieved_results = retrieve_with_scores(
            question,
            top_k=3
        )

        last_retrieved_sources = retrieved_results

        if not retrieved_results:

            return "No relevant research information found."

        # Prepare research context
        context_parts = []

        for result in retrieved_results:

            context_parts.append(
                f"""
Source [{result['citation_id']}]
Title: {result['title']}
URL: {result['url']}
Content: {result['content']}
"""
            )

        context = "\n\n".join(context_parts)

        # Prepare AI prompt
        prompt = f"""
You are an AI research assistant.

Answer the user's question using the research context below.

IMPORTANT RULES:

1. Use the provided research documents.
2. Add citation numbers such as [1], [2] after relevant claims.
3. Do not invent sources or URLs.
4. If information is insufficient, clearly mention it.
5. Give a clear and informative answer.
6. Do not claim that sources prove anything they do not support.

Research Topic:
{current_topic}

Research Context:
{context}

User Question:
{question}

Provide a clear answer with appropriate citations.
"""

        print("\nGenerating answer using AI providers...")

        # Gemini first, Groq automatically as backup
        answer = generate_ai_response(prompt)

        return answer

    except Exception as error:

        print(
            "RAG answer generation failed:",
            error
        )

        return f"Unable to generate answer: {error}"


# --------------------------------------------------
# 12. TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\nSaved Research Topics:")

    for topic in get_saved_topics():

        print("-", topic)

    sample_topic = "ai_in_healthcare"

    if load_knowledge_base(sample_topic):

        question = (
            "What are the applications of AI in healthcare?"
        )

        print("\nQuestion:", question)

        answer = answer_question(question)

        print("\nAI Answer:")

        print(answer)

        print("\nRetrieved Sources:")

        for source in get_last_retrieved_sources():

            print("\nTitle:", source["title"])

            print("URL:", source["url"])

            print(
                "Similarity Score:",
                round(source["similarity_score"], 4)
            )

    else:

        print(
            "Please create the healthcare knowledge base first."
        )
