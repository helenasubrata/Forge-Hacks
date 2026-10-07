# 🧾 Receipts

### Citation Trust, Without the Guesswork.

Receipts is an AI-powered citation verification and source discovery tool for academic writing.

Instead of trusting that a citation "looks right", Receipts helps writers check whether a reference can actually be found and whether its bibliographic details match a real source.

🔗 **Live Demo:** https://tryreceipts.vercel.app

---

## 🏆 Hackathon Track

**AI + Cybersecurity**

AI makes fake evidence cheap. Chatbots invent studies that look real, with plausible titles, real-sounding journals and DOIs, and real researchers' names attached to papers they never wrote. Receipts helps people **verify** citations and catch **AI-enabled fabrication** before it spreads into essays, articles and claims online.

---

## 🚨 The Problem

Academic writing depends on reliable sources.

But checking references manually is slow and error-prone:

- Is this paper actually real?
- Does the title match the cited source?
- Is the author correct?
- Is the publication year correct?
- Did I accidentally cite a source that doesn't exist?
- What source should I use to support this claim?

Students often have to search databases one by one just to answer these questions.

**Receipts turns that process into one workflow.**

---

## 💡 The Solution

Receipts combines AI reasoning with academic source retrieval to help users:

> **Audit citations they already have — and discover sources they still need.**

### Two Core Workflows

#### 🔎 Citation Audit

Paste a citation or an entire bibliography.

Receipts analyzes each reference and classifies it as:

- 🟢 **Verified** — the source was found and the reference details match.
- 🟡 **Details Don't Match** — a related source was found, but some bibliographic details differ.
- 🔴 **Not Found** — no matching source could be identified.
- ⚪ **Can't Check** — there wasn't enough information to confidently verify it.

#### 📚 Find Sources

Have a claim but don't know what to cite?

Paste the claim and Receipts searches real databases, checks each paper's abstract against your claim, and returns:

- A support label: **Verified**, **Weak Support** or **Contradicted**
- The exact evidence sentence from the abstract
- A short explanation of why
- A ready-to-copy APA citation and a link to the paper

---

## ✨ Features

### Citation Audit
Verify individual citations or complete bibliographies.
For citations with wrong details, Receipts shows the corrected citation for the real paper, ready to copy.

### Source Discovery
Find academic sources relevant to a claim.

### AI-Assisted Verification
AI reads messy reference lists in any style; the details are then compared against real database records by code, not by the AI.

### Clear Trust Labels
Results are separated into understandable verification states instead of giving users an unexplained confidence score.

### Multiple Citation Support
Audit multiple references in a single request and get an overview of the results.

### Clean Academic Workflow
Designed to fit naturally into the research and writing process.

---

## 🎯 Why Receipts?

Most citation tools focus on **formatting**.

Receipts focuses on **trust**.

A citation can follow APA formatting perfectly and still point to the wrong paper, contain incorrect bibliographic details, or reference a source that does not exist.

Receipts asks a different question:

> **Can I actually find the source behind this citation?**

This makes Receipts useful not only for formatting references, but for checking whether the references themselves are trustworthy.

---

## 🧠 How It Works

```text
                    ┌──────────────────┐
                    │       User       │
                    │ Citation / Claim │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Receipts     │
                    │    FastAPI API   │
                    └────────┬─────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌───────────────┐     ┌───────────────┐
          │ Source Search │     │   AI Analysis │
          │  & Retrieval  │     │  & Matching   │
          └───────┬───────┘     └───────┬───────┘
                  │                     │
                  └──────────┬──────────┘
                             ▼
                    ┌──────────────────┐
                    │ Verification /   │
                    │ Source Results   │
                    └──────────────────┘
```

### Receipts checks its own AI

AI does the reading; real data does the deciding.

- **Sources come from real databases**: Crossref, OpenAlex, Semantic Scholar and the doi.org registry. The AI never invents a paper.
- **Quotes are verified**: when the AI says a paper supports a claim, the quoted sentence must appear in the paper's abstract, or the result is downgraded.
- **Only findings count**: a paper is "Verified" only if the quote is one of its own findings, not background or method.
- **The parser can't invent details**: titles and years must appear in the pasted text, and DOIs are read straight from it, never from the AI.
- **Formatting is plain code**: APA and MLA citations are built by rules, not generated by AI.

---

