from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.formatter import format_apa, format_mla
from backend.services.search import search_all

router = APIRouter()

FORMATTERS = {"apa": format_apa, "mla": format_mla}


class FindRequest(BaseModel):
    text: str           # what the user wants sources for
    style: str = "apa"  # "apa" or "mla"
    limit: int = 5      # how many results to return


@router.post("/find")
def find_sources(request: FindRequest):
    """Search for real papers matching the text and return formatted citations."""
    text = request.text.strip()
    if not text:
        return {"query": text, "results": [], "message": "Please enter some text."}

    style = request.style.lower()
    formatter = FORMATTERS.get(style, format_apa)

    papers = search_all(text, rows=request.limit)

    results = []
    for paper in papers:
        results.append({
            "title": paper["title"],
            "authors": paper.get("authors", []),
            "year": paper.get("year"),
            "year_uncertain": paper.get("year_uncertain", False),
            "journal": paper.get("journal", ""),
            "doi": paper.get("doi"),
            "url": paper.get("url"),
            "abstract": paper.get("abstract", ""),
            "citations": paper.get("citations", 0),
            "sources": paper.get("sources", []),
            "score": paper.get("score"),
            "citation": formatter(paper),
        })

    message = "" if results else "No matching papers found."
    return {"query": text, "style": style, "results": results, "message": message}