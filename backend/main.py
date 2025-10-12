from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import os
import shutil
import requests
import arxiv

from .controller_agent import handle_query
from .utils.config import (
    LOGS_DIR,
    SAMPLE_PDFS_DIR,
    MAX_PDF_SIZE_MB,
    ALLOWED_UPLOAD_EXTENSIONS,
    SERPAPI_KEY,
    GROQ_API_KEY,
)
from .utils.logger import append_log

app = FastAPI(title="Multi-Agent Controller API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Environment Check Endpoint
@app.get("/check_env")
def check_environment():
    """Check external integrations (Groq, SerpAPI, ArXiv)."""
    report = {}

    # Groq API Check
    if GROQ_API_KEY:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                timeout=10,
            )
            if resp.status_code == 200:
                report["Groq_API"] = " Connected successfully"
            else:
                report["Groq_API"] = f" Error {resp.status_code}: {resp.text[:100]}"
        except Exception as e:
            report["Groq_API"] = f" Failed: {e}"
    else:
        report["Groq_API"] = " Missing GROQ_API_KEY"

    # SerpAPI Check 
    if SERPAPI_KEY:
        try:
            from serpapi import GoogleSearch
            search = GoogleSearch({"q": "test", "api_key": SERPAPI_KEY})
            res = search.get_dict()
            if "organic_results" in res:
                report["SerpAPI"] = " Working"
            else:
                report["SerpAPI"] = " Key loaded, but no search results"
        except Exception as e:
            report["SerpAPI"] = f" Failed: {e}"
    else:
        report["SerpAPI"] = " Missing SERPAPI_KEY"

    # ArXiv Check 
    try:
        search = arxiv.Search(query="AI", max_results=1)
        if next(search.results(), None):
            report["ArXiv"] = " Working"
        else:
            report["ArXiv"] = " No results"
    except Exception as e:
        report["ArXiv"] = f" Failed: {e}"

    return report


# File upload endpoint
UPLOAD_DIR = Path(SAMPLE_PDFS_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Handle PDF upload and store it in sample directory."""
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_PDF_SIZE_MB:
        raise HTTPException(
            status_code=400, detail=f"File too large. Max {MAX_PDF_SIZE_MB} MB."
        )

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    saved_path = UPLOAD_DIR / filename
    with open(saved_path, "wb") as f:
        f.write(contents)

    append_log(f"Saved uploaded PDF to {saved_path}")
    return JSONResponse(
        {"status": "ok", "filename": file.filename, "saved_path": str(saved_path)}
    )

# Main query endpoint
@app.post("/ask")
async def ask(payload: dict):
    """Main query endpoint for controller orchestration."""
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="query is required.")

    uploaded_pdf_path = payload.get("uploaded_pdf_path")
    result = handle_query(query, uploaded_pdf_path)
    return JSONResponse(result)



# Logs endpoints
@app.get("/logs")
def list_logs():
    p = Path(LOGS_DIR)
    files = [str(x.name) for x in p.glob("*") if x.is_file()]
    return {"logs": files}


@app.get("/logs/{filename}")
def get_log(filename: str):
    p = Path(LOGS_DIR) / filename
    if not p.exists():
        raise HTTPException(status_code=404, detail="Log not found")
    return FileResponse(str(p))
