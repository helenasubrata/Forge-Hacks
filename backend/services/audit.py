"""Audit: is each citation real, and do its details match the real paper?"""
import re
import unicodedata
from difflib import SequenceMatcher

import requests

from backend.services.formatter import format_apa
from backend.services.search import CONTACT_EMAIL, search_all

TITLE_MATCH = 0.85  # how close a title must be to count as the same paper
HEADERS = {"User-Agent": f"Receipts/0.1 (mailto:{CONTACT_EMAIL})"}


def _plain(text):
    """Lowercase, strip accents and punctuation: 'Łukasz Kaiser' -> 'lukasz kaiser'."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def _similarity(a, b):
    return SequenceMatcher(None, _plain(a), _plain(b)).ratio()


def lookup_doi(doi):
    """Does this DOI exist? If Crossref knows it, also return the paper it points to."""
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}", headers=HEADERS, timeout=15)
        if r.status_code == 200:
            item = r.json()["message"]
            date_parts = item.get("issued", {}).get("date-parts", [[None]])
            return {"exists": True, "paper": {
                "title": (item.get("title") or [""])[0],
                "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get("author", [])],
                "year": date_parts[0][0] if date_parts and date_parts[0] else None,
                "journal": (item.get("container-title") or [""])[0],
                "doi": item.get("DOI"),
                "url": item.get("URL"),
            }}
        # Not in Crossref: ask the global DOI registry whether it exists at all.
        h = requests.get(f"https://doi.org/api/handles/{doi}", headers=HEADERS, timeout=15)
        exists = h.status_code == 200 and h.json().get("responseCode") == 1
        return {"exists": exists, "paper": None}
    except requests.RequestException:
        return {"exists": None, "paper": None}  # couldn't check (network problem)


def _author_issue(paper, raw):
    """Do the real paper's first authors appear in the citation text?"""
    surnames = [_plain(name).split()[-1] for name in paper.get("authors", [])[:3] if _plain(name)]
    if not surnames:
        return None
    raw_plain = _plain(raw)
    if any(s in raw_plain.split() for s in surnames):
        return None
    return "Authors don't match the real paper."


def audit_citation(citation):
    """Check one parsed citation. Returns a label, the problems found, and the real paper if any."""
    title, raw = citation.get("title") or "", citation.get("raw") or ""
    issues = []

    if not title and not citation.get("doi"):
        return {"citation": citation, "label": "Can't check", "issues": ["No title or DOI to look up."], "match": None, "fixed_citation": ""}

    # 1. If a DOI is given, check it exists and see what it points to.
    doi_info = lookup_doi(citation["doi"]) if citation.get("doi") else None
    if doi_info and doi_info["exists"] is False:
        issues.append("The DOI doesn't exist.")

    # 2. Find the real paper. A DOI whose paper has the cited title is the most reliable
    #    match; otherwise search the databases for the title and take the closest one.
    doi_paper = doi_info["paper"] if doi_info else None
    match, best = None, 0.0
    if title and doi_paper and _similarity(title, doi_paper["title"]) >= TITLE_MATCH:
        match, best = doi_paper, 1.0
    elif title:
        close = []
        for paper in search_all(title, rows=5):
            score = _similarity(title, paper.get("title", ""))
            if score >= TITLE_MATCH:
                close.append((score, paper))
        if close:
            # The same paper often exists as several records (original, preprint, re-uploads).
            # Prefer a record whose authors and year agree with the citation before calling it wrong.
            cited_year = citation.get("year")

            def agreement(item):
                score, paper = item
                names = [_plain(n).split()[-1] for n in paper.get("authors", [])[:1] if _plain(n)]
                first_author_ok = bool(names) and names[0] in _plain(raw).split()
                authors_ok = _author_issue(paper, raw) is None
                year = paper.get("year")
                exact_year = bool(cited_year and year and cited_year == year)
                close_year = bool(cited_year and year and abs(cited_year - year) <= 1)
                return (first_author_ok, authors_ok, exact_year, close_year, score, paper.get("citations") or 0)

            best, match = max(close, key=agreement)

    # A DOI that exists but belongs to a different paper is a classic fabrication.
    if title and doi_paper and _similarity(title, doi_paper["title"]) < 0.6:
        issues.append(f"The DOI points to a different paper: \"{doi_paper['title']}\".")
    if not title and doi_paper:
        match = doi_paper  # no title given, but the DOI is real: use it

    # 3. Compare the details with the real paper.
    if match:
        if citation.get("year") and match.get("year") and abs(citation["year"] - match["year"]) > 1:
            issues.append(f"Year is {citation['year']}, but the real paper is from {match['year']}.")
        author_issue = _author_issue(match, raw)
        if author_issue:
            issues.append(author_issue)

    # 4. Decide the label.
    if not match:
        if doi_info and doi_info["exists"] and not doi_info["paper"]:
            label = "Can't check"
            issues.append("The DOI exists, but its details aren't available to compare.")
        else:
            label = "Not found"
            issues.insert(0, "No real paper with this title was found in Crossref, OpenAlex or Semantic Scholar.")
    elif issues:
        label = "Details don't match"
    else:
        label = "Verified"

    return {
        "citation": citation,
        "label": label,
        "issues": issues,
        "match": {k: match.get(k) for k in ("title", "authors", "year", "journal", "doi", "url")} if match else None,
        "fixed_citation": format_apa(match) if match and issues else "",
    }


if __name__ == "__main__":
    from backend.services.parser import parse_bibliography

    sample = """
1. Vaswani, A., Shazeer, N., & Parmar, N. (2017). Attention is all you need. Advances in Neural Information Processing Systems.
2. Smith, J., & Lee, K. (2021). Deep learning reduces homework stress in high school students. Journal of Educational AI, 12(3), 45-67. https://doi.org/10.1234/jeai.2021.045
3. LeCun, Y., Bengio, Y., & Hinton, G. (2019). Deep learning. Nature, 521, 436-444. https://doi.org/10.1038/nature14539
"""
    for result in map(audit_citation, parse_bibliography(sample)):
        print(f"[{result['label']}] {result['citation']['raw'][:80]}")
        for issue in result["issues"]:
            print("    -", issue)
        if result["fixed_citation"]:
            print("    Fixed:", result["fixed_citation"])
        print()