import os
import requests
from .logger import append_log


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in environment")

MODEL_NAME = "llama-3.1-8b-instant"  

def generate_summary(query: str, context: str = None) -> str:
    """
    Generate an intelligent response using GROQ's LLM API.
    
    Args:
        query: User's question or request
        context: Optional context from RAG or other sources
    """
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """You are an intelligent AI assistant that provides detailed, accurate, and helpful answers.
When given context information, analyze it carefully and synthesize an informative response that:
- Directly answers the user's question
- Provides relevant details and examples
- Organizes information clearly with sections if needed
- Cites specific sources when referencing information
- Maintains a professional but conversational tone

If no context is provided, use your general knowledge to give the best possible answer."""

        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({
                "role": "user", 
                "content": f"Here is some relevant information:\n\n{context}\n\nBased on this context, please answer: {query}"
            })
        else:
            messages.append({"role": "user", "content": query})
            
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "max_tokens": 800,  # detailed responses degree (increment for more detail)
            "temperature": 0.7,  # creative synthesis degree (increment for more creativity)
            "top_p": 0.9,
            "stop": None
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            append_log(f"GROQ HTTP Error {response.status_code}: {response.text[:200]}")
            return f"GROQ API error {response.status_code}: {response.text}"

        data = response.json()
        message = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        append_log(f"GROQ summary generated ({len(message)} chars)")
        return message or "No summary generated."

    except Exception as e:
        append_log(f"GROQ API Exception: {e}")
        return f"Error while summarizing via GROQ: {e}"
