/* ── dashboard.js ──────────────────────────────────────────────────────
   Handles:
     - Tab navigation
     - Theme toggle (dark / light)
     - Dashboard data fetching, KPI rendering, chart rendering, table
     - Single-text analysis tab
     - CSV upload tab
──────────────────────────────────────────────────────────────────────── */

"use strict";

// ════════════════════════════════════════════════════════════════════════
// 0. THEME TOGGLE
// ════════════════════════════════════════════════════════════════════════
const themeBtn = document.getElementById("theme-toggle");

function applyTheme(theme) {
  if (theme === "light") {
    document.body.classList.add("light");
    themeBtn.textContent = "☀️";
    themeBtn.title = "Switch to Dark Mode";
  } else {
    document.body.classList.remove("light");
    themeBtn.textContent = "🌙";
    themeBtn.title = "Switch to Light Mode";
  }
  localStorage.setItem("theme", theme);
}

// Load saved preference on page load
applyTheme(localStorage.getItem("theme") || "dark");

themeBtn.addEventListener("click", () => {
  const isLight = document.body.classList.contains("light");
  applyTheme(isLight ? "dark" : "light");
});

// ── Chart colour palette ────────────────────────────────────────────────
const C = {
  pos:    "#22c55e",
  neu:    "#f59e0b",
  neg:    "#ef4444",
  accent: "#6366f1",
  muted:  "#94a3b8",
  grid:   "rgba(51,65,85,0.6)",
  text:   "#e2e8f0",
};

Chart.defaults.color = C.text;
Chart.defaults.borderColor = C.grid;

// ── Shared chart instances (so we can destroy/recreate on filter) ────────
let pieChart    = null;
let lineChart   = null;
let platformChart = null;
let topChart    = null;

