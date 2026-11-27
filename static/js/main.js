/**
 * main.js
 * -------
 * Handles interactive frontend behavior for StudyMate AI:
 *  1. Simple Markdown-to-HTML rendering for Gemini AI outputs
 *  2. Task list filtering on the Dashboard page
 *  3. Mode switching & AJAX generation on the AI Study Studio page
 *  4. AJAX schedule generation on the Study Schedule Planner page
 *  5. One-click Copy to Clipboard for generated outputs
 */

// ---------------------------------------------------------------------------
// 1. Lightweight Markdown Renderer (safe HTML escaping + headings/lists/bold)
// ---------------------------------------------------------------------------
function renderSimpleMarkdown(text) {
  if (!text) return "";

  // Escape HTML characters first to prevent XSS
  const safe = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  const lines = safe.split("\n");
  let html = "";
  let inList = false;

  const formatInline = (line) =>
    line
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/`(.+?)`/g, "<code>$1</code>");

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line) {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      continue;
    }

    if (line.startsWith("&gt; ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<blockquote>${formatInline(line.slice(5))}</blockquote>`;
    } else if (line.startsWith("### ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<h3>${formatInline(line.slice(4))}</h3>`;
    } else if (line.startsWith("## ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<h2>${formatInline(line.slice(3))}</h2>`;
    } else if (line.startsWith("# ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<h2>${formatInline(line.slice(2))}</h2>`;
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${formatInline(line.slice(2))}</li>`;
    } else {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<p>${formatInline(line)}</p>`;
    }
  }

  if (inList) html += "</ul>";
  return html;
}

// Render any saved markdown previews already on the page
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".markdown-source").forEach((el) => {
    el.innerHTML = renderSimpleMarkdown(el.textContent);
  });

  initTaskFilters();
  initStudyStudio();
  initStudyPlanner();
});

// ---------------------------------------------------------------------------
// 2. Dashboard Task Filters (All / Pending / Completed)
// ---------------------------------------------------------------------------
function initTaskFilters() {
  const buttons = document.querySelectorAll(".filter-btn");
  const items = document.querySelectorAll(".task-item");
  if (!buttons.length) return;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const filter = btn.dataset.filter;
      items.forEach((item) => {
        const status = item.dataset.status;
        const show = filter === "all" || filter === status;
        item.style.display = show ? "flex" : "none";
      });
    });
  });
}

