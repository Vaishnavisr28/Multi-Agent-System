## Multi-Agent AI System 

This app can:
- Ask questions about a PDF you upload (PDF agent)
- Search the web (Web search agent)
- Find research papers on arXiv (ArXiv agent)

You can run it as a Streamlit app (simple) or as a Flask API.

### 1) Streamlit
1. Create a Python 3.10+ virtual environment.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. (Optional) Set a GROQ API key if you want AI-written answers:
```bash
# PowerShell
$env:GROQ_API_KEY = "your_key_here"

# cmd
set GROQ_API_KEY=your_key_here
```
Without the key, the app still works and returns simple, readable answers.
4. Run Streamlit:
```bash
streamlit run app.py
```

### 2) Run Flask API 
```bash
python -m backend.flask
```
The server starts on port 5001.

### Folder structure
- `app.py`: Streamlit UI
- `backend/agents.py`: PDF, web search, and arXiv agents
- `backend/controller_agent.py`: Chooses which agent to use and builds the answer
- `backend/utilities.py`: Simple logger helper
- `backend/flask.py`: Flask API version

### Notes
- PDF processing uses PyMuPDF (`fitz`).
- Vector storage uses FAISS saved under `vector_stores/`.
- Logs are written to `logs/`.

