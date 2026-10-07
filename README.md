# 🧾 Receipts

### Citation Trust, Without the Guesswork.

Receipts is an AI-powered citation verification and source discovery tool for academic writing.

Instead of trusting that a citation "looks right", Receipts helps writers check whether a reference can actually be found and whether its bibliographic details match a real source.

🔗 **Live Demo:** https://tryreceipts.vercel.app

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

---

## 🏆 Hackathon Track

**AI + Education**

Receipts uses AI-powered source retrieval and reasoning to help students and academic writers verify citations, identify citation mismatches, and discover reliable academic sources. 

---

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

Paste the claim and Receipts finds relevant academic sources, including:

- Paper title
- Authors
- Publication year
- Journal / venue
- Source link

---

## ✨ Features

### Citation Audit
Verify individual citations or complete bibliographies.

### Source Discovery
Find academic sources relevant to a claim.

### AI-Assisted Verification
AI helps interpret citation details and compare them against retrieved source information.

### Clear Trust Labels
Results are separated into understandable verification states instead of giving users an unexplained confidence score.

### Multiple Citation Support
Audit multiple references in a single request and get an overview of the results.

### Clean Academic Workflow
Designed to fit naturally into the research and writing process.

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

---

## 🎯 Why Receipts?

Most citation tools focus on **formatting**.

Receipts focuses on **trust**.

A citation can follow APA formatting perfectly and still point to the wrong paper, contain incorrect bibliographic details, or reference a source that does not exist.

Receipts asks a different question:

> **Can I actually find the source behind this citation?**

This makes Receipts useful not only for formatting references, but for checking whether the references themselves are trustworthy.

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
- Semantic Scholar API

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

## 📂 Project Structure

```text
Forge-Hacks/
│
├── backend/
│   ├── routes/
│   │   ├── audit.py
│   │   └── find.py
│   ├── services/
│   │   ├── audit.py
│   │   ├── find.py
│   │   └── parser.py
│   ├── __init__.py
│   ├── llm.py
│   └── main.py
│
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

## 🔮 Future Improvements

Potential future directions include:

- 🔗 **DOI-level verification** for more precise source matching
- 📚 **More academic databases** beyond the current source provider
- 📝 **Citation export** to APA, MLA, Chicago, and other formats
- 🌐 **Browser extension** for checking citations while researching
- 📄 **PDF and document scanning** to audit references directly from documents
- 🔄 **In-text citation ↔ bibliography consistency checking**
- ✍️ **Citation recommendations** based on the user's writing
- 🎯 **Stronger evidence matching** between claims and sources
- 🧠 **Better semantic matching** for paraphrased or incomplete citations
- 📊 **Citation quality insights** across an entire document

---

## 👥 Built For

Students, researchers, and writers who want to spend less time manually checking references and more time doing meaningful research.

---

## 🧾 Built with Receipts

**Don't just cite it. Get the receipts.**
