# 🤖 AI Research Agent

An intelligent AI-powered research assistant that searches the web, analyzes information, evaluates source credibility, generates research reports, and answers questions using Retrieval-Augmented Generation (RAG).

Built using Python, Streamlit, Gemini, Groq, Tavily, FAISS, and Sentence Transformers.

## 🚀 Features

- **Web Research:** Collects relevant information from the internet using Tavily Search API.
- **AI-Powered Analysis:** Uses Google Gemini to generate structured research reports.
- **Automatic AI Fallback:** Switches to Groq when Gemini encounters quota, network, or server errors.
- **Source Credibility Evaluation:** Evaluates research sources using a heuristic credibility scoring system.
- **RAG-Based Question Answering:** Retrieves relevant documents using FAISS and generates context-aware answers.
- **Vector Database:** Stores research document embeddings using FAISS.
- **Research History:** Saves completed research records using SQLite.
- **PDF and TXT Reports:** Generates downloadable research reports.
- **Multi-Topic Knowledge Library:** Maintains separate knowledge bases for different research topics.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Streamlit | Interactive web interface |
| Google Gemini API | Primary AI analysis |
| Groq API | Backup AI provider |
| Tavily API | Web search |
| FAISS | Vector database and similarity search |
| Sentence Transformers | Text embeddings |
| NumPy | Numerical operations |
| SQLite | Research history storage |
| ReportLab | PDF report generation |
| python-dotenv | Environment variable management |

## 🏗️ Project Architecture

```text
                 USER
                   |
                   v
            STREAMLIT APP
                   |
                   v
             TAVILY SEARCH
                   |
                   v
            RESEARCH SOURCES
                   |
          +--------+--------+
          |                 |
          v                 v
     FAISS VECTOR       SOURCE
       DATABASE         EVALUATION
          |                 |
          v                 |
     DOCUMENT              |
     RETRIEVAL              |
          |                 |
          +--------+--------+
                   |
                   v
              AI ANALYSIS
                   |
             +-----+-----+
             |           |
             v           v
           GEMINI       GROQ
          PRIMARY      BACKUP
             |           |
             +-----+-----+
                   |
                   v
            RESEARCH REPORT
                   |
          +--------+--------+
          |                 |
          v                 v
       PDF / TXT        RAG ANSWERS
```

## 📂 Project Structure

```text
AI-Research-Agent/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── test_connections.py
│
├── src/
│   ├── __init__.py
│   ├── search.py
│   ├── researcher.py
│   ├── analyzer.py
│   ├── credibility.py
│   ├── rag.py
│   ├── database.py
│   └── report_generator.py
│
├── data/
├── reports/
└── vector_store/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/kallurisrinidhi/AI-Research-Agent.git
```

### 2. Navigate to the project folder

```bash
cd AI-Research-Agent
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Configure API keys

Create a `.env` file in the project root.

Add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Get API keys from:

- Gemini: https://aistudio.google.com/
- Groq: https://console.groq.com/keys
- Tavily: https://app.tavily.com/

**Important:** Never upload your `.env` file or expose your API keys publicly.

### 7. Run the application

```bash
streamlit run app.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

## 🧠 How RAG Works

This project uses Retrieval-Augmented Generation to answer questions based on collected research documents.

1. Research documents are collected through Tavily.
2. Sentence Transformers converts documents into numerical embeddings.
3. FAISS stores and indexes the embeddings.
4. User questions are converted into embeddings.
5. FAISS retrieves the most relevant documents.
6. Retrieved information is passed to the AI model.
7. Gemini or Groq generates an answer using the retrieved context.

## 📊 Example Use Cases

- Research applications of Generative AI in daily life.
- Explore Artificial Intelligence in healthcare.
- Understand emerging technologies and industry trends.
- Generate structured research reports.
- Ask questions about previously collected research documents.

## 🔐 Environment Variables

The application requires the following API credentials:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `GROQ_API_KEY` | Groq API key |
| `TAVILY_API_KEY` | Tavily search API key |

## ⚠️ Limitations

- AI-generated answers may contain inaccuracies and should be verified against original sources.
- Source credibility scores are heuristic indicators, not definitive fact-checking results.
- AI provider usage is subject to API rate limits.
- Local research history and generated files are stored in the application's filesystem.

## 🔮 Future Enhancements

- Advanced citation verification.
- Improved source quality evaluation.
- Conversational research memory.
- Advanced research analytics dashboard.
- Enhanced PDF report formatting.
- More AI model integrations.

## 👨‍💻 Author

**Kalluri Srinidhi Reddy**

B.Tech – Computer Science and Engineering (Artificial Intelligence and Machine Learning)

GitHub: https://github.com/kallurisrinidhi

LinkedIn: https://linkedin.com/in/srinidhi-reddy-729002265

## ⭐ Support

If you find this project useful, consider giving the repository a star on GitHub!