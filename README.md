Multi-Agent Research Assistant
Overview:

This project is a modular multi-agent system designed for NebulaByte Technologies to automate AI research assistance tasks such as PDF summarization, web search, and academic paper retrieval.
It integrates FastAPI (backend) and Streamlit (frontend) to create an interactive interface for users to upload PDFs, query research topics, and visualize AI-driven insights.

Key Features:

Controller Agent (Decision Maker):
Dynamically routes user queries to appropriate agents (PDF RAG, Web Search, or ArXiv) using rule-based logic.
Logs all decisions, rationale, and trace files.

PDF RAG Agent:
Extracts, chunks, embeds, and retrieves relevant passages from research PDFs using FAISS and SentenceTransformers.
Provides concise contextual answers or summaries.

Web Search Agent:
Performs live searches using SerpAPI or Google Gemini to fetch the latest AI developments, papers, and news.

ArXiv Agent:
Fetches the latest academic papers from ArXiv.org and summarizes them for easy review.

Frontend:
Built using Streamlit for interactive user experience — allowing PDF uploads, query input, and displaying logs or summaries.

Tech Stack:
Layer	Technology
Frontend	Streamlit
Backend	FastAPI
Vector Search	FAISS
Embeddings	SentenceTransformers
LLM API	Gemini / Groq (configurable)
Web Search	SerpAPI
Research Papers	ArXiv API
Language	Python 3.10+

Project Structure:
Solar_assignment/
│
├── backend/
│   ├── main.py                 # FastAPI backend
│   ├── controller_agent.py     # Core controller logic
│   ├── pdf_rag_agent.py        # PDF retrieval + summarization
│   ├── web_search_agent.py     # Web Search via SerpAPI
│   ├── arxiv_agent.py          # ArXiv integration
│   ├── utils/
│   │   ├── config.py           # API keys & paths
│   │   ├── logger.py           # Logging system
│   │   └── llm_model.py        # Gemini or Groq LLM wrapper
│   └── logs/                   # Auto-generated logs/traces
│
├── app.py                      # Streamlit frontend
├── sample_pdfs/                # Curated NebulaByte PDFs for RAG demo
├── requirements.txt            # Dependencies
└── README.md                   # Project documentation

Installation & Setup
1️ Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

2️ Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # for Windows
# OR
source venv/bin/activate  # for Mac/Linux

3️ Install dependencies
pip install -r requirements.txt

4️ Create a .env file

Include the following (replace with your actual keys):

GROQ_API_KEY=your_groq_api_key
SERPAPI_KEY=your_serpapi_key
BACKEND_URL=http://localhost:8000

Running the Application:
Start the backend (FastAPI):
python -m uvicorn backend.main:app --reload --port 8000

Start the frontend (Streamlit):
streamlit run app.py


Now open your browser at:

http://localhost:8501

Testing the System:

You can try queries like:

“Summarize this uploaded document.”

“Show me the latest AI research papers from ArXiv.”

“Recent projects by NebulaByte Technologies.”

“What are developments in quantum AI in 2025?”

Each response will generate a trace file in /logs detailing:

The decision logic

Agents used

Retrieved documents

Final synthesized answer

Deployment:

You can deploy this project using:

Render (recommended for FastAPI + Streamlit)

Hugging Face Spaces (Gradio/Streamlit mode)

Railway.app or Google Cloud Run

Each deployment should expose:

FastAPI backend (/ask, /upload_pdf, /logs, /check_env)

Streamlit frontend (app.py)

Deliverables:

 Modular multi-agent architecture
 Deployed demo link
 5 curated NebulaByte PDFs in sample_pdfs/
 Logs + trace files demonstrating routing logic
 Detailed REPORT.pdf explaining architecture
