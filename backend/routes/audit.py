from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.audit import audit_citation
from backend.services.parser import parse_bibliography

router = APIRouter()

LABEL_ORDER = ["Verified", "Details don't match", "Not found", "Can't check"]


class AuditRequest(BaseModel):
    text: str  # the pasted reference list


@router.post("/audit")
def audit_references(request: AuditRequest):
    """Split a pasted reference list and check every citation."""
    text = request.text.strip()
    if not text:
        return {"results": [], "summary": {}, "message": "Paste a reference list to check."}

    try:
        citations = parse_bibliography(text)
    except Exception:
        return {"results": [], "summary": {}, "message": "Couldn't read the reference list right now. Please try again."}

    if not citations:
        return {"results": [], "summary": {}, "message": "No citations found in that text."}

    results = [audit_citation(c) for c in citations]

    summary = {label: 0 for label in LABEL_ORDER}
    for r in results:
        summary[r["label"]] = summary.get(r["label"], 0) + 1

    return {"results": results, "summary": summary, "message": ""}