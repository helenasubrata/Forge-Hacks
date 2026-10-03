def _split_name(full_name):
    """Split 'Ashish Vaswani' into ('Vaswani', ['Ashish'])."""
    parts = full_name.strip().split()
    if len(parts) < 2:
        return full_name.strip(), []
    return parts[-1], parts[:-1]


def _link(paper):
    return f"https://doi.org/{paper['doi']}" if paper.get("doi") else (paper.get("url") or "")


def format_apa(paper):
    names = []
    for full in paper.get("authors", []):
        family, given = _split_name(full)
        initials = " ".join(f"{g[0]}." for g in given)
        names.append(f"{family}, {initials}".strip(", "))

    if not names:
        author_text = ""
    elif len(names) == 1:
        author_text = names[0]
    elif len(names) <= 20:
        author_text = ", ".join(names[:-1]) + ", & " + names[-1]
    else:
        author_text = ", ".join(names[:19]) + ", . . . " + names[-1]

    year = paper.get("year") or "n.d."
    parts = [f"{author_text} ({year}).".strip(), f"{paper['title'].rstrip('.')}."]
    if paper.get("journal"):
        parts.append(f"*{paper['journal']}*.")
    if _link(paper):
        parts.append(_link(paper))
    return " ".join(parts)


def format_mla(paper):
    names = []
    for i, full in enumerate(paper.get("authors", [])):
        family, given = _split_name(full)
        names.append(f"{family}, {' '.join(given)}" if i == 0 else f"{' '.join(given)} {family}")

    if not names:
        author_text = ""
    elif len(names) == 1:
        author_text = names[0]
    elif len(names) == 2:
        author_text = f"{names[0]}, and {names[1]}"
    else:
        author_text = f"{names[0]}, et al"

    parts = []
    if author_text:
        parts.append(f"{author_text}.")
    parts.append(f'"{paper["title"].rstrip(".")}."')
    tail = []
    if paper.get("journal"):
        tail.append(f"*{paper['journal']}*")
    if paper.get("year"):
        tail.append(str(paper["year"]))
    if _link(paper):
        tail.append(_link(paper))
    if tail:
        parts.append(", ".join(tail) + ".")
    return " ".join(parts)


if __name__ == "__main__":
    sample = {  # made-up sample data just for testing
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        "year": 2017,
        "journal": "Advances in Neural Information Processing Systems",
        "doi": None,
        "url": "https://example.com/paper",
    }
    print("APA:", format_apa(sample))
    print("MLA:", format_mla(sample))