## 🏗️ Tech Stack

### Frontend
- HTML
- CSS
- JavaScript
- Vercel

### Backend
- Python
- FastAPI
- Vercel

### AI
- Groq
- OpenAI-compatible LLM API

### Academic Source Retrieval
- Crossref
- OpenAlex
- Semantic Scholar
- doi.org

---

## 🔐 Trust & Safety

Receipts is designed to assist with citation verification, not replace academic judgment.

AI-generated results are treated as supporting analysis, while source metadata and retrieval results provide the evidence used for verification.

API keys are stored as environment variables and are not exposed in the frontend.

---

## 🌍 Real-World Impact

Receipts is designed to reduce the time and effort required to verify academic references.

For students and researchers, manually checking every citation can mean searching multiple academic databases and comparing bibliographic details one by one.

Receipts turns this into a single workflow:

1. Paste a citation or bibliography.
2. Retrieve potentially matching academic sources.
3. Compare citation details against retrieved metadata.
4. Receive a clear verification result.

This can help users catch incorrect, incomplete, or unverifiable references before they become part of an academic paper.

Receipts can also help users discover relevant sources when they know what they want to research but do not yet know what to cite.

---

## 🚀 Live Demo

**Frontend:** https://tryreceipts.vercel.app  
**Backend API:** https://receipts-api.vercel.app

---

## 🎥 Demo Video

**Public Demo Video:**  
[ADD YOUTUBE LINK]

The demo shows:

- The citation verification problem
- How Citation Audit works
- How Find Sources works
- AI-assisted source matching
- Verification results
- The deployed Receipts application

---

## 💻 Run It Locally

```bash
git clone https://github.com/helenasubrata/Forge-Hacks.git
cd Forge-Hacks
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`):

```
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your-groq-key
LLM_MODEL=openai/gpt-oss-120b
S2_API_KEY=your-semantic-scholar-key   # optional, avoids rate limits
```

Start the backend with `uvicorn backend.main:app --reload`, then set the first line of `frontend/app.js` to `http://127.0.0.1:8000` and open `frontend/index.html`.

---

## 📂 Project Structure

```text
Forge-Hacks/
│
├── backend/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── audit.py
│   │   └── find.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audit.py
│   │   ├── find.py
│   │   ├── formatter.py
│   │   ├── parser.py
│   │   ├── search.py
│   │   └── verify.py
│   ├── __init__.py
│   ├── llm.py
│   └── main.py
├── frontend/
│   ├── assets/
│   │   └── logo.svg
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── index.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ✅ What Works / ⚠️ What Doesn't (Yet)

**Works**
- Auditing pasted bibliographies (up to 30 citations): existence, DOI checks, year and author mismatches, corrected citations
- Finding sources for a claim, with support labels and verified evidence quotes
- Live deployment (frontend and backend on Vercel)

**Known limitations**
- Support labels on borderline papers can vary between runs, since AI judgments aren't perfectly consistent
- Only abstracts are checked, not full papers
- Long bibliographies can be slow (Semantic Scholar allows 1 request per second)
- Some author names (e.g. multi-word surnames) are formatted imperfectly
- "Not found" means no match in our databases, not proof that a paper doesn't exist

---

## ⚠️ Limitations

Receipts relies on available academic source metadata and retrieval results.

A **Not Found** result does not necessarily mean that a paper does not exist. It may mean that Receipts could not confidently retrieve or match the source.

Users should always review the original source before citing it in academic work.

---

## 🔮 Future Improvements

Potential future directions include:

- 📚 **More academic databases** beyond the current retrieval sources
- 📝 **More citation styles** such as Chicago (APA and MLA already supported)
- 🌐 **Browser extension** for checking citations while researching
- 📄 **PDF and document scanning** to audit references directly from documents
- 🔄 **In-text citation ↔ bibliography consistency checking**
- ✍️ **Citation recommendations** based on the user's writing
- 🎯 **Stronger evidence matching** between claims and sources
- 📊 **Citation quality insights** across an entire document

---

## 👥 Built For

Students, researchers, and writers who want to spend less time manually checking references and more time doing meaningful research.

---

## 🧾 Built with Receipts

**Don't just cite it. Get the receipts.**

### Built With AI Assistance
AI coding assistants helped write parts of the code. The AI inside Receipts is gpt-oss-120b, served by Groq.