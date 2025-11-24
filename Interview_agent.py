import os
import random
from typing import List, Dict, Any

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def fallback_model(prompt: str, messages: List[Dict[str, str]]) -> str:
    ...

def call_openai_system(user_prompt: str, messages: List[Dict[str, str]], max_tokens: int = 300) -> str:
    try:
        if not OPENAI_KEY:
            raise Exception("No API key set")
        import openai
        openai.api_key = OPENAI_KEY
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI call failed:", str(e))
        return fallback_model(user_prompt, messages)
