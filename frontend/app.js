/* Where the Receipts backend runs. Override with window.RECEIPTS_API_URL if it's hosted elsewhere. */
const API_BASE = window.RECEIPTS_API_URL || "https://receipts-api.vercel.app";;

const auditInput = document.getElementById("auditInput");
const findInput = document.getElementById("findInput");

const auditButton = document.getElementById("auditButton");
const findButton = document.getElementById("findButton");

const auditPage = document.getElementById("auditPage");
const findPage = document.getElementById("findPage");

const pageTitle = document.getElementById("pageTitle");

const resultsSection = document.getElementById("resultsSection");
const resultsList = document.getElementById("resultsList");
const sourcesList = document.getElementById("sourcesList");


/* =========================
   NAVIGATION
========================= */

document.querySelectorAll(".nav-item").forEach(button => {
    button.addEventListener("click", () => {
        const page = button.dataset.page;

        document.querySelectorAll(".nav-item")
            .forEach(item => item.classList.remove("active"));
        button.classList.add("active");

        if (page === "audit") {
            auditPage.classList.add("active");
            findPage.classList.remove("active");
            pageTitle.textContent = "Citation Audit";
        }

        if (page === "find") {
            auditPage.classList.remove("active");
            findPage.classList.add("active");
            pageTitle.textContent = "Find Sources";
        }
    });
});


/* =========================
   CHARACTER COUNTERS
========================= */

auditInput.addEventListener("input", () => {
    document.getElementById("charCount").textContent =
        `${auditInput.value.length} characters`;
});

findInput.addEventListener("input", () => {
    document.getElementById("findCharCount").textContent =
        `${findInput.value.length} characters`;
});


/* =========================
   API HELPER
========================= */

