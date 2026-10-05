"""Split a pasted bibliography into separate citations.

The AI reads the messy text and pulls out each citation's details.
Then Receipts double-checks it: every title, year and DOI it returns
must actually appear in the text the user pasted.
"""
import re

from backend.llm import ask_json

MAX_CITATIONS = 30

SYSTEM = (
    "You extract citations from text. Copy details exactly as written; never fix, guess or add anything. "
    "Reply with JSON only."
)

PROMPT = """Below is a pasted reference list. It may use any style (APA, MLA, numbered, messy).

{text}

Return a JSON list with one object per citation, in order, with exactly these keys:
{{"raw": "the full citation text as written",
  "title": "the work's title as written, or empty",
  "authors": ["author names as written"],
  "year": 2017 or null,
  "journal": "journal, venue or publisher as written, or empty",
  "doi": "the DOI if one is written, or empty"}}"""

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)


def _norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (text or "").lower())).strip()


def _clean(item, source_text):
    """Keep only details that really appear in what the user pasted."""
    raw = str(item.get("raw") or "").strip()
    if not raw:
        return None
    pasted = _norm(source_text)

    title = str(item.get("title") or "").strip()
    if title and _norm(title) not in pasted:
        title = ""  # the AI invented or "fixed" the title: drop it

    year = item.get("year")
    try:
        year = int(year) if year else None
    except (TypeError, ValueError):
        year = None
    if year and str(year) not in raw:
        year = None

    doi_match = DOI_RE.search(raw)  # DOIs come from the text itself, never the AI
    doi = doi_match.group(0).rstrip(".,;)") if doi_match else None

    authors = [str(a).strip() for a in (item.get("authors") or []) if str(a).strip()]

    return {
        "raw": raw,
        "title": title,
        "authors": authors,
        "year": year,
        "journal": str(item.get("journal") or "").strip(),
        "doi": doi,
    }


def parse_bibliography(text):
    """Turn pasted reference text into a list of citation dicts."""
    text = (text or "").strip()
    if not text:
        return []

    result = ask_json(PROMPT.format(text=text[:15000]), system=SYSTEM)
    if isinstance(result, dict):  # some models wrap the list: {"citations": [...]}
        result = next((v for v in result.values() if isinstance(v, list)), [])

    citations = []
    for item in result[:MAX_CITATIONS]:
        if isinstance(item, dict):
            cleaned = _clean(item, text)
            if cleaned:
                citations.append(cleaned)
    return citations


if __name__ == "__main__":
    sample = """
1. Vaswani, A., Shazeer, N., & Parmar, N. (2017). Attention is all you need. Advances in Neural Information Processing Systems.
2. Smith, J., & Lee, K. (2021). Deep learning reduces homework stress in high school students. Journal of Educational AI, 12(3), 45-67. https://doi.org/10.1234/jeai.2021.045
3. LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. Nature, 521, 436-444. https://doi.org/10.1038/nature14539
"""
    for c in parse_bibliography(sample):
        print(c["year"], "|", c["title"], "|", c["doi"])
        print("   authors:", ", ".join(c["authors"]))