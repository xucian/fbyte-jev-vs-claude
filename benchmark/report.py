#!/usr/bin/env python3
"""Generate the HTML report from results.json."""

import json
import sys
import os

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jev vs Claude — Benchmark Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0f;--bg2:#12121a;--bg3:#1a1a28;
  --text:#e0e0e8;--text2:#8888a0;--border:#2a2a3a;
  --jev:#00f0ff;--opus:#8b5cf6;--sonnet:#f97316;
  --opus-think:#c084fc;--sonnet-think:#fb923c;
  --green:#22c55e;--red:#ef4444;
}
body{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;line-height:1.6;overflow-x:hidden}
h1,h2,h3,.mono{font-family:'JetBrains Mono',monospace}
a{color:var(--jev);text-decoration:none}

.container{max-width:1100px;margin-left:auto;margin-right:auto;padding:0 24px}
#scoreboard{max-width:1280px;margin-left:auto;margin-right:auto}

/* HERO */
.hero{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:40px 20px}
.hero h1{font-size:clamp(1.8rem,5vw,3.2rem);font-weight:700;letter-spacing:-0.02em;margin-bottom:16px;background:linear-gradient(135deg,var(--jev),#a78bfa,var(--sonnet));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero .subtitle{font-size:clamp(0.9rem,2vw,1.15rem);color:var(--text2);overflow:hidden;white-space:nowrap;border-right:2px solid var(--jev);width:0;animation:typing 2.5s steps(52) 0.8s forwards,blink 0.7s step-end infinite}
@keyframes typing{to{width:100%}}
@keyframes blink{50%{border-color:transparent}}
.hero .meta{margin-top:32px;display:flex;gap:24px;flex-wrap:wrap;justify-content:center}
.hero .meta-item{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:12px 20px;text-align:center}
.hero .meta-item .num{font-family:'JetBrains Mono',monospace;font-size:1.6rem;font-weight:700}
.hero .meta-item .label{font-size:0.75rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.1em}

/* SECTIONS */
section{padding:60px 0;margin-bottom:40px}
section h2{font-size:1.6rem;margin-bottom:8px}
section .section-sub{color:var(--text2);margin-bottom:40px;font-size:0.95rem}

/* ANIMATE IN */
.animate-in{opacity:0;transform:translateY(30px);transition:opacity 0.6s ease,transform 0.6s ease}
.animate-in.visible{opacity:1;transform:translateY(0)}

/* TASK CARD */
.task-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:28px;margin-bottom:32px}
.task-card:last-child{margin-bottom:0}
.task-card .task-header{display:flex;align-items:center;gap:12px;margin-bottom:20px}
.task-card .task-emoji{font-size:1.8rem}
.task-card .task-name{font-size:1.1rem;font-weight:600}
.task-card .task-tag{font-size:0.75rem;color:var(--text2);background:var(--bg3);padding:3px 10px;border-radius:20px;margin-left:auto}

/* BAR CHART */
.bar-group{display:flex;flex-direction:column;gap:10px}
.bar-row{display:flex;align-items:center;gap:12px}
.bar-label{width:110px;font-size:0.8rem;font-family:'JetBrains Mono',monospace;text-align:right;flex-shrink:0}
.bar-track{flex:1;height:32px;background:var(--bg);border-radius:6px;position:relative}
.bar-fill{height:100%;border-radius:6px;display:flex;align-items:center;padding:0 12px;font-size:0.8rem;font-family:'JetBrains Mono',monospace;font-weight:600;color:#000;width:0;transition:width 1s cubic-bezier(0.22,1,0.36,1);position:relative;overflow:hidden;white-space:nowrap}
.bar-fill.jev{background:var(--jev)}
.bar-fill.opus{background:var(--opus);color:#fff}
.bar-fill.sonnet{background:var(--sonnet);color:#000}
.bar-fill.opus-think{background:var(--opus-think);color:#000}
.bar-fill.sonnet-think{background:var(--sonnet-think);color:#000}
.bar-fill.winner{box-shadow:0 0 20px rgba(255,255,255,0.2)}
.bar-val-out{position:absolute;left:0;top:0;height:32px;display:flex;align-items:center;font-size:0.8rem;font-family:'JetBrains Mono',monospace;font-weight:600;white-space:nowrap;padding-left:8px;opacity:0;transition:opacity 0.6s 0.8s}

/* CALIBRATION PLOT */
.cal-plot{width:100%;max-width:600px;margin:0 auto}
.cal-plot svg{width:100%;height:auto}

/* SPEED BARS */
.speed-note{color:var(--text2);font-size:0.85rem;font-style:italic;text-align:center;margin-bottom:24px}

/* COST */
.cost-callout{text-align:center;background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:24px;margin-top:20px}
.cost-callout .big{font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:var(--jev)}

/* SCOREBOARD */
.scoreboard{width:100%;border-collapse:collapse;font-size:0.85rem}
.scoreboard th{background:var(--bg3);padding:10px 12px;text-align:center;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--text2);position:sticky;top:0}
.scoreboard td{padding:10px 12px;text-align:center;border-bottom:1px solid var(--border);color:var(--text2)}
.scoreboard tr:hover td{background:var(--bg2)}
.scoreboard .task-col{text-align:left;font-weight:600;white-space:nowrap;min-width:150px}
.cell-best{color:#fff;font-weight:700;background:rgba(34,197,94,0.25)}
.cell-worst{color:var(--red)}
.tab-bar{display:flex;justify-content:center;gap:4px;margin-top:16px}
.tab-btn{background:var(--bg3);border:1px solid var(--border);border-radius:6px;padding:6px 20px;color:var(--text2);font-size:0.8rem;font-family:'JetBrains Mono',monospace;cursor:pointer;transition:all 0.2s}
.tab-btn:hover{border-color:var(--text2)}
.tab-btn.active{background:var(--border);color:var(--text);border-color:var(--text2)}

/* VERDICT */
.verdict{text-align:center;padding:60px 20px}
.verdict .crown{font-size:4rem;margin-bottom:16px}
.verdict .winner-name{font-size:2rem;font-weight:700;margin-bottom:8px}
.verdict .verdict-line{color:var(--text2);font-size:1rem}
.awards{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-top:32px}
.award{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px 24px;text-align:center;min-width:160px}
.award .award-emoji{font-size:2rem}
.award .award-label{font-size:0.75rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.08em;margin:8px 0 4px}
.award .award-winner{font-weight:700;font-size:0.95rem}

/* TASK LINEUP */
.lineup{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:0}
.lineup-item{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:16px 18px}
.lineup-item .li-top{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.lineup-item .li-emoji{font-size:1.3rem}
.lineup-item .li-name{font-weight:600;font-size:0.9rem}
.lineup-item .li-desc{color:var(--text2);font-size:0.78rem;line-height:1.45}

/* TAKEAWAY */
.takeaway-body{display:flex;flex-direction:column;gap:20px}
.takeaway-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:28px}
.takeaway-card .takeaway-icon{font-size:1.6rem;margin-bottom:10px}
.takeaway-card h3{font-size:1rem;font-weight:600;margin-bottom:10px;font-family:'JetBrains Mono',monospace}
.takeaway-card p{color:var(--text2);font-size:0.9rem;line-height:1.7}
.takeaway-card em{color:var(--text);font-style:italic}

/* LEGEND */
.legend{display:flex;gap:20px;justify-content:center;margin-bottom:24px;flex-wrap:wrap}
.legend-item{display:flex;align-items:center;gap:6px;font-size:0.8rem}
.legend-dot{width:12px;height:12px;border-radius:3px}

/* RESPONSIVE */
@media(max-width:600px){
  .hero h1{font-size:1.6rem}
  .bar-label{width:80px;font-size:0.7rem}
  .awards{flex-direction:column;align-items:center}
}
</style>
</head>
<body>

<!-- HERO -->
<section class="hero">
  <h1>CAN A MUTE MODEL BEAT THE LOUDEST LLMs?</h1>
  <div style="display:inline-block;max-width:700px">
    <p class="subtitle" id="subtitle"></p>
  </div>
  <div class="meta" id="hero-meta"></div>
</section>

<!-- TASK LINEUP -->
<section class="container animate-in" id="lineup">
  <h2>The Lineup</h2>
  <p class="section-sub">What each task actually measures</p>
  <div class="lineup">
    <div class="lineup-item"><div class="li-top"><span class="li-emoji">&#x1F6AA;</span><span class="li-name">Bouncer</span></div><div class="li-desc">Route customer messages to the right department. One label, no hedging.</div></div>
    <div class="lineup-item"><div class="li-top"><span class="li-emoji">&#x1F50D;</span><span class="li-name">Lie Detector</span></div><div class="li-desc">Spot fake reviews, read sentiment, and flag PII &mdash; three judgments per review.</div></div>
    <div class="lineup-item"><div class="li-top"><span class="li-emoji">&#x1F52E;</span><span class="li-name">Oracle</span></div><div class="li-desc">Triage bug reports: priority, component, and whether it&rsquo;s a regression.</div></div>
    <div class="lineup-item"><div class="li-top"><span class="li-emoji">&#x1F378;</span><span class="li-name">Bartender</span></div><div class="li-desc">Moderate user comments: toxic or not, what kind, and how severe.</div></div>
    <div class="lineup-item"><div class="li-top"><span class="li-emoji">&#x1F6C2;</span><span class="li-name">Customs Agent</span></div><div class="li-desc">Classify contract clauses, assess risk, and flag ones that need a lawyer.</div></div>
  </div>
</section>

<!-- ACCURACY GAUNTLET -->
<section class="container animate-in" id="accuracy">
  <h2>The Accuracy Gauntlet</h2>
  <p class="section-sub">5 tasks. 3 models. 20 cases each. No softballs.</p>
  <div class="legend" id="accuracy-legend"></div>
  <div id="accuracy-cards"></div>
</section>

<!-- CALIBRATION -->
<section class="container animate-in" id="calibration">
  <h2>Confidence vs Reality</h2>
  <p class="section-sub">Are they as good as they think they are?</p>
  <div class="legend" id="cal-legend"></div>
  <div class="cal-plot" id="cal-plot"></div>
</section>

<!-- SPEED -->
<section class="container animate-in" id="speed">
  <h2>Speed Race</h2>
  <p class="section-sub">Median latency per task</p>
  <p class="speed-note">"Speed matters too."</p>
  <div id="speed-cards"></div>
</section>

<!-- COST -->
<section class="container animate-in" id="cost">
  <h2>The Money Shot</h2>
  <p class="section-sub">Total cost per task (USD)</p>
  <div id="cost-cards"></div>
  <div class="cost-callout" id="cost-callout"></div>
</section>

<!-- SCOREBOARD -->
<section class="container animate-in" id="scoreboard">
  <h2>Scoreboard</h2>
  <p class="section-sub">Every number, one table</p>
  <div style="overflow-x:auto"><table class="scoreboard" id="scoreboard-table"></table></div>
  <div class="tab-bar">
    <button class="tab-btn active" data-mode="simple" onclick="switchScoreboardTab('simple',this)">Simple</button>
    <button class="tab-btn" data-mode="detailed" onclick="switchScoreboardTab('detailed',this)">Detailed</button>
  </div>
</section>

<!-- VERDICT -->
<section class="verdict animate-in" id="verdict"></section>

<!-- TAKEAWAY -->
<section class="container animate-in" id="takeaway">
  <h2>Why Does Sonnet Beat Opus?</h2>
  <p class="section-sub">September 18, 2026 &mdash; General observations on model selection for structured tasks</p>
  <div class="takeaway-body">
    <div class="section-sub">
      <h3>Classification is pattern matching, not reasoning</h3>
      <p>Every task here has the same shape: read a short text, match it to a label or score, output JSON. The right answer is almost always obvious from surface signals &mdash; the words, the tone, the structure. There is no multi-step logic chain to follow. Opus&rsquo;s extra capacity is built for reasoning depth &mdash; holding complex chains of logic, synthesizing across long documents, making judgment calls where the answer isn&rsquo;t in any single sentence. That machinery doesn&rsquo;t help when the task is &ldquo;this message says <em>I want to integrate your API</em> &mdash; is it sales or technical?&rdquo;</p>
    </div>
    <div class="section-sub">
      <h3>Thinking made it worse</h3>
      <p>The adaptive-thinking results are the smoking gun. Sonnet <em>lost</em> accuracy with thinking enabled &mdash; its first instinct was already correct, and the reasoning step introduced second-guessing. Opus barely moved. These tasks don&rsquo;t have enough ambiguity to reason <em>about</em>. It&rsquo;s like asking a chess grandmaster to play tic-tac-toe &mdash; they won&rsquo;t play it better than someone who memorized the three rules.</p>
    </div>
    <div class="section-sub">
      <h3>Model hierarchy isn&rsquo;t a straight line</h3>
      <p>Opus &gt; Sonnet &gt; Haiku is true for <em>reasoning ceiling</em>, not for every task. Opus shines on multi-file code reasoning, long-context synthesis, architectural planning, and agent loops where each decision compounds. For structured classification at volume, Sonnet is the right pick. And Jev gets you most of the way there for a fraction of the cost. Picking the right model for the job is itself the smartest decision.</p>
    </div>
  </div>
</section>

<script>
const RESULTS = __RESULTS_JSON__;

const TASK_META = {
  bouncer:       {name:"Bouncer",       emoji:"\u{1F6AA}", tagline:"Intent Routing"},
  lie_detector:  {name:"Lie Detector",  emoji:"\u{1F50D}", tagline:"Fake Review Detection"},
  oracle:        {name:"Oracle",        emoji:"\u{1F52E}", tagline:"Bug Triage"},
  bartender:     {name:"Bartender",     emoji:"\u{1F378}", tagline:"Content Moderation"},
  customs_agent: {name:"Customs Agent", emoji:"\u{1F6C2}", tagline:"Contract Clauses"},
};
const MODEL_COLORS = {jev:"var(--jev)", opus:"var(--opus)", sonnet:"var(--sonnet)", "opus-think":"var(--opus-think)", "sonnet-think":"var(--sonnet-think)"};
const MODEL_LABELS = {jev:"Jev", opus:"Opus 4.6", sonnet:"Sonnet 4.6", "opus-think":"Opus 4.6 \u{1F9E0}", "sonnet-think":"Sonnet 4.6 \u{1F9E0}"};
const TASK_ORDER = ["bouncer","lie_detector","oracle","bartender","customs_agent"];
const ALL_MODELS = ["jev","opus","sonnet","opus-think","sonnet-think"];
const MODEL_ORDER = ALL_MODELS.filter(m => RESULTS.some(r => r.model === m));

function lookup(model, task) {
  return RESULTS.find(r => r.model === model && r.task === task);
}

function buildLegend(targetId, suffix) {
  const el = document.getElementById(targetId);
  if(!el) return;
  el.innerHTML = MODEL_ORDER.map(m =>
    `<div class="legend-item"><div class="legend-dot" style="background:${MODEL_COLORS[m]}"></div>${MODEL_LABELS[m]}${suffix?suffix(m):""}</div>`
  ).join("");
}

function fmt(n, d=1) { return n == null ? "—" : (n*100).toFixed(d)+"%"; }
function fmtMs(n)    { return n == null ? "—" : Math.round(n)+"ms"; }
function fmtCost(n)  { return n == null ? "—" : "$"+n.toFixed(6); }

const MODEL_CSS_COLORS = {jev:"#00f0ff", opus:"#8b5cf6", sonnet:"#f97316", "opus-think":"#c084fc", "sonnet-think":"#fb923c"};
function makeBar(model, pct, label, extraClass) {
  const narrow = pct < 15;
  const barText = narrow ? "" : label;
  const outside = narrow
    ? `<span class="bar-val-out" style="left:${pct}%;color:${MODEL_CSS_COLORS[model]}">${label}</span>`
    : "";
  return `<div class="bar-row">
    <span class="bar-label">${MODEL_LABELS[model]}</span>
    <div class="bar-track">
      <div class="bar-fill ${model}${extraClass}" data-width="${pct}%">${barText}</div>${outside}
    </div>
  </div>`;
}

// HERO
(function renderHero(){
  const sub = document.getElementById("subtitle");
  const models = [...new Set(RESULTS.map(r=>MODEL_LABELS[r.model]))];
  const text = models.join(" vs ") + ` · 5 tasks · ${RESULTS.length} runs · 1 truth`;
  sub.textContent = text;
  sub.style.setProperty("--chars", text.length);

  const meta = document.getElementById("hero-meta");
  const totalCases = RESULTS.reduce((s,r) => s + r.cases.length, 0);
  const totalCost  = RESULTS.reduce((s,r) => s + r.summary.total_cost_usd, 0);
  const items = [
    {num: RESULTS.length, label:"Runs"},
    {num: totalCases, label:"Predictions"},
    {num: "$"+totalCost.toFixed(4), label:"Total Cost"},
  ];
  meta.innerHTML = items.map(i =>
    `<div class="meta-item"><div class="num">${i.num}</div><div class="label">${i.label}</div></div>`
  ).join("");
})();

// ACCURACY
(function renderAccuracy(){
  buildLegend("accuracy-legend");
  const container = document.getElementById("accuracy-cards");
  TASK_ORDER.forEach(slug => {
    const m = TASK_META[slug];
    const accs = {};
    MODEL_ORDER.forEach(model => {
      const r = lookup(model, slug);
      accs[model] = r ? r.summary.accuracy : null;
    });
    const best = Math.max(...Object.values(accs).filter(v=>v!=null));

    let html = `<div class="task-card"><div class="task-header">
      <span class="task-emoji">${m.emoji}</span>
      <span class="task-name">${m.name}</span>
      <span class="task-tag">${m.tagline}</span>
    </div><div class="bar-group">`;

    MODEL_ORDER.forEach(model => {
      const pct = accs[model] != null ? accs[model]*100 : 0;
      const isWinner = accs[model] === best;
      html += makeBar(model, pct, pct.toFixed(1)+"%", isWinner?" winner":"");
    });

    html += `</div></div>`;
    container.innerHTML += html;
  });
})();

// CALIBRATION
(function renderCalibration(){
  buildLegend("cal-legend", m => m==="jev"?" (calibrated)":" (self-reported)");
  const W=560, H=400, P=50, PR=30;
  const pw=W-P-PR, ph=H-P-P;

  let svg = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
  svg += `<rect width="${W}" height="${H}" fill="var(--bg2)" rx="8"/>`;

  // grid
  for(let i=0;i<=5;i++){
    const x=P+pw*i/5, y=P+ph-ph*i/5;
    svg += `<line x1="${P}" y1="${y}" x2="${P+pw}" y2="${y}" stroke="var(--border)" stroke-width="0.5"/>`;
    svg += `<line x1="${x}" y1="${P}" x2="${x}" y2="${P+ph}" stroke="var(--border)" stroke-width="0.5"/>`;
    svg += `<text x="${x}" y="${P+ph+18}" text-anchor="middle" fill="var(--text2)" font-size="11" font-family="JetBrains Mono">${(i*20)}%</text>`;
    svg += `<text x="${P-8}" y="${y+4}" text-anchor="end" fill="var(--text2)" font-size="11" font-family="JetBrains Mono">${(i*20)}%</text>`;
  }

  // diagonal (perfect)
  svg += `<line x1="${P}" y1="${P+ph}" x2="${P+pw}" y2="${P}" stroke="#444" stroke-width="1.5" stroke-dasharray="6,4"/>`;
  svg += `<text x="${P+pw-4}" y="${P+16}" text-anchor="end" fill="#555" font-size="10" font-family="Inter">Perfect</text>`;

  // axis labels
  svg += `<text x="${P+pw/2}" y="${H-6}" text-anchor="middle" fill="var(--text2)" font-size="12" font-family="Inter">Reported Confidence</text>`;
  svg += `<text x="14" y="${P+ph/2}" text-anchor="middle" fill="var(--text2)" font-size="12" font-family="Inter" transform="rotate(-90,14,${P+ph/2})">Actual Accuracy</text>`;

  // per-model curves
  MODEL_ORDER.forEach(model => {
    const allCurve = [];
    TASK_ORDER.forEach(slug => {
      const r = lookup(model, slug);
      if(r && r.summary.calibration_curve) allCurve.push(...r.summary.calibration_curve);
    });

    const bins = {};
    allCurve.filter(pt => pt.count > 0 && pt.avg_confidence != null).forEach(pt => {
      const k = pt.bin_center.toFixed(2);
      if(!bins[k]) bins[k] = {conf:0, acc:0, n:0};
      bins[k].conf += pt.avg_confidence * pt.count;
      bins[k].acc  += pt.avg_accuracy * pt.count;
      bins[k].n    += pt.count;
    });

    const points = Object.values(bins).filter(b=>b.n>0).map(b=>({
      x: P + (b.conf/b.n) * pw,
      y: P + ph - (b.acc/b.n) * ph
    }));

    const colorMap = MODEL_COLORS;

    if(points.length > 1){
      const d = points.map((p,i)=>( i===0?"M":"L")+p.x.toFixed(1)+","+p.y.toFixed(1)).join(" ");
      svg += `<path d="${d}" fill="none" stroke="${colorMap[model]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`;
    }
    points.forEach(p => {
      svg += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="5" fill="${colorMap[model]}" stroke="var(--bg)" stroke-width="2"/>`;
    });
  });

  svg += `</svg>`;
  document.getElementById("cal-plot").innerHTML = svg;
})();

// SPEED
(function renderSpeed(){
  const container = document.getElementById("speed-cards");
  TASK_ORDER.forEach(slug => {
    const m = TASK_META[slug];
    const lats = {};
    let maxLat = 0;
    MODEL_ORDER.forEach(model => {
      const r = lookup(model, slug);
      lats[model] = r ? r.summary.median_latency_ms : null;
      if(lats[model] > maxLat) maxLat = lats[model];
    });

    let html = `<div class="task-card"><div class="task-header">
      <span class="task-emoji">${m.emoji}</span>
      <span class="task-name">${m.name}</span>
    </div><div class="bar-group">`;

    MODEL_ORDER.forEach(model => {
      const ms = lats[model];
      const pct = maxLat > 0 && ms != null ? (ms/maxLat)*100 : 0;
      const fastest = ms === Math.min(...Object.values(lats).filter(v=>v!=null));
      html += makeBar(model, pct, Math.round(ms||0)+"ms", fastest?" winner":"");
    });

    html += `</div></div>`;
    container.innerHTML += html;
  });
})();

// COST
(function renderCost(){
  const container = document.getElementById("cost-cards");
  const totals = {};
  MODEL_ORDER.forEach(m => totals[m] = 0);

  TASK_ORDER.forEach(slug => {
    const m = TASK_META[slug];
    const costs = {};
    let maxCost = 0;
    MODEL_ORDER.forEach(model => {
      const r = lookup(model, slug);
      costs[model] = r ? r.summary.total_cost_usd : null;
      if(costs[model] > maxCost) maxCost = costs[model];
    });

    MODEL_ORDER.forEach(model => { if(costs[model] != null) totals[model] += costs[model]; });

    let html = `<div class="task-card"><div class="task-header">
      <span class="task-emoji">${m.emoji}</span>
      <span class="task-name">${m.name}</span>
    </div><div class="bar-group">`;

    MODEL_ORDER.forEach(model => {
      const c = costs[model];
      const pct = maxCost > 0 && c != null ? Math.max((c / maxCost) * 100, 3) : 0;
      const cheapest = c === Math.min(...Object.values(costs).filter(v=>v!=null));
      html += makeBar(model, pct, fmtCost(c), cheapest?" winner":"");
    });

    html += `</div></div>`;
    container.innerHTML += html;
  });

  const callout = document.getElementById("cost-callout");
  const jevTotal = totals.jev || 0;
  const mostExpensive = MODEL_ORDER.reduce((a,b) => totals[a]>=totals[b]?a:b);
  if(jevTotal > 0 && totals[mostExpensive] > 0){
    const mult = Math.round(totals[mostExpensive] / jevTotal);
    const parts = MODEL_ORDER.filter(m=>m!=="jev"&&totals[m]>0).map(m=>`1 ${MODEL_LABELS[m]} = <strong>${Math.round(totals[m]/jevTotal)}x</strong> Jev`);
    callout.innerHTML = `<div class="big">${mult}x</div><div style="color:var(--text2)">For the price of 1 ${MODEL_LABELS[mostExpensive]} run, Jev runs <strong>${mult} times</strong></div><div style="color:var(--text2);margin-top:8px">${parts.join(" · ")}</div>`;
  }
})();

// SCOREBOARD
function renderScoreboard(mode) {
  const table = document.getElementById("scoreboard-table");
  const simple = mode === 'simple';
  const colCount = simple ? 2 : 4;

  let html = `<thead><tr>
    <th>Task</th>
    ${MODEL_ORDER.map(m=>`<th colspan="${colCount}">${MODEL_LABELS[m]}</th>`).join("")}
  </tr><tr>
    <th></th>
    ${MODEL_ORDER.map(()=> simple
      ? `<th>Acc</th><th>Cost</th>`
      : `<th>Acc</th><th>Conf</th><th>Lat</th><th>Cost</th>`
    ).join("")}
  </tr></thead><tbody>`;

  TASK_ORDER.forEach(slug => {
    const m = TASK_META[slug];
    html += `<tr><td class="task-col">${m.emoji} ${m.name}</td>`;

    const vals = {};
    MODEL_ORDER.forEach(model => {
      const r = lookup(model, slug);
      vals[model] = r ? r.summary : null;
    });

    const accs = MODEL_ORDER.map(m => vals[m]?.accuracy).filter(v=>v!=null);
    const bestAcc = Math.max(...accs);
    const worstAcc = Math.min(...accs);

    MODEL_ORDER.forEach(model => {
      const s = vals[model];
      if(!s){ html += simple ? `<td>—</td><td>—</td>` : `<td>—</td><td>—</td><td>—</td><td>—</td>`; return; }
      const accClass = s.accuracy===bestAcc?"cell-best":s.accuracy===worstAcc?"cell-worst":"";
      html += `<td class="${accClass}">${fmt(s.accuracy)}</td>`;
      if(!simple) {
        html += `<td>${fmt(s.mean_confidence)}</td>`;
        html += `<td>${fmtMs(s.median_latency_ms)}</td>`;
      }
      html += `<td>${fmtCost(s.total_cost_usd)}</td>`;
    });
    html += `</tr>`;
  });

  const avgs = {};
  MODEL_ORDER.forEach(model => {
    const runs = RESULTS.filter(r=>r.model===model);
    const n = runs.length || 1;
    avgs[model] = {
      accuracy: runs.reduce((s,r)=>s+r.summary.accuracy,0)/n,
      mean_confidence: runs.reduce((s,r)=>s+r.summary.mean_confidence,0)/n,
      median_latency_ms: runs.reduce((s,r)=>s+r.summary.median_latency_ms,0)/n,
      total_cost_usd: runs.reduce((s,r)=>s+r.summary.total_cost_usd,0),
    };
  });
  const avgAccs = MODEL_ORDER.map(m=>avgs[m].accuracy);
  const bestAvgAcc = Math.max(...avgAccs);
  const worstAvgAcc = Math.min(...avgAccs);

  html += `<tr style="border-top:2px solid var(--text2)"><td class="task-col">Average</td>`;
  MODEL_ORDER.forEach(model => {
    const a = avgs[model];
    const accClass = a.accuracy===bestAvgAcc?"cell-best":a.accuracy===worstAvgAcc?"cell-worst":"";
    html += `<td class="${accClass}" style="font-weight:700">${fmt(a.accuracy)}</td>`;
    if(!simple) {
      html += `<td style="font-weight:700">${fmt(a.mean_confidence)}</td>`;
      html += `<td style="font-weight:700">${fmtMs(a.median_latency_ms)}</td>`;
    }
    html += `<td style="font-weight:700">${fmtCost(a.total_cost_usd)}</td>`;
  });
  html += `</tr>`;

  html += `</tbody>`;
  table.innerHTML = html;
}

function switchScoreboardTab(mode, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderScoreboard(mode);
}

renderScoreboard('simple');

// VALUE CARD helper — cents per accuracy point (lower = better, linear)
function renderValueCard(meanAcc, totalCost) {
  const cppMap = {};
  MODEL_ORDER.forEach(m => {
    const cents = totalCost[m] * 100;
    cppMap[m] = (meanAcc[m] * 100) > 0 ? cents / (meanAcc[m] * 100) : 0;
  });

  const sorted = MODEL_ORDER.slice().sort((a,b)=>cppMap[a]-cppMap[b]);
  const maxVal = Math.max(...sorted.map(m=>cppMap[m]));
  const minVal = Math.min(...sorted.map(m=>cppMap[m]));

  let bars = "";
  sorted.forEach(m => {
    const val = cppMap[m];
    const pct = maxVal > 0 ? (val / maxVal) * 100 : 0;
    const label = val >= 0.01 ? val.toFixed(2) + "¢/pt" : val.toFixed(4) + "¢/pt";
    bars += makeBar(m, Math.max(pct, 3), label, val === minVal ? " winner" : "");
  });

  return `<div style="margin:40px auto 0;background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:28px">
    <div style="text-align:center;margin-bottom:20px">
      <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--text2);margin-bottom:6px">Cost per Accuracy Point</div>
      <div style="font-size:0.85rem;color:var(--text2)">Lower is better. 1 point means e.g. going from 85% to 86% (this does not scale linearly, i know, but still)</div>
    </div>
    <div class="bar-group">${bars}</div>
  </div>`;
}

// VERDICT
(function renderVerdict(){
  const section = document.getElementById("verdict");
  const meanAcc = {}, totalCost = {}, totalEce = {}, totalLat = {};
  MODEL_ORDER.forEach(model => {
    const runs = RESULTS.filter(r=>r.model===model);
    meanAcc[model] = runs.reduce((s,r)=>s+r.summary.accuracy,0) / (runs.length||1);
    totalCost[model] = runs.reduce((s,r)=>s+r.summary.total_cost_usd,0);
    totalEce[model] = runs.reduce((s,r)=>s+r.summary.calibration_error,0) / (runs.length||1);
    totalLat[model] = runs.reduce((s,r)=>s+r.summary.median_latency_ms,0) / (runs.length||1);
  });

  const bestAccModel    = MODEL_ORDER.reduce((a,b)=>meanAcc[a]>=meanAcc[b]?a:b);
  const bestCalModel    = MODEL_ORDER.reduce((a,b)=>totalEce[a]<=totalEce[b]?a:b);
  const bestValueModel  = MODEL_ORDER.reduce((a,b)=>(meanAcc[a]/(totalCost[a]||1e-9))>=(meanAcc[b]/(totalCost[b]||1e-9))?a:b);
  const bestSpeedModel  = MODEL_ORDER.reduce((a,b)=>totalLat[a]<=totalLat[b]?a:b);

  section.innerHTML = `
    <div class="crown">\u{1F3C6}</div>
    <div class="winner-name" style="color:${MODEL_COLORS[bestAccModel]}">${MODEL_LABELS[bestAccModel]}</div>
    <div class="verdict-line">Highest mean accuracy across all 5 tasks: ${fmt(meanAcc[bestAccModel])}</div>
    <div class="awards">
      <div class="award"><div class="award-emoji">\u{1F3C6}</div><div class="award-label">Best Accuracy</div><div class="award-winner" style="color:${MODEL_COLORS[bestAccModel]}">${MODEL_LABELS[bestAccModel]}</div></div>
      <div class="award"><div class="award-emoji">\u{1F4B8}</div><div class="award-label">Efficiency King</div><div class="award-winner" style="color:${MODEL_COLORS[bestValueModel]}">${MODEL_LABELS[bestValueModel]}</div></div>
      <div class="award"><div class="award-emoji">\u{1F3AF}</div><div class="award-label">Best Calibration</div><div class="award-winner" style="color:${MODEL_COLORS[bestCalModel]}">${MODEL_LABELS[bestCalModel]}</div></div>
      <div class="award"><div class="award-emoji">\u{26A1}</div><div class="award-label">Speed Demon</div><div class="award-winner" style="color:${MODEL_COLORS[bestSpeedModel]}">${MODEL_LABELS[bestSpeedModel]}</div></div>
    </div>
    ${renderValueCard(meanAcc, totalCost)}
  `;
})();

// SCROLL ANIMATIONS + BAR GROWTH
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if(e.isIntersecting){
      e.target.classList.add("visible");
      e.target.querySelectorAll(".bar-fill[data-width]").forEach(bar => {
        setTimeout(() => { bar.style.width = bar.dataset.width; }, 100);
      });
      e.target.querySelectorAll(".bar-val-out").forEach(el => {
        setTimeout(() => { el.style.opacity = "1"; }, 100);
      });
      observer.unobserve(e.target);
    }
  });
}, {threshold: 0.15});

document.querySelectorAll(".animate-in").forEach(el => observer.observe(el));
</script>
</body>
</html>"""


def main():
    results_path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "report.html"

    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found. Run `python run.py` first.")
        sys.exit(1)

    with open(results_path) as f:
        results = json.load(f)

    html = HTML_TEMPLATE.replace("__RESULTS_JSON__", json.dumps(results, default=str))

    with open(output_path, "w") as f:
        f.write(html)

    print(f"Report generated: {output_path}")
    print(f"  {len(results)} runs embedded")


if __name__ == "__main__":
    main()