async function requestAPI(endpoint, body) {
    let response;

    try {
        response = await fetch(`${API_BASE}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });
    } catch (networkError) {
        throw new Error(
            "Can't reach the Receipts server. Please try again in a moment."
        );
    }

    let data = {};
    try {
        data = await response.json();
    } catch (parseError) {
        throw new Error("The server sent an unexpected reply. Please try again.");
    }

    if (!response.ok) {
        throw new Error(data.detail || data.message || "The request failed. Please try again.");
    }

    return data;
}


/* =========================
   API STATUS (real check, not just a label)
========================= */

async function checkAPIStatus() {
    const badge = document.querySelector(".api-status");
    const sidebar = document.querySelector(".system-status");

    let online = false;
    try {
        const response = await fetch(`${API_BASE}/`);
        online = response.ok;
    } catch (error) {
        online = false;
    }

    const dotClass = online ? "status-dot" : "status-dot offline";

    if (badge) {
        badge.innerHTML = `<span class="${dotClass}"></span>${online ? "API ready" : "API offline"}`;
    }

    if (sidebar) {
        sidebar.innerHTML = `
            <span class="${dotClass}"></span>
            <div>
                <strong>${online ? "Receipts ready" : "Server not running"}</strong>
                <small>${online ? "Ready to verify citations" : "Start the backend to check citations"}</small>
            </div>`;
    }
}

checkAPIStatus();


/* =========================
   AUDIT
========================= */

auditButton.addEventListener("click", async () => {
    const text = auditInput.value.trim();

    if (!text) {
        showError("auditError", "Please paste a citation or bibliography first.");
        return;
    }

    hideError("auditError");
    show("loading");

    auditButton.disabled = true;
    auditButton.textContent = "Checking...";

    try {
        const data = await requestAPI("/audit", { text: text });
        renderAuditResults(data);
    } catch (error) {
        showError("auditError", error.message);
    } finally {
        hide("loading");
        auditButton.disabled = false;
        auditButton.textContent = "✦ Check Receipts";
    }
});


/* =========================
   AUDIT RESULTS
========================= */

const LABEL_ORDER = {
    "Not found": 0,
    "Details don't match": 1,
    "Can't check": 2,
    "Verified": 3
};

function renderAuditResults(data) {
    const results = Array.isArray(data.results) ? data.results : [];
    const summary = data.summary || {};

    document.getElementById("verifiedCount").textContent = summary["Verified"] || 0;
    document.getElementById("weakCount").textContent = summary["Details don't match"] || 0;
    document.getElementById("notFoundCount").textContent = summary["Not found"] || 0;

    document.getElementById("resultTotal").textContent =
        `${results.length} citation${results.length === 1 ? "" : "s"}`;

    if (!results.length) {
        resultsList.innerHTML = `
            <div class="empty">
                ${escapeHTML(data.message || "No citation results were returned.")}
            </div>`;
    } else {
        // Problems first: that's what people need to see.
        const sorted = [...results].sort(
            (a, b) => (LABEL_ORDER[a.label] ?? 2) - (LABEL_ORDER[b.label] ?? 2)
        );
        resultsList.innerHTML = sorted.map(renderCitation).join("");
    }

    resultsSection.classList.remove("hidden");
}


/* =========================
   STATUS -> CSS CLASS
========================= */

function getStatus(label) {
    switch (String(label || "").toLowerCase()) {
        case "verified": return "verified";
        case "details don't match": return "weak";
        case "weak support": return "weak";
        case "not found": return "not-found";
        case "contradicted": return "not-found";
        default: return "cant-check";
    }
}

const ICONS = { "verified": "✓", "weak": "!", "not-found": "×", "cant-check": "?" };


/* =========================
   AUDIT CARD
   Backend shape: { citation: {raw, title, authors, year, journal, doi},
                    label, issues: [...], match: {...} | null, fixed_citation }
========================= */

function renderCitation(item) {
    const status = getStatus(item.label);
    const citation = item.citation || {};
    const issues = Array.isArray(item.issues) ? item.issues : [];
    const match = item.match;

    const title = citation.title || citation.raw || "Citation";

    const meta = [
        (citation.authors || []).join("; "),
        citation.year,
        citation.journal
    ].filter(Boolean).map(escapeHTML).join(" · ");

    const issuesHTML = issues.length
        ? `<ul class="explanation issues ${status === "not-found" ? "danger" : ""}">
               ${issues.map(issue => `<li>${escapeHTML(issue)}</li>`).join("")}
           </ul>`
        : "";

    const matchHTML = match && status === "verified"
        ? `<div class="match-line">
               Matched: ${escapeHTML(match.title)}${match.year ? " · " + escapeHTML(match.year) : ""}${match.journal ? " · " + escapeHTML(match.journal) : ""}
               ${match.url ? `<a class="source-link" href="${escapeHTML(match.url)}" target="_blank" rel="noopener noreferrer">View paper ↗</a>` : ""}
           </div>`
        : "";

    const fixedHTML = item.fixed_citation
        ? citeBox("Corrected citation", item.fixed_citation)
        : "";

    return `
        <article class="citation">
            <div class="result-icon ${status}">${ICONS[status]}</div>

            <div class="citation-body">
                <span class="trust-label ${status}">${escapeHTML(item.label || "Can't check")}</span>
                <div class="citation-title">${escapeHTML(title)}</div>
                ${meta ? `<div class="citation-meta">${meta}</div>` : ""}
                ${issuesHTML}
                ${matchHTML}
                ${fixedHTML}
            </div>
        </article>`;
}


/* =========================
   FIND SOURCES
========================= */

findButton.addEventListener("click", async () => {
    const text = findInput.value.trim();

    if (!text) {
        showError("findError", "Please enter a claim or research topic.");
        return;
    }

    hideError("findError");
    show("findLoading");

    findButton.disabled = true;
    findButton.textContent = "Searching...";

    try {
        const data = await requestAPI("/find", { text: text, style: "apa", limit: 5 });
        renderSources(data);
    } catch (error) {
        showError("findError", error.message);
    } finally {
        hide("findLoading");
        findButton.disabled = false;
        findButton.textContent = "⌕ Find Sources";
    }
});


/* =========================
   FIND RESULTS
========================= */

function renderSources(data) {
    const sources = Array.isArray(data.results) ? data.results : [];

    if (!sources.length) {
        sourcesList.innerHTML = `
            <div class="empty">${escapeHTML(data.message || "No sources found.")}</div>`;
    } else {
        sourcesList.innerHTML = sources.map(renderSource).join("");
    }

    document.getElementById("findResults").classList.remove("hidden");
}


/* =========================
   SOURCE CARD
   Backend shape: { label, evidence, explanation, title, authors, year,
                    year_uncertain, journal, doi, url, citations, citation }
========================= */

function renderSource(source) {
    const status = getStatus(source.label);

    const year = source.year
        ? escapeHTML(source.year) + (source.year_uncertain ? " (year uncertain)" : "")
        : "";

    const meta = [
        escapeHTML((source.authors || []).slice(0, 3).join(", ") + ((source.authors || []).length > 3 ? " et al." : "")),
        year,
        escapeHTML(source.journal || "")
    ].filter(Boolean).join(" · ");

    return `
        <article class="source-card">
            <span class="trust-label ${status}">${escapeHTML(source.label || "")}</span>

            <div class="source-title">${escapeHTML(source.title || "Untitled source")}</div>
            ${meta ? `<div class="source-meta">${meta}</div>` : ""}

            ${source.evidence ? `<blockquote class="evidence ${status}">“${escapeHTML(source.evidence)}”</blockquote>` : ""}
            ${source.explanation ? `<div class="source-meta">${escapeHTML(source.explanation)}</div>` : ""}

            ${source.citation ? citeBox("Citation (APA)", source.citation) : ""}

            ${source.url ? `<a class="source-link" href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">View source ↗</a>` : ""}
        </article>`;
}


/* =========================
   CITATION BOX + COPY
========================= */

/* The backend marks italics as *Journal*. Show them as italics, copy them as plain text. */
function citeBox(heading, text) {
    const plain = String(text).replace(/\*(.+?)\*/g, "$1");
    const shown = escapeHTML(text).replace(/\*(.+?)\*/g, "<em>$1</em>");

    return `
        <div class="cite-box">
            <div>
                <div class="cite-heading">${escapeHTML(heading)}</div>
                <div class="cite-text">${shown}</div>
            </div>
            <button type="button" class="secondary-button copy-button" data-copy="${escapeHTML(plain)}">Copy</button>
        </div>`;
}

document.addEventListener("click", async event => {
    const button = event.target.closest("[data-copy]");
    if (!button) return;

    try {
        await navigator.clipboard.writeText(button.dataset.copy);
        button.textContent = "Copied";
    } catch (error) {
        button.textContent = "Copy failed";
    }

    setTimeout(() => { button.textContent = "Copy"; }, 1500);
});


/* =========================
   CLEAR
========================= */

document.getElementById("clearButton").addEventListener("click", () => {
    auditInput.value = "";
    document.getElementById("charCount").textContent = "0 characters";
    resultsSection.classList.add("hidden");
});


/* =========================
   ERROR / SHOW / HIDE
========================= */

function showError(id, message) {
    const element = document.getElementById(id);
    element.textContent = message;
    element.classList.remove("hidden");
}

function hideError(id) {
    document.getElementById(id).classList.add("hidden");
}

function show(id) {
    document.getElementById(id).classList.remove("hidden");
}

function hide(id) {
    document.getElementById(id).classList.add("hidden");
}


/* =========================
   ESCAPE HTML
========================= */

function escapeHTML(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}