// ════════════════════════════════════════════════════════════════════════
// 1. TAB NAVIGATION
// ════════════════════════════════════════════════════════════════════════
document.querySelectorAll(".nav-tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-tab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-section").forEach(s => s.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// ════════════════════════════════════════════════════════════════════════
// 2. DASHBOARD – FETCH & RENDER
// ════════════════════════════════════════════════════════════════════════

async function loadDashboard() {
  const platform = document.getElementById("filter-platform").value;
  const keyword  = document.getElementById("filter-keyword").value.trim();

  const params = new URLSearchParams();
  if (platform) params.set("platform", platform);
  if (keyword)  params.set("keyword", keyword);

  const url = `/api/dashboard?${params.toString()}`;

  try {
    const res  = await fetch(url);
    const data = await res.json();
    renderKPIs(data.stats);
    renderPieChart(data.stats);
    renderLineChart(data.timeline);
    renderPlatformChart(data.posts);
    renderTopChart(data.top_posts);
    renderTable(data.posts);
  } catch (err) {
    console.error("Failed to load dashboard:", err);
  }
}

// ── KPI Cards ─────────────────────────────────────────────────────────
function renderKPIs(stats) {
  document.getElementById("kpi-total").textContent    = stats.total;
  document.getElementById("kpi-positive").textContent = stats.positive;
  document.getElementById("kpi-neutral").textContent  = stats.neutral;
  document.getElementById("kpi-negative").textContent = stats.negative;
  document.getElementById("kpi-positive-pct").textContent = `${stats.positive_pct}%`;
  document.getElementById("kpi-neutral-pct").textContent  = `${stats.neutral_pct}%`;
  document.getElementById("kpi-negative-pct").textContent = `${stats.negative_pct}%`;

  const avg = stats.avg_score;
  const el  = document.getElementById("kpi-avg-score");
  el.textContent = avg;
  el.style.color = avg > 0.05 ? C.pos : avg < -0.05 ? C.neg : C.neu;
}

// ── Pie Chart ──────────────────────────────────────────────────────────
function renderPieChart(stats) {
  const ctx = document.getElementById("chart-pie").getContext("2d");
  if (pieChart) pieChart.destroy();
  pieChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [{
        data: [stats.positive, stats.neutral, stats.negative],
        backgroundColor: [C.pos, C.neu, C.neg],
        borderWidth: 0,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "60%",
      plugins: {
        legend: { position: "bottom", labels: { padding: 16, font: { size: 12 } } },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed} posts`
          }
        }
      }
    }
  });
}

// ── Line Chart (timeline) ──────────────────────────────────────────────
function renderLineChart(timeline) {
  const ctx = document.getElementById("chart-line").getContext("2d");
  if (lineChart) lineChart.destroy();

  const labels   = timeline.map(t => t.date);
  const posData  = timeline.map(t => t.positive);
  const neuData  = timeline.map(t => t.neutral);
  const negData  = timeline.map(t => t.negative);

  lineChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Positive", data: posData, borderColor: C.pos, backgroundColor: "rgba(34,197,94,0.12)", tension: 0.4, fill: true, pointRadius: 4 },
        { label: "Neutral",  data: neuData, borderColor: C.neu, backgroundColor: "rgba(245,158,11,0.12)", tension: 0.4, fill: true, pointRadius: 4 },
        { label: "Negative", data: negData, borderColor: C.neg, backgroundColor: "rgba(239,68,68,0.12)", tension: 0.4, fill: true, pointRadius: 4 },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: { grid: { color: C.grid }, ticks: { color: C.muted } },
        y: { beginAtZero: true, grid: { color: C.grid }, ticks: { color: C.muted, stepSize: 1 } }
      },
      plugins: { legend: { position: "bottom", labels: { padding: 14, font: { size: 12 } } } }
    }
  });
}

// ── Platform Bar Chart ─────────────────────────────────────────────────
function renderPlatformChart(posts) {
  const ctx = document.getElementById("chart-platform").getContext("2d");
  if (platformChart) platformChart.destroy();

  // Count sentiments per platform
  const map = {};
  posts.forEach(p => {
    const pl = p.platform || "Unknown";
    if (!map[pl]) map[pl] = { positive: 0, neutral: 0, negative: 0 };
    map[pl][p.label]++;
  });

  const platforms = Object.keys(map);
  platformChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: platforms,
      datasets: [
        { label: "Positive", data: platforms.map(pl => map[pl].positive), backgroundColor: C.pos, borderRadius: 4 },
        { label: "Neutral",  data: platforms.map(pl => map[pl].neutral),  backgroundColor: C.neu, borderRadius: 4 },
        { label: "Negative", data: platforms.map(pl => map[pl].negative), backgroundColor: C.neg, borderRadius: 4 },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: false, grid: { color: C.grid }, ticks: { color: C.muted } },
        y: { beginAtZero: true, grid: { color: C.grid }, ticks: { color: C.muted, stepSize: 1 } }
      },
      plugins: { legend: { position: "bottom", labels: { padding: 14, font: { size: 12 } } } }
    }
  });
}

// ── Top Posts Horizontal Bar ───────────────────────────────────────────
function renderTopChart(topPosts) {
  const ctx = document.getElementById("chart-top").getContext("2d");
  if (topChart) topChart.destroy();

  const labels = topPosts.map(p => {
    const w = p.text.split(" ").slice(0, 5).join(" ");
    return w.length < p.text.length ? w + "…" : w;
  });

  const colors = topPosts.map(p =>
    p.label === "positive" ? C.pos : p.label === "negative" ? C.neg : C.neu
  );

  topChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Likes",
        data: topPosts.map(p => parseInt(p.likes) || 0),
        backgroundColor: colors,
        borderRadius: 4,
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { beginAtZero: true, grid: { color: C.grid }, ticks: { color: C.muted } },
        y: { grid: { color: "transparent" }, ticks: { color: C.muted, font: { size: 11 } } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => topPosts[items[0].dataIndex].text,
            label: (item) => ` ${item.parsed.x} likes`
          }
        }
      }
    }
  });
}

// ── Posts Table ────────────────────────────────────────────────────────
function renderTable(posts) {
  const tbody = document.getElementById("posts-tbody");
  if (!posts.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="loading-cell">No posts found for this filter.</td></tr>`;
    return;
  }

  tbody.innerHTML = posts.map((p, i) => {
    const platformClass = `platform-${(p.platform || "").toLowerCase()}`;
    const scoreColor = p.label === "positive" ? C.pos : p.label === "negative" ? C.neg : C.neu;
    return `
      <tr>
        <td>${i + 1}</td>
        <td><span class="platform-tag ${platformClass}">${p.platform || "—"}</span></td>
        <td style="color:var(--text);font-size:0.85rem;white-space:nowrap">${p.username || "—"}</td>
        <td>${escHtml(p.text)}</td>
        <td><span class="badge badge-${p.label}">${p.label}</span></td>
        <td style="color:${scoreColor};font-weight:600">${p.score}</td>
        <td>${p.likes || "—"}</td>
      </tr>`;
  }).join("");
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Filter buttons ─────────────────────────────────────────────────────
document.getElementById("btn-filter").addEventListener("click", loadDashboard);
document.getElementById("btn-reset").addEventListener("click", () => {
  document.getElementById("filter-platform").value = "";
  document.getElementById("filter-keyword").value  = "";
  loadDashboard();
});

// ════════════════════════════════════════════════════════════════════════
// 3. ANALYZE TEXT TAB
// ════════════════════════════════════════════════════════════════════════

document.getElementById("btn-analyze").addEventListener("click", async () => {
  const text = document.getElementById("analyze-input").value.trim();
  if (!text) return;

  const btn = document.getElementById("btn-analyze");
  btn.textContent = "Analyzing…";
  btn.disabled = true;

  try {
    const res  = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    renderAnalyzeResult(data);
  } catch (err) {
    console.error(err);
  } finally {
    btn.textContent = "Analyze Sentiment";
    btn.disabled = false;
  }
});

function renderAnalyzeResult(data) {
  const result = document.getElementById("analyze-result");
  result.classList.remove("hidden");

  const badge = document.getElementById("result-badge");
  badge.textContent = `😊 ${data.label}`.replace("positive", "😊 Positive")
                                          .replace("neutral",  "😐 Neutral")
                                          .replace("negative", "😞 Negative");
  badge.className = `result-badge result-${data.label}`;

  const posP = Math.round(data.positive * 100);
  const neuP = Math.round(data.neutral  * 100);
  const negP = Math.round(data.negative * 100);

  document.getElementById("bar-pos").style.width = `${posP}%`;
  document.getElementById("bar-neu").style.width = `${neuP}%`;
  document.getElementById("bar-neg").style.width = `${negP}%`;
  document.getElementById("val-pos").textContent = `${posP}%`;
  document.getElementById("val-neu").textContent = `${neuP}%`;
  document.getElementById("val-neg").textContent = `${negP}%`;
  document.getElementById("compound-val").textContent = data.score;
}

// ════════════════════════════════════════════════════════════════════════
// 4. UPLOAD CSV TAB
// ════════════════════════════════════════════════════════════════════════

const fileInput  = document.getElementById("csv-file-input");
const uploadBtn  = document.getElementById("btn-upload");
const dropZone   = document.getElementById("drop-zone");
const fileNameEl = document.getElementById("file-name-display");

let selectedFile = null;

function setFile(file) {
  selectedFile = file;
  fileNameEl.textContent = file ? file.name : "No file selected";
  uploadBtn.disabled = !file;
}

fileInput.addEventListener("change", () => setFile(fileInput.files[0] || null));

dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file && file.name.endsWith(".csv")) setFile(file);
});

uploadBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  uploadBtn.textContent = "Uploading…";
  uploadBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res  = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (data.error) { alert(data.error); return; }
    renderUploadResult(data);
  } catch (err) {
    console.error(err);
  } finally {
    uploadBtn.textContent = "Upload & Analyze";
    uploadBtn.disabled = false;
  }
});

function renderUploadResult(data) {
  document.getElementById("upload-result").classList.remove("hidden");

  const { stats, posts } = data;

  // Mini KPIs
  const kpiContainer = document.getElementById("upload-kpis");
  kpiContainer.innerHTML = `
    <div class="kpi-card kpi-total"><span class="kpi-label">Total</span><span class="kpi-value">${stats.total}</span></div>
    <div class="kpi-card kpi-pos"><span class="kpi-label">Positive</span><span class="kpi-value">${stats.positive}</span><span class="kpi-pct">${stats.positive_pct}%</span></div>
    <div class="kpi-card kpi-neu"><span class="kpi-label">Neutral</span><span class="kpi-value">${stats.neutral}</span><span class="kpi-pct">${stats.neutral_pct}%</span></div>
    <div class="kpi-card kpi-neg"><span class="kpi-label">Negative</span><span class="kpi-value">${stats.negative}</span><span class="kpi-pct">${stats.negative_pct}%</span></div>
  `;

  // Table
  const tbody = document.getElementById("upload-tbody");
  tbody.innerHTML = posts.map((p, i) => {
    const scoreColor = p.label === "positive" ? C.pos : p.label === "negative" ? C.neg : C.neu;
    return `<tr>
      <td>${i + 1}</td>
      <td>${escHtml(p.text)}</td>
      <td><span class="badge badge-${p.label}">${p.label}</span></td>
      <td style="color:${scoreColor};font-weight:600">${p.score}</td>
    </tr>`;
  }).join("");
}

// ════════════════════════════════════════════════════════════════════════
// 5. INIT
// ════════════════════════════════════════════════════════════════════════
loadDashboard();
