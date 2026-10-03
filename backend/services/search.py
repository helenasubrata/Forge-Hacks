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


if __name__ == "__main__":
    for r in search_crossref("Attention is all you need"):
        print(r["title"], "|", r["year"], "|", r["doi"])