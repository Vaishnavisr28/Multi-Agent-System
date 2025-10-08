import os
import requests
from typing import Dict
from .utils.config import SERPAPI_KEY
from .utils.logger import append_log
from serpapi import GoogleSearch


def web_search(query: str, top_k: int = 5) -> Dict:
    """
    Perform a live web search using SerpAPI.
    Returns a dictionary of search results (title, snippet, and link).
    """
    append_log(f"Web Search triggered for: '{query}'")

    # test API key
    if not SERPAPI_KEY:
        append_log("No SERPAPI_KEY found. Returning fallback result.")
        return {
            "query": query,
            "source": "fallback",
            "results": [
                {
                    "title": "No API key provided",
                    "snippet": "Please connect your SerpAPI key in config.py or .env for live web results.",
                    "link": ""
                }
            ]
        }

    #Serpapi search
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": top_k
        }

        resp = requests.get("https://serpapi.com/search", params=params, timeout=20)

        if resp.status_code != 200:
            append_log(f"SerpAPI HTTP Error: {resp.status_code} - {resp.text}")
            return {
                "query": query,
                "source": "serpapi",
                "results": [
                    {
                        "title": "SerpAPI Error",
                        "snippet": f"Error code: {resp.status_code}. Check API key or quota.",
                        "link": ""
                    }
                ]
            }

        data = resp.json()
        organic_results = data.get("organic_results", [])[:top_k]

        if not organic_results:
            append_log(f"No results found for query: {query}")
            return {
                "query": query,
                "source": "serpapi",
                "results": [
                    {"title": "No results found", "snippet": "Try another query.", "link": ""}
                ]
            }

        results = []
        for r in organic_results:
            results.append({
                "title": r.get("title", "Untitled Result"),
                "snippet": r.get("snippet", "No description available."),
                "link": r.get("link", "")
            })

        append_log(f"Web Search returned {len(results)} live results for: {query}")
        return {"query": query, "source": "serpapi", "results": results}

    except Exception as e:
        append_log(f"Web Search Exception: {e}")
        return {
            "query": query,
            "source": "error",
            "results": [
                {
                    "title": "Network or API Error",
                    "snippet": f"Error occurred: {e}",
                    "link": ""
                }
            ]
        }
