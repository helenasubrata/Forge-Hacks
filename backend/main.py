import os
import requests

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.find import router as find_router

app = FastAPI(title="Receipts API", description="Find real sources and check citations.")

from backend.routes.audit import router as audit_router
app.include_router(audit_router)

# Lets the website (running on a different address) talk to this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(find_router)


APP_VERSION = "2026-10-09 audit-v2"


@app.get("/")
def home():
    """Quick check that the API is running, and which version."""
    return {"status": "ok", "message": "Receipts API is running", "version": APP_VERSION}


@app.get("/health")
def health():
    """Which outside services answer from this server? No keys are shown."""
    checks = {
        "crossref": "https://api.crossref.org/works?query=deep+learning&rows=1",
        "openalex": "https://api.openalex.org/works?search=deep+learning&per-page=1",
        "semantic_scholar": "https://api.semanticscholar.org/graph/v1/paper/search?query=deep+learning&limit=1&fields=title",
    }
    s2_key = (os.getenv("S2_API_KEY") or "").strip().strip('"') or None
    results = {}
    for name, url in checks.items():
        headers = {"x-api-key": s2_key} if name == "semantic_scholar" and s2_key else {}
        try:
            results[name] = requests.get(url, headers=headers, timeout=10).status_code
        except requests.RequestException as error:
            results[name] = f"failed: {error.__class__.__name__}"
    results["s2_key_set"] = bool(s2_key)
    results["llm_configured"] = all(os.getenv(k) for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"))
    return results