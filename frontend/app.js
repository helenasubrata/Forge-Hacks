const API_BASE = "http://127.0.0.1:8000";

const auditInput = document.getElementById("auditInput");
const findInput = document.getElementById("findInput");

const auditButton = document.getElementById("auditButton");
const findButton = document.getElementById("findButton");

const auditPage = document.getElementById("auditPage");
const findPage = document.getElementById("findPage");

const pageTitle = document.getElementById("pageTitle");

const resultsSection = document.getElementById("resultsSection");
const resultsList = document.getElementById("resultsList");


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

    const response = await fetch(
        `${API_BASE}${endpoint}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail ||
            data.message ||
            "API request failed."
        );
    }

    return data;
}


/* =========================
   AUDIT
========================= */

auditButton.addEventListener("click", async () => {

    const text = auditInput.value.trim();

    if (!text) {
        showError(
            "auditError",
            "Please paste a citation or bibliography first."
        );
        return;
    }

    hideError("auditError");

    show("loading");

    auditButton.disabled = true;
    auditButton.textContent = "Checking...";

    try {

        const data = await requestAPI(
            "/audit",
            {
                text: text
            }
        );

        renderAuditResults(data);

    } catch (error) {

        showError(
            "auditError",
            error.message
        );

    } finally {

        hide("loading");

        auditButton.disabled = false;
        auditButton.textContent = "✦ Check Receipts";
    }
});


/* =========================
   AUDIT RESULTS
========================= */

function renderAuditResults(data) {

    const results = Array.isArray(data.results)
        ? data.results
        : [];

    const summary = data.summary || {};

    const verified =
        summary["Verified"] || 0;

    const detailsMismatch =
        summary["Details don't match"] || 0;

    const notFound =
        summary["Not found"] || 0;

    const cantCheck =
        summary["Can't check"] || 0;


    /*
     * Existing UI has three summary cards.
     * We use:
     * Verified
     * Weak Support = Details don't match
     * Not Found = Not found
     *
     * Can't check is still shown inside
     * individual result cards.
     */

    document.getElementById("verifiedCount")
        .textContent = verified;

    document.getElementById("weakCount")
        .textContent = detailsMismatch;

    document.getElementById("notFoundCount")
        .textContent = notFound;


    document.getElementById("resultTotal")
        .textContent =
        `${results.length} citation${results.length === 1 ? "" : "s"}`;


    if (!results.length) {

        resultsList.innerHTML = `
            <div class="empty">
                ${escapeHTML(
                    data.message ||
                    "No citation results were returned."
                )}
            </div>
        `;

    } else {

        resultsList.innerHTML =
            results.map(renderCitation).join("");
    }


    resultsSection.classList.remove("hidden");
}


/* =========================
   AUDIT STATUS
========================= */

function getStatus(item) {

    const label = String(
        item.label ||
        item.status ||
        ""
    ).toLowerCase();


    if (label === "verified") {
        return "verified";
    }

    if (label === "details don't match") {
        return "weak";
    }

    if (label === "not found") {
        return "not-found";
    }

    if (label === "can't check") {
        return "cant-check";
    }

    return "cant-check";
}


/* =========================
   AUDIT CARD
========================= */

function renderCitation(item) {

    const status = getStatus(item);

    const label =
        item.label ||
        "Can't check";


    const title =
        item.title ||
        item.citation ||
        item.reference ||
        item.text ||
        item.source_title ||
        "Citation";


    const reason =
        item.reason ||
        item.explanation ||
        item.message ||
        "";


    const authors =
        item.authors ||
        item.author ||
        "";


    const year =
        item.year ||
        item.publication_year ||
        "";


    const journal =
        item.journal ||
        item.venue ||
        "";


    let icon = "?" ;

    if (status === "verified") {
        icon = "✓";
    }

    if (status === "weak") {
        icon = "!";
    }

    if (status === "not-found") {
        icon = "×";
    }


    return `
        <article class="citation">

            <div class="result-icon ${status}">
                ${icon}
            </div>

            <div class="citation-body">

                <span class="trust-label ${status}">
                    ${escapeHTML(label)}
                </span>

                <div class="citation-title">
                    ${escapeHTML(title)}
                </div>

                <div class="citation-meta">
                    ${escapeHTML(authors)}

                    ${
                        year
                            ? " · " + escapeHTML(year)
                            : ""
                    }

                    ${
                        journal
                            ? " · " + escapeHTML(journal)
                            : ""
                    }
                </div>

                ${
                    reason
                        ? `
                            <div class="explanation ${
                                status === "not-found"
                                    ? "danger"
                                    : ""
                            }">
                                ${escapeHTML(reason)}
                            </div>
                        `
                        : ""
                }

            </div>

        </article>
    `;
}


/* =========================
   FIND SOURCES
========================= */

findButton.addEventListener("click", async () => {

    const text = findInput.value.trim();

    if (!text) {

        showError(
            "findError",
            "Please enter a claim or research topic."
        );

        return;
    }


    hideError("findError");

    show("findLoading");

    findButton.disabled = true;
    findButton.textContent = "Searching...";


    try {

        /*
         * Backend expects:
         *
         * {
         *     text: "...",
         *     style: "apa",
         *     limit: 5
         * }
         */

        const data = await requestAPI(
            "/find",
            {
                text: text,
                style: "apa",
                limit: 5
            }
        );


        renderSources(data);

    } catch (error) {

        showError(
            "findError",
            error.message
        );

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

    const sources = Array.isArray(data.results)
        ? data.results
        : [];


    if (!sources.length) {

        sourcesList.innerHTML = `
            <div class="empty">
                ${escapeHTML(
                    data.message ||
                    "No sources found."
                )}
            </div>
        `;

    } else {

        sourcesList.innerHTML =
            sources.map(renderSource).join("");
    }


    document.getElementById("findResults")
        .classList.remove("hidden");
}


/* =========================
   SOURCE CARD
========================= */

function renderSource(source) {

    const title =
        source.title ||
        source.name ||
        "Untitled source";


    const authors =
        source.authors ||
        source.author ||
        "";


    const year =
        source.year ||
        source.publication_year ||
        "";


    const journal =
        source.journal ||
        source.venue ||
        "";


    const abstract =
        source.abstract ||
        source.description ||
        "";


    const url =
        source.url ||
        source.link ||
        "";


    return `
        <article class="source-card">

            <div class="source-title">
                ${escapeHTML(title)}
            </div>

            <div class="source-meta">

                ${escapeHTML(authors)}

                ${
                    year
                        ? " · " + escapeHTML(year)
                        : ""
                }

                ${
                    journal
                        ? " · " + escapeHTML(journal)
                        : ""
                }

            </div>

            ${
                abstract
                    ? `
                        <div class="source-meta">
                            ${escapeHTML(
                                abstract.substring(0, 300)
                            )}
                            ${
                                abstract.length > 300
                                    ? "..."
                                    : ""
                            }
                        </div>
                    `
                    : ""
            }

            ${
                url
                    ? `
                        <a
                            class="source-link"
                            href="${escapeHTML(url)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            View source ↗
                        </a>
                    `
                    : ""
            }

        </article>
    `;
}


/* =========================
   CLEAR
========================= */

document.getElementById("clearButton")
    .addEventListener("click", () => {

        auditInput.value = "";

        document.getElementById("charCount")
            .textContent = "0 characters";

        resultsSection.classList.add("hidden");
    });


/* =========================
   ERROR
========================= */

function showError(id, message) {

    const element = document.getElementById(id);

    element.textContent = message;

    element.classList.remove("hidden");
}


function hideError(id) {

    document.getElementById(id)
        .classList.add("hidden");
}


/* =========================
   SHOW / HIDE
========================= */

function show(id) {

    document.getElementById(id)
        .classList.remove("hidden");
}


function hide(id) {

    document.getElementById(id)
        .classList.add("hidden");
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