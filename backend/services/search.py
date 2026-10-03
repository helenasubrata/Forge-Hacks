import math
import re
import time
from difflib import SequenceMatcher

import requests

CONTACT_EMAIL = "you@example.com"  # put your real email here

CROSSREF_URL = "https://api.crossref.org/works"
OPENALEX_URL = "https://api.openalex.org/works"
SEMANTIC_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


# ---------- Crossref ----------

def search_crossref(query, rows=5):
    """Look up papers in Crossref and return a clean list of results."""
    params = {"query.bibliographic": query, "rows": rows}
    headers = {"User-Agent": f"Receipts/0.1 (mailto:{"notwilliam007@gmail.com"})"}

    response = requests.get(CROSSREF_URL, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    items = response.json()["message"]["items"]

    results = []
    for item in items:
        authors = [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in item.get("author", [])
        ]
        date_parts = item.get("issued", {}).get("date-parts", [[None]])
        year = date_parts[0][0] if date_parts and date_parts[0] else None

        results.append({
            "title": (item.get("title") or [""])[0],
            "authors": authors,
            "year": year,
            "journal": (item.get("container-title") or [""])[0],
            "doi": item.get("DOI"),
            "url": item.get("URL"),
            "abstract": "",
            "citations": item.get("is-referenced-by-count", 0),
        })
    return results


# ---------- OpenAlex ----------

def rebuild_abstract(inverted_index):
    """OpenAlex stores abstracts as word -> positions. Put them back in order."""
    if not inverted_index:
        return ""
    words = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words[i] for i in sorted(words))


def search_openalex(query, rows=5):
    """Look up papers in OpenAlex and return a clean list of results."""
    params = {"search": query, "per-page": rows, "mailto": CONTACT_EMAIL}
    response = requests.get(OPENALEX_URL, params=params, timeout=15)
    response.raise_for_status()

    results = []
    for item in response.json()["results"]:
        authors = [a["author"]["display_name"] for a in item.get("authorships", [])]
        source = (item.get("primary_location") or {}).get("source") or {}
        doi_url = item.get("doi") or ""

        results.append({
            "title": item.get("title") or "",
            "authors": authors,
            "year": item.get("publication_year"),
            "journal": source.get("display_name") or "",
            "doi": doi_url.replace("https://doi.org/", "") or None,
            "url": doi_url or item.get("id"),
            "abstract": rebuild_abstract(item.get("abstract_inverted_index")),
            "citations": item.get("cited_by_count", 0),
        })
    return results


# ---------- Semantic Scholar ----------

def search_semantic_scholar(query, rows=5):
    """Look up papers in Semantic Scholar (no key needed, but it rate-limits)."""
    params = {
        "query": query,
        "limit": rows,
        "fields": "title,year,authors,venue,externalIds,citationCount,abstract,url",
    }
    response = requests.get(SEMANTIC_URL, params=params, timeout=15)
    if response.status_code == 429:  # "too many requests": wait a moment, try once more
        time.sleep(2)
        response = requests.get(SEMANTIC_URL, params=params, timeout=15)
    response.raise_for_status()

    results = []
    for item in response.json().get("data", []):
        ids = item.get("externalIds") or {}
        results.append({
            "title": item.get("title") or "",
            "authors": [a.get("name", "") for a in item.get("authors", [])],
            "year": item.get("year"),
            "journal": item.get("venue") or "",
            "doi": ids.get("DOI"),
            "url": item.get("url"),
            "abstract": item.get("abstract") or "",
            "citations": item.get("citationCount") or 0,
        })
    return results


# ---------- combining ----------

def _normalize(text):
    """Lowercase and strip punctuation so titles can be compared fairly."""
    return re.sub(r"[^a-z0-9 ]", "", (text or "").lower()).strip()


def _same_paper(a, b):
    """Same DOI, or exactly the same title, means same paper."""
    doi_a, doi_b = (a.get("doi") or "").lower(), (b.get("doi") or "").lower()
    if doi_a and doi_a == doi_b:
        return True
    title_a = _normalize(a["title"])
    return bool(title_a) and title_a == _normalize(b["title"])


def _score(paper, query):
    """Title similarity matters most; citations give a small boost."""
    similarity = SequenceMatcher(None, _normalize(query), _normalize(paper["title"])).ratio()
    citation_boost = math.log10(paper.get("citations", 0) + 1) / 10
    return similarity + citation_boost


def search_all(query, rows=5):
    """Search every source, merge duplicates, settle the year, rank best first."""
    sources = [
        ("crossref", search_crossref),
        ("openalex", search_openalex),
        ("semantic_scholar", search_semantic_scholar),
    ]
    papers = []

    for source_name, search in sources:
        try:
            results = search(query, rows)
        except requests.RequestException as error:
            print(f"Warning: {source_name} failed ({error})")
            continue

        for paper in results:
            match = next((p for p in papers if _same_paper(p, paper)), None)
            if match is None:
                paper["sources"] = [source_name]
                paper["years_seen"] = [paper["year"]] if paper.get("year") else []
                papers.append(paper)
            else:
                match["sources"].append(source_name)
                if paper.get("year"):
                    match["years_seen"].append(paper["year"])
                match["citations"] = max(match.get("citations", 0), paper.get("citations", 0))
                for field, value in paper.items():
                    if value and not match.get(field):
                        match[field] = value

    for paper in papers:
        # A paper can be republished later, but never published before it existed,
        # so when sources disagree we trust the earliest year and flag it.
        years = paper.pop("years_seen")
        paper["year"] = min(years) if years else None
        paper["year_uncertain"] = len(set(years)) > 1
        paper["score"] = round(_score(paper, query), 3)

    papers.sort(key=lambda p: p["score"], reverse=True)
    return papers[:rows]


if __name__ == "__main__":
    for r in search_all("Attention is all you need"):
        flag = " (year uncertain)" if r["year_uncertain"] else ""
        print(r["score"], "|", r["title"], "|", f"{r['year']}{flag}", "|", ", ".join(r["sources"]))