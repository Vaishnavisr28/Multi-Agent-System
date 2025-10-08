import os
from dotenv import load_dotenv
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "GROQ")

# LLM API keys 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# SerpAPI 
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# ArXiv 
ARXIV_EMAIL = os.getenv("ARXIV_EMAIL")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SAMPLE_PDFS_DIR = os.path.join(BASE_DIR, "sample_pdfs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
RAG_INDEX_DIR = os.path.join(BASE_DIR, "rag_index")

# Limits & security
MAX_PDF_SIZE_MB = int(os.getenv("MAX_PDF_SIZE_MB", "10"))  
ALLOWED_UPLOAD_EXTENSIONS = {".pdf"}

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(RAG_INDEX_DIR, exist_ok=True)
