"""The one place Receipts talks to an AI model.

Works with any OpenAI-compatible provider (Groq, Featherless, ...).
To switch providers, change the three LLM_ lines in .env. No code changes needed.
"""
import json
import os
import re
import time

import requests
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = (os.getenv("LLM_BASE_URL") or "").strip().strip('"').rstrip("/")
LLM_API_KEY = (os.getenv("LLM_API_KEY") or "").strip().strip('"')
LLM_MODEL = (os.getenv("LLM_MODEL") or "").strip().strip('"')


def ask_llm(prompt, system=None, temperature=0):
    """Send a prompt to the AI and return its text reply."""
    if not (LLM_BASE_URL and LLM_API_KEY and LLM_MODEL):
        raise RuntimeError("LLM settings missing: check LLM_BASE_URL, LLM_API_KEY and LLM_MODEL in .env")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {"model": LLM_MODEL, "messages": messages, "temperature": temperature}
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}

    for attempt in range(4):
        response = requests.post(f"{LLM_BASE_URL}/chat/completions", json=body, headers=headers, timeout=60)
        if response.status_code not in (429, 503):  # busy? wait and retry
            break
        if attempt < 3:
            time.sleep(2 ** attempt)  # exponential backoff: 1, 2, 4 seconds

    if response.status_code != 200:
        raise RuntimeError(f"LLM error {response.status_code}: {response.text[:300]}")

    return response.json()["choices"][0]["message"]["content"].strip()


def ask_json(prompt, system=None):
    """Ask the AI for JSON and turn the reply into Python data."""
    reply = ask_llm(prompt, system=system)
    reply = re.sub(r"^```(?:json)?\s*|\s*```$", "", reply.strip())  # drop ``` fences if any
    start = min([i for i in (reply.find("{"), reply.find("[")) if i != -1], default=-1)
    end = max(reply.rfind("}"), reply.rfind("]"))
    if start == -1 or end == -1:
        raise ValueError(f"AI did not return JSON: {reply[:200]}")
    return json.loads(reply[start:end + 1])


if __name__ == "__main__":
    print("Model:", LLM_MODEL)
    print("Reply:", ask_llm("Reply with exactly this sentence: Receipts is online."))
    print("JSON:", ask_json('Return only this JSON: {"status": "ok", "number": 7}'))