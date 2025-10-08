import os
from pathlib import Path
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from typing import List, Dict
from .utils.config import RAG_INDEX_DIR, SAMPLE_PDFS_DIR, EMBEDDING_MODEL
from .utils.logger import append_log

EMB_MODEL = SentenceTransformer(EMBEDDING_MODEL)

def extract_text_from_pdf(path: str) -> str:
    """Extract text from each page and return combined text."""
    doc = fitz.open(path)
    pages = []
    for p in doc:
        text = p.get_text().strip()
        if text:
            pages.append(text)
    doc.close()
    return "\n\n".join(pages)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

def build_or_update_index(pdf_paths: List[str], index_name: str = "nebula_rag"):
    """Create FAISS index + metadata store from PDFs."""
    texts, meta = [], []

    for p in pdf_paths:
        text = extract_text_from_pdf(p)
        chunks = chunk_text(text)
        for idx, ch in enumerate(chunks):
            texts.append(ch)
            meta.append({"source": os.path.basename(p), "chunk_id": idx})

    append_log(f"Embedding {len(texts)} chunks for RAG.")
    embeddings = EMB_MODEL.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    idx_path = Path(RAG_INDEX_DIR) / f"{index_name}.index"
    faiss.write_index(index, str(idx_path))
    with open(Path(RAG_INDEX_DIR) / f"{index_name}_meta.pkl", "wb") as f:
        pickle.dump({"texts": texts, "meta": meta}, f)

    append_log(f"Saved RAG index to {idx_path}")
    return str(idx_path)

def load_index(index_name: str = "nebula_rag"):
    idx_path = Path(RAG_INDEX_DIR) / f"{index_name}.index"
    meta_path = Path(RAG_INDEX_DIR) / f"{index_name}_meta.pkl"

    if not idx_path.exists() or not meta_path.exists():
        sample_paths = [str(p) for p in Path(SAMPLE_PDFS_DIR).glob("*.pdf")]
        build_or_update_index(sample_paths, index_name=index_name)

    index = faiss.read_index(str(idx_path))
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)
    return index, meta

def query_rag(query: str, top_k: int = 5, index_name: str = "nebula_rag") -> Dict:
    """Return top_k text chunks for a query using FAISS."""
    index, meta = load_index(index_name)
    q_emb = EMB_MODEL.encode([query], convert_to_numpy=True)
    D, I = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(D[0], I[0]):
        results.append({
            "score": float(score),
            "text": meta["texts"][idx],
            "meta": meta["meta"][idx]
        })

    append_log(f"RAG query '{query}' returned {len(results)} results.")
    return {"query": query, "results": results}
