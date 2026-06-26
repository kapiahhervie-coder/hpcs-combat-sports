path = r'combat\templates\combat\report_card.html'

# Baca file asli untuk ambil bagian script chart
with open(path, 'r', encoding='utf-8') as f:
    old = f.read()

# Ambil script chart yang sudah ada
import re
script_match = re.search(r'(<script>.*?</script>)', old, re.DOTALL)
chart_script = script_match.group(1) if script_match else ''

NEW_HTML = '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HPCS — Athlete Performance Report</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  body {
    font-family: 'Inter', sans-serif;
    background: #05080f;
    color: #e2e8f0;
    min-height: 100vh;
  }

  /* ── Garis dekoratif atas ── */
  .top-rule {
    height: 3px;
    background: linear-gradient(90deg, #b45309 0%, #f59e0b 40%, #fcd34d 60%, #b45309 100%);
    margin-bottom: 0;
  }

  /* ── Header ── */
  .report-header {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f1629 100%);
    border-bottom: 1px solid rgba(245,158,11,0.15);
    padding: 28px 40px 24px;
  }
  .brand-logo {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #b45309, #f59e0b);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 18px; color: #000;
    flex-shrink: 0;
  }
  .report-title {
    font-size: 28px; font-weight: 800;
    letter-spacing: -0.5px; color: #fff;
    line-height: 1;
  }
  .report-title span { color: #f59e0b; }
  .report-meta {
    font-size: 9px; letter-spacing: 2px;
    color: #475569; text-transform: uppercase; font-weight: 600;
  }
  .meta-value { color: #f59e0b; font-weight: 700; font-size: 11px; }
  .report-id { color: #475569; font-family: 'DM Mono', monospace; font-size: 10px; }

  /* ── Kartu utama ── */
  .card {
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
  }
  .card-premium {
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    border: 1px solid rgba(245,158,11,0.12);
    border-radius: 12px;
  }
  .section-label {
    font-size: 9px; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: #f59e0b; margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
  }
  .section-label::after {
    content: ''; flex: 1; height: 1px;
    background: rgba(245,158,11,0.15);
  }

  /* ── Combat Readiness ── */
  .readiness-score {
    font-size: 72px; font-weight: 900;
    color: #fff; line-height: 1;
    letter-spacing: -2px;
    font-variant-numeric: tabular-nums;
  }
  .readiness-bar {
    height: 6px; border-radius: 3px;
    background: rgba(255,255,255,0.06);
    overflow: hidden; margin-top: 16px;
  }
  .readiness-fill {
    height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, #b45309, #f59e0b, #fcd34d);
    transition: width 1s ease;
  }

  /* ── Biodata ── */
  .bio-name {
    font-size: 32px; font-weight: 900;
    color: #fff; letter-spacing: -0.5px;
    line-height: 1; text-transform: uppercase;
  }
  .bio-sport {
    font-size: 10px; font-weight: 700;
    letter-spacing: 3px; color: #f59e0b;
    text-transform: uppercase; margin-top: 4px;
  }
  .bio-divider {
    height: 1px; background: rgba(255,255,255,0.06);
    margin: 16px 0;
  }
  .bio-row {
    display: flex; justify-content: space-between;
    align-items: center; padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
  }
  .bio-label {
    font-size: 9px; font-weight: 600;
    letter-spacing: 1.5px; color: #475569;
    text-transform: uppercase;
  }
  .bio-value {
    font-size: 12px; font-weight: 600; color: #cbd5e1;
  }
  .bio-value-accent { color: #f59e0b !important; font-weight: 700; }

  /* ── DNA Card ── */
  .dna-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 6px; padding: 6px 12px;
    font-size: 12px; font-weight: 700;
    color: #f59e0b; letter-spacing: 0.5px;
  }
  .risk-dot {
    width: 8px; height: 8px; border-radius: 50%;
    display: inline-block; margin-right: 6px;
  }
  .risk-low { background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.6); }
  .risk-mid { background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.6); }
  .risk-high { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.6); }

  /* ── Score pills per level ── */
  .level-scores {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
    margin: 16px 0;
  }
  .level-pill {
    padding: 10px 8px; border-radius: 8px; text-align: center;
    border: 1px solid rgba(255,255,255,0.06);
  }
  .level-pill .lp-label {
    font-size: 8px; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #475569; display: block; margin-bottom: 4px;
  }
  .level-pill .lp-score {
    font-size: 20px; font-weight: 800;
    font-family: 'DM Mono', monospace; line-height: 1;
  }
  .level-pill .lp-pred {
    font-size: 8px; font-weight: 700;
    letter-spacing: 1px; display: block; margin-top: 3px;
  }
  .lp-l1 { border-color: rgba(0,210,255,0.2); background: rgba(0,210,255,0.04); }
  .lp-l1 .lp-score { color: #00d2ff; }
  .lp-l1 .lp-pred { color: rgba(0,210,255,0.6); }
  .lp-l2 { border-color: rgba(0,229,176,0.2); background: rgba(0,229,176,0.04); }
  .lp-l2 .lp-score { color: #00e5b0; }
  .lp-l2 .lp-pred { color: rgba(0,229,176,0.6); }
  .lp-l3 { border-color: rgba(251,191,36,0.2); background: rgba(251,191,36,0.04); }
  .lp-l3 .lp-score { color: #fbbf24; }
  .lp-l3 .lp-pred { color: rgba(251,191,36,0.6); }
  .lp-l4 { border-color: rgba(232,121,249,0.2); background: rgba(232,121,249,0.04); }
  .lp-l4 .lp-score { color: #e879f9; }
  .lp-l4 .lp-pred { color: rgba(232,121,249,0.6); }

  /* ── Analytic cards ── */
  .analytic-card {
    padding: 20px; border-radius: 10px;
    background: #0d1117;
  }
  .analytic-title {
    font-size: 9px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
  }
  .analytic-title::before {
    content: ''; width: 3px; height: 14px; border-radius: 2px;
  }
  .strength-title::before { background: #10b981; }
  .limiting-title::before { background: #ef4444; }
  .action-title::before { background: #f59e0b; }
  .analytic-item {
    display: flex; align-items: flex-start; gap: 8px;
    margin-bottom: 8px; font-size: 11px; color: #94a3b8;
  }
  .analytic-icon { flex-shrink: 0; margin-top: 1px; }
  .action-num {
    font-size: 18px; font-weight: 900; color: #f59e0b;
    font-family: 'DM Mono', monospace; line-height: 1;
    flex-shrink: 0; width: 24px;
  }
  .action-text strong { color: #e2e8f0; font-size: 11px; display: block; }
  .action-text span { font-size: 10px; color: #475569; }

  /* ── Footer ── */
  .report-footer {
    background: #080c15;
    border-top: 1px solid rgba(255,255,255,0.04);
    padding: 16px 40px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .footer-brand { font-size: 10px; color: #1e293b; letter-spacing: 1px; text-transform: uppercase; }
  .btn-print {
    background: linear-gradient(135deg, #b45309, #f59e0b);
    color: #000; font-weight: 800; font-size: 11px;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 10px 24px; border-radius: 8px; border: none;
    cursor: pointer; transition: opacity 0.2s;
  }
  .btn-print:hover { opacity: 0.85; }

  /* ── Print ── */
  @media print {
    .no-print { display: none !important; }
    body { background: #000 !important; }
    .card, .card-premium, .analytic-card { border-color: #1e293b !important; }
  }
</style>
</head>
<body>

<!-- Accent line -->
<div class="top-rule"></div>

<!-- Header -->
<div class="report-header">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
    <div>
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
        <div class="brand-logo">H</div>
        <div>
          <div style="font-size:13px; font-weight:800; letter-spacing:2px; color:#fff;">HPCS</div>
          <div style="font-size:8px; color:#f59e0b; letter-spacing:2px; font-weight:600;">HIGH PERFORMANCE COMBAT SYSTEM</div>
        </div>
      </div>
      <div class="report-title">ATHLETE <span>PERFORMANCE</span> REPORT</div>
      <div class="report-meta" style="margin-top:6px;">Combat Sports Assessment · Official Document</div>
    </div>
    <div style="text-align:right;">
      <div class="report-meta">Assessment Cycle</div>
      <div class="meta-value">{{ tanggal_cetak|date:"F Y"|upper }}</div>
      <div class="report-meta" style="margin-top:8px;">Report ID</div>
      <div class="report-id">HPCS-BOX-{{ tanggal_cetak|date:"my" }}-{{ atlet.pk|stringformat:"03d" }}</div>
    </div>
  </div>
</div>

<!-- Main Content -->
<div style="padding: 28px 40px; max-width: 1280px; margin: 0 auto;">

  <!-- ROW 1: Score | Bio | DNA -->
  <div style="display:grid; grid-template-columns:220px 1fr 280px; gap:16px; margin-bottom:20px;">

    <!-- Combat Readiness -->
    <div class="card-premium" style="padding:24px; display:flex; flex-direction:column; justify-content:space-between;">
      <div class="section-label">Combat Readiness</div>
      <div style="text-align:center; padding:8px 0;">
        <div class="readiness-score">{{ readiness }}</div>
        <div style="font-size:9px; color:#475569; letter-spacing:1px; margin-top:4px;">/100 POINTS</div>
        <div style="font-size:10px; font-weight:700; color:#10b981; letter-spacing:2px; margin-top:10px; text-transform:uppercase;">
          {% if readiness >= 80 %}&#9989; COMPETITION READY
          {% elif readiness >= 60 %}&#9899; NEAR READY
          {% else %}&#128308; IN DEVELOPMENT{% endif %}
        </div>
      </div>
      <div class="readiness-bar">
        <div class="readiness-fill" style="width:{{ readiness }}%;"></div>
      </div>

      <!-- Score per level -->
      <div class="level-scores" style="margin-top:16px;">
        <div class="level-pill lp-l1">
          <span class="lp-label">L1</span>
          <span class="lp-score">{% if l1 %}{{ l1.total_skor|floatformat:1 }}{% else %}—{% endif %}</span>
          <span class="lp-pred">{% if l1 %}{{ l1.predikat }}{% else %}N/A{% endif %}</span>
        </div>
        <div class="level-pill lp-l2">
          <span class="lp-label">L2</span>
          <span class="lp-score">{% if l2 %}{{ l2.total_skor|floatformat:1 }}{% else %}—{% endif %}</span>
          <span class="lp-pred">{% if l2 %}{{ l2.predikat }}{% else %}N/A{% endif %}</span>
        </div>
        <div class="level-pill lp-l3">
          <span class="lp-label">L3</span>
          <span class="lp-score">{% if l3 %}{{ l3.total_skor|floatformat:1 }}{% else %}—{% endif %}</span>
          <span class="lp-pred">{% if l3 %}{{ l3.predikat }}{% else %}N/A{% endif %}</span>
        </div>
        <div class="level-pill lp-l4">
          <span class="lp-label">L4</span>
          <span class="lp-score">{% if l4 %}{{ l4.total_skor|floatformat:1 }}{% else %}—{% endif %}</span>
          <span class="lp-pred">{% if l4 %}{{ l4.predikat }}{% else %}N/A{% endif %}</span>
        </div>
      </div>
    </div>

    <!-- Biodata -->
    <div class="card" style="padding:24px;">
      <div class="bio-name">{{ atlet.nama_atlet }}</div>
      <div class="bio-sport">&#9889; Boxing Division · HPCS Athlete</div>
      <div class="bio-divider"></div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0 24px;">
        <div class="bio-row">
          <span class="bio-label">Tanggal Lahir</span>
          <span class="bio-value">{{ atlet.tanggal_lahir|date:"d M Y"|default:"—" }}</span>
        </div>
        <div class="bio-row">
          <span class="bio-label">Umur</span>
          <span class="bio-value">{{ atlet.umur|default:"—" }} Tahun</span>
        </div>
        <div class="bio-row">
          <span class="bio-label">Gender</span>
          <span class="bio-value">{{ atlet.gender|default:"—" }}</span>
        </div>
        <div class="bio-row">
          <span class="bio-label">Berat Badan</span>
          <span class="bio-value">{{ atlet.kelas_berat|default:"—" }} KG</span>
        </div>
        <div class="bio-row">
          <span class="bio-label">Tinggi</span>
          <span class="bio-value">{{ atlet.tinggi_badan|default:"—" }} CM</span>
        </div>
        <div class="bio-row">
          <span class="bio-label">Kategori</span>
          <span class="bio-value">{{ atlet.get_kategori_umur_display|default:"—" }}</span>
        </div>
        <div class="bio-row" style="grid-column:span 2;">
          <span class="bio-label">Kelas Tanding</span>
          <span class="bio-value bio-value-accent">{{ kelas|default:"—" }}</span>
        </div>
      </div>
    </div>

    <!-- DNA & Diagnostics -->
    <div class="card" style="padding:24px; display:flex; flex-direction:column; gap:16px;">
      <div>
        <div class="section-label">Quick Diagnostics</div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
          <div>
            <div style="font-size:8px; color:#475569; letter-spacing:1.5px; font-weight:700; margin-bottom:6px;">INJURY RISK</div>
            <div style="font-size:13px; font-weight:800; color:#10b981;">
              <span class="risk-dot risk-low"></span>LOW
            </div>
          </div>
          <div>
            <div style="font-size:8px; color:#475569; letter-spacing:1.5px; font-weight:700; margin-bottom:6px;">PERFORMANCE TIER</div>
            <div style="font-size:11px; font-weight:800; color:#f59e0b; line-height:1.2;">
              {% if overall_predikat == 'ELITE' %}ELITE CLASS
              {% elif overall_predikat == 'READY' %}COMPETITION READY
              {% elif overall_predikat == 'DEVELOPING' %}DEVELOPMENT PHASE
              {% else %}FOUNDATION PHASE{% endif %}
            </div>
          </div>
        </div>
      </div>
      <div style="height:1px; background:rgba(255,255,255,0.05);"></div>
      <div>
        <div style="font-size:8px; color:#475569; letter-spacing:1.5px; font-weight:700; margin-bottom:8px;">COMBAT DNA</div>
        <div class="dna-badge">&#9889; Explosive Counter Fighter</div>
        <p style="font-size:10px; color:#475569; margin-top:10px; line-height:1.6;">
          Strong power profile with high efficiency in counter attacking situations. Excels in reactive movement patterns.
        </p>
      </div>
    </div>
  </div>

  <!-- ROW 2: Charts -->
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:20px;">
    <div class="card" style="padding:24px;">
      <div class="section-label">Performance Architecture</div>
      <div style="height:220px; display:flex; align-items:center; justify-content:center;">
        <canvas id="radarChart"></canvas>
      </div>
    </div>
    <div class="card" style="padding:24px;">
      <div class="section-label">Trend Progress (6 Months)</div>
      <div style="height:220px; position:relative;">
        <canvas id="trendChart"></canvas>
      </div>
    </div>
  </div>

  <!-- ROW 3: Analytics -->
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; margin-bottom:28px;">

    <!-- Key Strengths -->
    <div class="analytic-card" style="border-left:3px solid #10b981;">
      <div class="analytic-title strength-title" style="color:#10b981;">Key Strengths</div>
      <div class="analytic-item">
        <span class="analytic-icon" style="color:#10b981;">&#10003;</span>
        <span>Explosive rotational power</span>
      </div>
      <div class="analytic-item">
        <span class="analytic-icon" style="color:#10b981;">&#10003;</span>
        <span>Excellent strike transfer mechanics</span>
      </div>
      <div class="analytic-item">
        <span class="analytic-icon" style="color:#10b981;">&#10003;</span>
        <span>Strong acceleration profile</span>
      </div>
      <div class="analytic-item">
        <span class="analytic-icon" style="color:#10b981;">&#10003;</span>
        <span>High anaerobic capacity</span>
      </div>
    </div>

    <!-- Limiting Factors -->
    <div class="analytic-card" style="border-left:3px solid #ef4444;">
      <div class="analytic-title limiting-title" style="color:#ef4444;">Limiting Factors</div>
      <div class="analytic-item">
        <span class="analytic-icon" style="color:#f59e0b;">&#9888;</span>
        <span>Thoracic mobility restrictions</span>
      </div>
      <div class="analytic-item">
        <span class="analytic-icon" style="color:#f59e0b;">&#9888;</span>
        <span>Reactive agility reaction time</span>
      </div>
      <div class="analytic-item">
        <span class="analytic-icon" style="color:#f59e0b;">&#9888;</span>
        <span>Defensive timing under fatigue</span>
      </div>
    </div>

    <!-- Coach Priority Actions -->
    <div class="analytic-card" style="border-left:3px solid #f59e0b;">
      <div class="analytic-title action-title" style="color:#f59e0b;">Coach Priority Actions</div>
      <div class="analytic-item" style="align-items:flex-start; gap:10px;">
        <span class="action-num">01</span>
        <div class="action-text">
          <strong>MOBILITY RESTORATION</strong>
          <span>Focus on thoracic extension and ankle mobility drills.</span>
        </div>
      </div>
      <div class="analytic-item" style="align-items:flex-start; gap:10px; margin-top:10px;">
        <span class="action-num">02</span>
        <div class="action-text">
          <strong>REACTIVE MOVEMENT</strong>
          <span>Implement reaction-based agility and defense drills.</span>
        </div>
      </div>
    </div>
  </div>

</div>

<!-- Footer -->
<div class="report-footer no-print">
  <div class="footer-brand">HPCS Combat Sports Performance Engine &middot; {{ tanggal_cetak|date:"Y" }}</div>
  <button onclick="window.print()" class="btn-print">&#128424; Print / Cetak PDF</button>
</div>

''' + chart_script + '''

</body>
</html>'''

with open(path, 'w', encoding='utf-8') as f:
    f.write(NEW_HTML)

print('OK: report_card.html berhasil diredesign')
print('Jalankan: python manage.py runserver')
