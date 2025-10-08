from typing import Dict, Any, List
from .pdf_rag_agent import query_rag
from .web_search_agent import web_search
from .arxiv_agent import query_arxiv
from .utils.logger import save_trace, append_log
from .utils.config import LLM_PROVIDER


def simple_rule_router(user_input: str, uploaded_pdf: bool = False) -> Dict[str, Any]:
    """
    Simple rule-based router:
      - If user uploads a PDF and asks 'summarize' -> PDF RAG
      - If mentions 'arxiv' or 'papers' -> ArXiv
      - If mentions 'recent' or 'latest' -> Web Search
      - Else: fallback to PDF RAG or Web Search
    """
    text = user_input.lower()
    agents = []
    rationale = []

    if uploaded_pdf and ("summarize" in text or "summary" in text):
        agents = ["pdf_rag"]
        rationale.append("User uploaded a PDF and asked for summary → use PDF RAG.")
    elif "arxiv" in text or "papers" in text:
        agents = ["arxiv"]
        rationale.append("Query mentions 'arxiv' or 'papers' → ArXiv agent selected.")
    elif "recent" in text or "latest" in text or "news" in text:
        agents = ["web_search"]
        rationale.append("Query mentions 'recent' or 'latest' → Web Search agent selected.")
    else:
        if uploaded_pdf:
            agents = ["pdf_rag"]
            rationale.append("PDF uploaded → use RAG to fetch relevant sections.")
        else:
            agents = ["web_search", "arxiv"]
            rationale.append("No PDF uploaded → use Web Search and ArXiv as fallback.")

    llm_note = f"LLM_PROVIDER={LLM_PROVIDER} (not used in this version)."
    rationale.append(llm_note)
    decision = {"agents": agents, "rationale": " ; ".join(rationale)}
    append_log(f"Router decision: {decision}")
    return decision


def handle_query(user_input: str, uploaded_pdf_path: str = None) -> Dict:
    """
    Main controller function — decides which agent(s) to call and combines their outputs.
    """
    uploaded_pdf = uploaded_pdf_path is not None
    decision = simple_rule_router(user_input, uploaded_pdf=uploaded_pdf)

    agents_called = {}
    documents_retrieved = []
    final_answer_parts: List[str] = []

    for agent in decision["agents"]:
        if agent == "pdf_rag" and uploaded_pdf:
            rag_res = query_rag(user_input)
            agents_called["pdf_rag"] = rag_res
            for r in rag_res["results"]:
                documents_retrieved.append({
                    "source": r["meta"]["source"],
                    "chunk_id": r["meta"]["chunk_id"]
                })
            # context for LLM
            context_parts = []
            for idx, r in enumerate(rag_res["results"][:3], 1):
                context_parts.append(f"[Excerpt {idx} from {r['meta']['source']}]:\n{r['text']}\n")
            context = "\n".join(context_parts)
            
            # LLM
            from .utils.llm_model import generate_summary
            summary = generate_summary(user_input, context=context)
            final_answer_parts.append(summary)

        elif agent == "web_search":
            web = web_search(user_input)
            agents_called["web_search"] = web
            for r in web.get("results", [])[:3]:
                documents_retrieved.append({
                    "source": "web",
                    "title": r.get("title"),
                    "link": r.get("link")
                })
            # web search context for LLM
            context_parts = []
            for r in web.get("results", [])[:3]:
                context_parts.append(f"[Web Result: {r.get('title')}]\n{r.get('snippet')}\nSource: {r.get('link')}\n")
            context = "\n".join(context_parts)
            
            # response using LLM
            from .utils.llm_model import generate_summary
            web_summary = generate_summary(user_input, context=context)
            final_answer_parts.append(web_summary)

        elif agent == "arxiv":
            arx = query_arxiv(user_input)
            agents_called["arxiv"] = arx
            for r in arx.get("results", [])[:3]:
                documents_retrieved.append({
                    "source": "arxiv",
                    "id": r.get("id")
                })
            arxiv_summary = "\n".join([f"- {r['title']} ({r['published']})" for r in arx.get("results", [])[:3]])
            final_answer_parts.append("ArXiv Papers Found:\n" + arxiv_summary)

    final_answer = "\n\n".join(final_answer_parts) if final_answer_parts else "No results found."

    trace = {
        "input": user_input,
        "uploaded_pdf": uploaded_pdf_path if uploaded_pdf else None,
        "decision": decision,
        "agents_called": list(agents_called.keys()),
        "documents_retrieved": documents_retrieved,
        "answer": final_answer
    }
    trace_path = save_trace(trace)
    append_log(f"Saved controller trace to {trace_path}")
    return {
        "answer": final_answer,
        "agents_used": list(agents_called.keys()),
        "rationale": decision["rationale"],
        "trace_file": trace_path
    }
