import requests

CROSSREF_URL = "https://api.crossref.org/works"


def search_crossref(query, rows=5):
    """Look up papers in Crossref and return a clean list of results."""
    params = {"query.bibliographic": query, "rows": rows}
    headers = {"User-Agent": "Receipts/0.1 (mailto:notwilliam007@gmail.com)"}

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
        })
    return results

OPENALEX_URL = "https://api.openalex.org/works"


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
    params = {"search": query, "per-page": rows, "mailto": "you@example.com"}
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

if __name__ == "__main__":
    print("--- Crossref ---")
    for r in search_crossref("Attention is all you need"):
        print(r["title"], "|", r["year"], "|", r["doi"])

    print("--- OpenAlex ---")
    for r in search_openalex("Attention is all you need"):
        print(r["title"], "|", r["year"], "|", r["citations"], "citations")