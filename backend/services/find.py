"""Find mode: given a claim, find real papers that actually support it."""
from concurrent.futures import ThreadPoolExecutor

from backend.llm import ask_llm
from backend.services.formatter import format_apa, format_mla
from backend.services.search import search_all
from backend.services.verify import check_support, trust_label

CANDIDATES = 8  # how many papers to check per claim
LABEL_RANK = {"Verified": 0, "Weak support": 1, "Contradicted": 2}
FORMATTERS = {"apa": format_apa, "mla": format_mla}


def _search_query(claim):
    """Turn a claim sentence into a short academic search query."""
    try:
        query = ask_llm(
            "Turn this claim into a short academic search query of 4 to 8 keywords. "
            "Reply with the query only, no quotes or extra words.\n\nClaim: " + claim
        )
        query = query.strip().splitlines()[0].strip().strip('"')
        return query if 0 < len(query) <= 120 else claim
    except Exception:
        return claim  # if the AI is down, search with the claim itself


def find_sources(claim, style="apa", limit=5):
    """Search for papers, check each one against the claim, return the best supporters."""
    claim = (claim or "").strip()
    if not claim:
        return {"query": "", "results": [], "message": "Please enter a claim."}

    query = _search_query(claim)
    papers = [p for p in search_all(query, rows=CANDIDATES) if p.get("abstract")]
    if not papers:
        return {"query": query, "results": [], "message": "No papers with abstracts were found for this claim."}

    # Check several papers at once to save time.
    with ThreadPoolExecutor(max_workers=4) as pool:
        checks = list(pool.map(lambda p: check_support(claim, p), papers))

    formatter = FORMATTERS.get((style or "apa").lower(), format_apa)
    results = []
    for paper, check in zip(papers, checks):
        label = trust_label(check)
        if label not in LABEL_RANK:
            continue  # unrelated papers aren't useful as sources
        results.append({
            "label": label,
            "evidence": check["evidence"],
            "explanation": check["explanation"],
            "title": paper["title"],
            "authors": paper.get("authors", []),
            "year": paper.get("year"),
            "year_uncertain": paper.get("year_uncertain", False),
            "journal": paper.get("journal", ""),
            "doi": paper.get("doi"),
            "url": paper.get("url"),
            "citations": paper.get("citations", 0),
            "citation": formatter(paper),
        })

    results.sort(key=lambda r: (LABEL_RANK[r["label"]], -r["citations"]))
    message = "" if results else "No paper found that supports this claim. Try rewording it."
    return {"query": query, "results": results[:limit], "message": message}


if __name__ == "__main__":
    claim = "The Transformer architecture uses only attention mechanisms and no recurrence."
    result = find_sources(claim)
    print("Search query:", result["query"], "\n")
    for r in result["results"]:
        print(f"[{r['label']}] {r['title']} ({r['year']})")
        print("   Evidence:", r["evidence"] or "-")
        print("   Cite:", r["citation"], "\n")
    if result["message"]:
        print(result["message"])