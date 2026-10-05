from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.find import find_sources

router = APIRouter()


class FindRequest(BaseModel):
    text: str           # the claim to find sources for
    style: str = "apa"  # "apa" or "mla"
    limit: int = 5      # how many results to return


@router.post("/find")
def find_route(request: FindRequest):
    """Find real papers that support a claim, with evidence and a ready citation."""
    try:
        return find_sources(request.text, style=request.style, limit=request.limit)
    except Exception:
        return {"query": request.text, "results": [], "message": "Something went wrong while searching. Please try again."}