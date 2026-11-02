
import os
import streamlit as st

try:
    for key in [
        "GEMINI_API_KEY",
        "GROQ_API_KEY",
        "TAVILY_API_KEY"
    ]:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass
import streamlit as st
from pathlib import Path

from src.researcher import conduct_research
from src.analyzer import analyze_research
from src.report_generator import generate_report, generate_pdf_report

from src.database import (
    create_database,
    save_research,
    get_research_history,
    get_research_by_id
)

from src.credibility import evaluate_sources

from src.rag import (
    build_knowledge_base,
    load_knowledge_base,
    answer_question,
    get_saved_topics,
    get_last_retrieved_sources
)


# ==================================================
# 1. INITIAL SETUP
# ==================================================

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🤖",
    layout="wide"
)

create_database()

defaults = {
    "analysis": None,
    "research_topic": "",
    "research_data": None,
    "evaluated_sources": [],
    "rag_answer": None,
    "rag_sources": [],
    "txt_path": None,
    "pdf_path": None,
    "analysis_saved": False,
    "analysis_error": None,
    "kb_ready": False,
    "selected_history_id": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# 2. HELPER FUNCTION: GENERATE ANALYSIS
# ==================================================

def run_analysis():

    research_data = st.session_state.research_data

    if not research_data:
        st.error("No research data available.")
        return

    try:

        with st.spinner("Gemini is analyzing your research..."):

            analysis = analyze_research(research_data)

        if not analysis:
            raise ValueError("Gemini returned an empty analysis.")

        st.session_state.analysis = analysis
        st.session_state.analysis_error = None

        # Save only once to prevent duplicate history records
        if not st.session_state.analysis_saved:

            save_research(
                st.session_state.research_topic,
                analysis,
                len(research_data.get("sources", []))
            )

            st.session_state.analysis_saved = True

        # Generate TXT and PDF reports
        with st.spinner("Generating PDF and TXT reports..."):

            txt_path = generate_report(
                st.session_state.research_topic,
                analysis
            )

            pdf_path = generate_pdf_report(
                st.session_state.research_topic,
                analysis
            )

        st.session_state.txt_path = str(txt_path)
        st.session_state.pdf_path = str(pdf_path)

        st.success("AI analysis and reports generated successfully!")

    except Exception as error:

        st.session_state.analysis_error = str(error)

        st.error(f"AI analysis failed: {error}")

        st.warning(
            "Your collected sources and FAISS knowledge base "
            "are preserved. You can retry the analysis."
        )


# ==================================================
# 3. APPLICATION HEADER
# ==================================================

st.title("🤖 AI Research Agent")

st.write(
    "An intelligent research assistant that searches the web, "
    "analyzes information using Gemini, evaluates sources, "
    "generates reports, and answers questions using RAG."
)

st.divider()


# ==================================================
# 4. RESEARCH HISTORY
# ==================================================

st.sidebar.title("📚 Research History")

history = get_research_history()

if history:

    history_options = {
        f"#{record[0]} | {record[1]} | {record[3]}": record[0]
        for record in history
    }

    selected_history = st.sidebar.selectbox(
        "Select Previous Research",
        options=list(history_options.keys()),
        key="history_selection"
    )

    if st.sidebar.button("View Previous Research"):

        research_id = history_options[selected_history]

        previous = get_research_by_id(research_id)

        if previous:

            st.session_state.analysis = previous[2]
            st.session_state.research_topic = previous[1]

            st.session_state.research_data = None
            st.session_state.evaluated_sources = []

            st.session_state.analysis_error = None
            st.session_state.analysis_saved = True

            st.session_state.txt_path = None
            st.session_state.pdf_path = None

            st.session_state.kb_ready = False

            st.session_state.rag_answer = None
            st.session_state.rag_sources = []

            st.session_state.selected_history_id = research_id

            st.rerun()

else:

    st.sidebar.info("No previous research available.")


# ==================================================
# 5. START NEW RESEARCH
# ==================================================

st.header("🔍 Start New Research")

topic = st.text_input(
    "Enter your research topic",
    placeholder="Example: Applications of Generative AI in Healthcare",
    key="new_research_topic"
)

if st.button("🚀 Start Research", type="primary"):

    if not topic.strip():

        st.warning("Please enter a research topic.")

    else:

        # Reset previous research state
        st.session_state.analysis = None
        st.session_state.research_data = None
        st.session_state.evaluated_sources = []

        st.session_state.analysis_error = None
        st.session_state.analysis_saved = False

        st.session_state.txt_path = None
        st.session_state.pdf_path = None

        st.session_state.kb_ready = False

        st.session_state.rag_answer = None
        st.session_state.rag_sources = []

        st.session_state.research_topic = topic
        st.session_state.selected_history_id = None

        try:

            # ------------------------------------------
            # STEP 1: TAVILY WEB SEARCH
            # ------------------------------------------

            with st.spinner("Searching the web using Tavily..."):

                research_data = conduct_research(
                    topic,
                    max_results=5
                )

            sources = research_data.get("sources", [])

            if not sources:

                st.error("No research sources were found.")

            else:

                st.session_state.research_data = research_data

                st.success(
                    f"Successfully collected {len(sources)} sources!"
                )

                # --------------------------------------
                # STEP 2: SOURCE CREDIBILITY
                # --------------------------------------

                evaluated_sources = evaluate_sources(
                    topic,
                    sources
                )

                st.session_state.evaluated_sources = evaluated_sources

                # --------------------------------------
                # STEP 3: SAVE FAISS KNOWLEDGE BASE
                # --------------------------------------

                with st.spinner("Creating FAISS knowledge base..."):

                    build_knowledge_base(
                        evaluated_sources,
                        topic
                    )

                st.session_state.kb_ready = True

                st.success(
                    "Research sources and knowledge base saved successfully!"
                )

        except Exception as error:

            st.error(f"Research collection failed: {error}")


# ==================================================
# 6. AUTOMATIC GEMINI ANALYSIS
# ==================================================

if (
    st.session_state.research_data
    and not st.session_state.analysis
    and not st.session_state.analysis_error
):

    run_analysis()


# ==================================================
# 7. RETRY GEMINI ANALYSIS
# ==================================================

if (
    st.session_state.research_data
    and not st.session_state.analysis
    and st.session_state.analysis_error
):

    st.warning(
        "Your research has been saved, but AI analysis "
        "could not be completed."
    )

    if st.button("🔄 Retry AI Analysis"):

        st.session_state.analysis_error = None

        run_analysis()


# ==================================================
# 8. DISPLAY RESEARCH ANALYSIS
# ==================================================

if st.session_state.analysis:

    st.divider()

    st.header("🧠 Research Analysis")

    st.write(
        "**Research Topic:**",
        st.session_state.research_topic
    )

    st.markdown(st.session_state.analysis)


# ==================================================
# 9. SOURCE CREDIBILITY
# ==================================================

if st.session_state.evaluated_sources:

    st.divider()

    st.header("📊 Source Credibility Evaluation")

    for index, source in enumerate(
        st.session_state.evaluated_sources,
        start=1
    ):

        with st.expander(
            f"Source {index}: {source.get('title', 'Untitled')}"
        ):

            st.write(
                "URL:",
                source.get("url", "Not available")
            )

            st.write(
                "Credibility Score:",
                source.get(
                    "credibility_score",
                    source.get("score", "Not available")
                )
            )

            st.write(
                "Credibility Level:",
                source.get(
                    "credibility_label",
                    source.get("credibility", "Not available")
                )
            )

            st.write(source.get("content", ""))


# ==================================================
# 10. DOWNLOAD RESEARCH REPORTS
# ==================================================

if st.session_state.txt_path or st.session_state.pdf_path:

    st.divider()

    st.header("📄 Download Research Reports")

    col1, col2 = st.columns(2)

    if st.session_state.txt_path:

        txt_path = Path(st.session_state.txt_path)

        if txt_path.exists():

            with col1:

                with open(txt_path, "rb") as file:

                    st.download_button(
                        "⬇️ Download TXT Report",
                        data=file.read(),
                        file_name=txt_path.name,
                        mime="text/plain"
                    )

    if st.session_state.pdf_path:

        pdf_path = Path(st.session_state.pdf_path)

        if pdf_path.exists():

            with col2:

                with open(pdf_path, "rb") as file:

                    st.download_button(
                        "⬇️ Download PDF Report",
                        data=file.read(),
                        file_name=pdf_path.name,
                        mime="application/pdf"
                    )


# ==================================================
# 11. SAVED KNOWLEDGE LIBRARY
# ==================================================

st.divider()

st.header("📚 Saved Research Knowledge Library")

saved_topics = get_saved_topics()

if saved_topics:

    if (
        "selected_kb_topic" not in st.session_state
        or st.session_state.selected_kb_topic not in saved_topics
    ):

        st.session_state.selected_kb_topic = saved_topics[-1]

    selected_topic = st.selectbox(
        "Choose a saved research topic",
        options=saved_topics,
        format_func=lambda value: value.replace("_", " ").title(),
        key="selected_kb_topic"
    )

    if st.button("Load Knowledge Base"):

        try:

            with st.spinner("Loading knowledge base..."):

                load_knowledge_base(selected_topic)

            st.session_state.kb_ready = True

            st.success(
                f"Knowledge base loaded: {selected_topic}"
            )

        except Exception as error:

            st.session_state.kb_ready = False

            st.error(f"Knowledge base error: {error}")

else:

    st.info(
        "No saved knowledge bases available. "
        "Start a research task to create one."
    )


# ==================================================
# 12. ASK AI USING RAG
# ==================================================

st.divider()

st.header("💬 Ask AI About Your Research")

st.write(
    "Ask questions based on your saved research documents."
)

if saved_topics:

    question = st.text_input(
        "Enter your question",
        placeholder="Example: What are the applications of AI in healthcare?",
        key="rag_question"
    )

    if st.button("Ask AI"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            try:

                with st.spinner(
                    "Retrieving information and generating answer..."
                ):

                    load_knowledge_base(selected_topic)

                    answer = answer_question(question)

                    retrieved_sources = get_last_retrieved_sources()

                    st.session_state.rag_answer = answer
                    st.session_state.rag_sources = retrieved_sources

            except Exception as error:

                st.error(f"Question answering error: {error}")

else:

    st.info("Create a knowledge base before asking questions.")


# ==================================================
# 13. DISPLAY AI ANSWER AND REFERENCES
# ==================================================

if st.session_state.rag_answer:

    st.subheader("🤖 AI Answer")

    st.markdown(st.session_state.rag_answer)

    st.subheader("🔗 Retrieved Sources and References")

    if st.session_state.rag_sources:

        for source in st.session_state.rag_sources:

            with st.expander(
                f"Source {source.get('citation_id', '')}: "
                f"{source.get('title', 'Research Source')}"
            ):

                url = source.get("url", "")

                if url:

                    st.markdown(f"[Open Source]({url})")

                st.write(
                    "Similarity Score:",
                    round(
                        source.get("similarity_score", 0),
                        4
                    )
                )

                st.write(source.get("content", ""))

    else:

        st.info("No source references were returned.")


# ==================================================
# 14. FOOTER
# ==================================================

st.divider()

st.caption(
    "AI Research Agent | Built using Python, Streamlit, "
    "Gemini, Tavily, FAISS, and RAG."
)