// ---------------------------------------------------------------------------
// 3. AI Study Studio (Tab Switching + Fetch API Call)
// ---------------------------------------------------------------------------
function initStudyStudio() {
  const form = document.getElementById("studyStudioForm");
  if (!form) return;

  const modeInput = document.getElementById("studioMode");
  const formTitle = document.getElementById("studioFormTitle");
  const formHint = document.getElementById("studioFormHint");
  const sourceLabel = document.getElementById("sourceTextLabel");
  const extraGroup = document.getElementById("extraOptionGroup");
  const extraLabel = document.getElementById("extraOptionLabel");
  const extraInput = document.getElementById("studioExtraOption");
  const outputBox = document.getElementById("studioOutput");
  const submitBtn = document.getElementById("studioSubmitBtn");
  const copyBtn = document.getElementById("copyStudioBtn");

  const modeConfig = {
    notes: {
      title: "Generate Study Notes",
      hint: "Paste a paragraph, textbook excerpt, or lecture transcript below.",
      sourceLabel: "Study Material / Text",
      showExtra: false,
    },
    summary: {
      title: "Create Summary of Study Material",
      hint: "Condense long chapters or articles into concise exam-ready bullet points.",
      sourceLabel: "Text to Summarize",
      showExtra: false,
    },
    questions: {
      title: "Generate Revision Questions",
      hint: "Turn your notes into MCQs and short-answer practice questions with an answer key.",
      sourceLabel: "Study Material for Questions",
      showExtra: true,
      extraLabel: "Difficulty Level (Optional)",
      extraPlaceholder: "e.g., Easy, Medium, Exam-level Hard",
    },
    outline: {
      title: "Prepare Assignment Outline",
      hint: "Describe your assignment prompt or topic to get a structured section-by-section plan.",
      sourceLabel: "Assignment Prompt / Topic Details",
      showExtra: true,
      extraLabel: "Word Count or Formatting Notes (Optional)",
      extraPlaceholder: "e.g., 1500 words, include real-world case study",
    },
  };

  // Handle tab clicks
  document.querySelectorAll("#studioTabs .tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("#studioTabs .tab-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const mode = btn.dataset.mode;
      const cfg = modeConfig[mode];
      modeInput.value = mode;
      formTitle.textContent = cfg.title;
      formHint.textContent = cfg.hint;
      sourceLabel.textContent = cfg.sourceLabel;

      if (cfg.showExtra) {
        extraGroup.style.display = "flex";
        extraLabel.textContent = cfg.extraLabel;
        extraInput.placeholder = cfg.extraPlaceholder;
      } else {
        extraGroup.style.display = "none";
        extraInput.value = "";
      }
    });
  });

  let latestRawText = "";

  // Handle form submit via Fetch API
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = "Generating...";
    outputBox.innerHTML = `<div class="empty-state"><p>Asking Gemini AI to prepare your study material...</p></div>`;

    try {
      const response = await fetch("/api/study-studio/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode: modeInput.value,
          title: document.getElementById("studioTitle").value,
          source_text: document.getElementById("studioSourceText").value,
          extra_option: extraInput.value,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        outputBox.innerHTML = `<div class="flash flash-error">${data.error || "Generation failed."}</div>`;
      } else {
        latestRawText = data.output;
        outputBox.innerHTML = renderSimpleMarkdown(data.output);
        copyBtn.style.display = "inline-flex";
      }
    } catch (err) {
      outputBox.innerHTML = `<div class="flash flash-error">Network error. Please make sure Flask is running.</div>`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "✦ Generate with Gemini AI";
    }
  });

  // Copy to clipboard button
  copyBtn.addEventListener("click", async () => {
    if (!latestRawText) return;
    await navigator.clipboard.writeText(latestRawText);
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy Output"), 1500);
  });
}

// ---------------------------------------------------------------------------
// 4. Personalized Study Schedule Planner (Fetch API Call)
// ---------------------------------------------------------------------------
function initStudyPlanner() {
  const form = document.getElementById("plannerForm");
  if (!form) return;

  const outputBox = document.getElementById("plannerOutput");
  const submitBtn = document.getElementById("plannerSubmitBtn");
  const copyBtn = document.getElementById("copyPlannerBtn");
  let latestScheduleText = "";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = "Building Schedule...";
    outputBox.innerHTML = `<div class="empty-state"><p>Creating your personalized study timetable...</p></div>`;

    try {
      const response = await fetch("/api/planner/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: document.getElementById("planTitle").value,
          subjects: document.getElementById("planSubjects").value,
          exam_date: document.getElementById("planExamDate").value,
          daily_hours: document.getElementById("planDailyHours").value,
          focus_areas: document.getElementById("planFocusAreas").value,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        outputBox.innerHTML = `<div class="flash flash-error">${data.error || "Could not create schedule."}</div>`;
      } else {
        latestScheduleText = data.output;
        outputBox.innerHTML = renderSimpleMarkdown(data.output);
        copyBtn.style.display = "inline-flex";
      }
    } catch (err) {
      outputBox.innerHTML = `<div class="flash flash-error">Network error. Please make sure Flask is running.</div>`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "✦ Generate Study Schedule";
    }
  });

  copyBtn.addEventListener("click", async () => {
    if (!latestScheduleText) return;
    await navigator.clipboard.writeText(latestScheduleText);
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy Schedule"), 1500);
  });
}
