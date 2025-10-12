import arxiv
from typing import Dict
from .utils.logger import append_log
from .utils.llm_model import generate_summary


def query_arxiv(query: str, max_results: int = 5) -> Dict:
    """
    Query ArXiv for recent papers related to a given topic.
    Uses GROQ to summarize results into a readable paragraph.
    """
    append_log(f"ArXiv query: {query}")

    try:
        search = arxiv.Search(
            query=f"{query} OR {query} AI OR {query} research",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        results = []
        for r in search.results():
            results.append({
                "id": r.entry_id,
                "title": r.title,
                "summary": r.summary[:800],
                "published": r.published.isoformat(),
                "authors": [a.name for a in r.authors],
                "pdf_url": r.pdf_url
            })

        append_log(f"ArXiv returned {len(results)} results for '{query}'.")

        if not results:
            return {"query": query, "source": "arxiv", "summary": "No relevant papers found."}

        paper_summaries = "\n".join(
            [f"- {r['title']} ({r['published'][:10]}): {r['summary']}" for r in results[:max_results]]
        )

        groq_prompt = f"""
        You are an AI research assistant.
        The user asked for recent papers on: "{query}"

        Below are abstracts from ArXiv:
        {paper_summaries}

        Please summarize the main research trends, goals, and findings in 5-6 sentences.
        """
        summary = generate_summary(groq_prompt)

        return {
            "query": query,
            "source": "arxiv",
            "summary": summary,
            "results": results
        }

    except Exception as e:
        append_log(f"ArXiv error: {e}")
        return {"query": query, "source": "error", "summary": f"Error: {e}", "results": []}
