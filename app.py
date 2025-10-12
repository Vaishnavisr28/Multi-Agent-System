import streamlit as st
import requests
import os
from requests.exceptions import ConnectionError, Timeout
import subprocess
import threading

def run_backend():
    subprocess.Popen(["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"])

threading.Thread(target=run_backend, daemon=True).start()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Multi-Agent System Demo", layout="wide")
st.title("Multi-Agent System - Demo")
st.caption("Upload a PDF, ask a question, and the backend will decide which agent(s) to use.")

with st.sidebar:
    st.header("Settings")
    backend = st.text_input("Backend URL", BACKEND_URL)
    if st.button("Reconnect"):
        st.experimental_rerun()


# Main UI
uploaded_file = st.file_uploader(" Upload a PDF (optional)", type=["pdf"])

default_query = "Summarize this PDF" if uploaded_file else "Show me the latest AI research papers"
query = st.text_input(" Ask a question:", value=default_query)

if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a query first.")
        st.stop()

    uploaded_pdf_path = None

    
    # Upload PDF to backend
    
    if uploaded_file:
        st.info(f"Uploading `{uploaded_file.name}` to backend...")
        try:
            upload_resp = requests.post(
                f"{backend}/upload_pdf",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                timeout=30
            )
            if upload_resp.status_code == 200:
                upload_json = upload_resp.json()
                uploaded_pdf_path = upload_json.get("saved_path")
                st.success(f" Uploaded `{uploaded_file.name}` successfully!")
            else:
                st.error(f" Upload failed: {upload_resp.status_code}")
                st.json(upload_resp.text)
                st.stop()
        except (ConnectionError, Timeout):
            st.error(" Could not connect to backend. Make sure FastAPI is running on port 8000.")
            st.stop()
        except Exception as e:
            st.error(f" Unexpected error during upload: {e}")
            st.stop()

    
    # 2️ Send query to backend /ask

    st.info("Sending query to controller agent...")

    try:
        resp = requests.post(
            f"{backend}/ask",
            json={"query": query, "uploaded_pdf_path": uploaded_pdf_path},
            timeout=60
        )

        if resp.status_code == 200:
            out = resp.json()
            st.subheader("Final Answer")
            st.write(out.get("answer", "No answer received."))

            st.subheader("Agents Used")
            st.write(out.get("agents_used"))

            st.subheader("Controller Rationale")
            st.write(out.get("rationale"))

            st.subheader("Trace File")
            st.code(out.get("trace_file"))
        else:
            st.error(f"Backend error: {resp.status_code}")
            st.text(resp.text)

    except (ConnectionError, Timeout):
        st.error(" Could not connect to backend `/ask`. Is it running?")
    except Exception as e:
        st.error(f" Error while querying backend: {e}")
