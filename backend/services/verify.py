"""Support check: does a paper's abstract really back a claim?

The AI judges the claim, then Receipts double-checks the AI:
the evidence sentence it quotes must actually appear in the abstract.
"""
import re

from backend.llm import ask_json

SYSTEM = (
    "You are a careful fact-checker. You judge whether a research paper's abstract supports a claim. "
    "Use ONLY the abstract you are given, never outside knowledge about the paper. Reply with JSON only."
)

PROMPT = """Claim:
{claim}

Paper title: {title}

Abstract:
{abstract}

How does this abstract relate to the claim? Pick one verdict:
- "supports": the abstract directly backs the claim as one of its own findings or conclusions (not just background, an assumption, or a method)
- "partially_supports": it backs only part of the claim, or a weaker version of it
- "contradicts": it says the opposite of the claim
- "unrelated": it does not address the claim

Return JSON with exactly these keys:
{{"verdict": "...",
  "evidence": "the single most relevant sentence, copied word for word from the abstract, or empty if none",
  "evidence_type": "finding" if the evidence reports this paper's own result or conclusion, "background" if it describes prior knowledge, motivation or an assumption, "method" if it describes what the study did,
  "explanation": "one short plain-English sentence"}}"""

VERDICTS = {"supports", "partially_supports", "contradicts", "unrelated"}
MAX_ABSTRACT_CHARS = 4000


def _norm(text):
    """Lowercase and drop punctuation, so tiny quote differences don't matter."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (text or "").lower())).strip()


def check_support(claim, paper):
    """Ask the AI whether the paper backs the claim, then verify its quote."""
    abstract = (paper.get("abstract") or "").strip()
    if not abstract:
        return {
            "verdict": "no_abstract",
            "evidence": "",
            "evidence_verified": False,
            "explanation": "No abstract is available, so the claim couldn't be checked against this paper.",
        }

    prompt = PROMPT.format(claim=claim.strip(), title=paper.get("title", ""), abstract=abstract[:MAX_ABSTRACT_CHARS])
    try:
        result = ask_json(prompt, system=SYSTEM)
    except Exception as error:  # AI down, bad JSON, etc.: say so instead of guessing
        return {
            "verdict": "error",
            "evidence": "",
            "evidence_verified": False,
            "explanation": f"The AI check failed ({error.__class__.__name__}).",
        }

    verdict = str(result.get("verdict", "")).strip().lower()
    if verdict not in VERDICTS:
        verdict = "unrelated"

    evidence = str(result.get("evidence") or "").strip().strip('"')
    # The self-check: is the quoted evidence really in the abstract?
    evidence_verified = bool(_norm(evidence)) and _norm(evidence) in _norm(abstract)

    return {
        "verdict": verdict,
        "evidence": evidence if evidence_verified else "",
        "evidence_verified": evidence_verified,
        "evidence_type": str(result.get("evidence_type") or "").strip().lower(),
        "explanation": str(result.get("explanation") or "").strip(),
    }


def trust_label(check):
    """Turn a support check into the label people see."""
    verdict = check["verdict"]
    if verdict == "supports" and check["evidence_verified"] and check.get("evidence_type") == "finding":
        return "Verified"
    if verdict in ("supports", "partially_supports"):
        return "Weak support"
    if verdict == "contradicts":
        return "Contradicted"
    if verdict == "unrelated":
        return "Not supported"
    return "Can't check"


if __name__ == "__main__":
    from backend.services.search import search_all

    paper = search_all("Attention is all you need", rows=1)[0]
    print("Paper:", paper["title"], paper["year"], "\n")

    claims = [
        "The Transformer is built only on attention, without recurrence or convolutions.",
        "The Transformer relies on recurrent neural networks to process sequences.",
        "Transformers can detect lung cancer in X-ray images.",
    ]
    for claim in claims:
        check = check_support(claim, paper)
        print("Claim:", claim)
        print("  Label:", trust_label(check), f"({check['verdict']})")
        print("  Evidence:", check["evidence"] or "-")
        print("  Why:", check["explanation"], "\n")