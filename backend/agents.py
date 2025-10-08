import os
from typing import List, Dict
from .utils.config import SERPAPI_KEY
from .utils.logger import append_log

def web_search(query: str, top_k: int = 5) -> Dict:
    append_log(f"Web search requested for: {query}")
    if not SERPAPI_KEY:
        append_log("No SERPAPI_KEY found - returning fallback placeholders.")
        # fallback response
        return {"query": query, "source": "fallback", "results": [
            {"title": "Fallback result 1", "snippet": "No API key provided; connect SerpAPI for live results.", "link": ""},
        ]}


    try:
        from serpapi import GoogleSearch
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": top_k
        }
        search = GoogleSearch(params)
        res = search.get_dict()
        organic = res.get("organic_results", [])[:top_k]
        results = []
        for item in organic:
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link")
            })
        append_log(f"Web search returned {len(results)} results.")
        return {"query": query, "source": "serpapi", "results": results}
    except Exception as e:
        append_log(f"Web search error: {e}")
        return {"query": query, "source": "error", "results": []}
