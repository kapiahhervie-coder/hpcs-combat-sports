content = r"""{% extends "base.html" %}
{% load static %}
{% block extra_css %}
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
:root{
  --bg:#07080d;--surface:#0f1018;--card:#13151f;--card2:#181b26;
  --border:rgba(255,255,255,0.07);--border2:rgba(255,255,255,0.13);
  --text:#e4e8f4;--text2:#8892a8;--text3:#454e66;
  --cyan:#f97316;--gold:#facc15;--green:#2ecc71;--red:#e74c3c;--blue:#60a5fa;
}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-size:14px;min-height:100vh;}
.mono{font-family:'JetBrains Mono',monospace}
.bebas{font-family:'Bebas Neue',sans-serif}
.topbar{background:rgba(7,8,13,0.92);backdrop-filter:blur(14px);border-bottom:1px solid var(--border2);padding:0 28px;height:54px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;width:100%;}
.topbar-brand{display:flex;align-items:center;gap:10px}
.brand-mark{width:32px;height:32px;border-radius:7px;background:linear-gradient(135deg,var(--cyan),#ea6c0a);display:flex;align-items:center;justify-content:center;font-family:'Bebas Neue',sans-serif;font-size:16px;color:#000;}
.brand-title{font-family:'Bebas Neue',sans-serif;font-size:15px;letter-spacing:3px;color:var(--text)}
.btn-dash{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;letter-spacing:1.5px;padding:8px 18px;border-radius:8px;background:linear-gradient(135deg,rgba(249,115,22,0.15),rgba(249,115,22,0.05));border:1.5px solid var(--cyan);color:var(--cyan);text-decoration:none;transition:.2s;display:inline-flex;align-items:center;gap:7px;box-shadow:0 0 12px rgba(249,115,22,0.15);}
.btn-dash:hover{background:linear-gradient(135deg,rgba(249,115,22,0.3),rgba(249,115,22,0.1));color:#fff;box-shadow:0 0 20px rgba(249,115,22,0.3);transform:translateY(-1px);}
.main{padding:20px 28px;max-width:1500px;margin:0 auto}
.page-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(28px,4vw,42px);letter-spacing:3px;color:var(--cyan);line-height:1;}
.page-sub{font-size:11px;color:var(--text3);margin-top:3px;font-family:'JetBrains Mono',monospace;letter-spacing:1px}
.filter-bar{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:10px 0}
.ftab{padding:4px 14px;border-radius:20px;font-size:10px;font-weight:600;text-transform:uppercase;text-decoration:none;letter-spacing:1px;border:1px solid var(--border2);color:var(--text3);transition:.2s;cursor:pointer;background:none;}
.ftab-all{border-color:#fff;color:#fff;background:rgba(255,255,255,0.07)}
.ftab-elite{border-color:var(--green);color:var(--green);background:rgba(46,204,113,0.08)}
.ftab-youth{border-color:var(--blue);color:var(--blue);background:rgba(96,165,250,0.08)}
.ftab-junior{border-color:var(--gold);color:var(--gold);background:rgba(250,204,21,0.08)}
.ftab-senior{border-color:var(--red);color:var(--red);background:rgba(231,76,60,0.08)}
.card-x{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;height:100%;}
.card-title{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;letter-spacing:2px;color:var(--text3);text-transform:uppercase;margin-bottom:14px;display:flex;align-items:center;gap:6px;border-left:3px solid var(--cyan);padding-left:10px;}
.form-control,.form-select{background:#1a1c28!important;border:1px solid #2a2d3e;color:var(--text)!important;border-radius:8px;font-size:13px;transition:border-color .2s;}
.form-control:focus,.form-select:focus{background:#1f2133!important;border-color:var(--cyan)!important;box-shadow:0 0 0 2px rgba(249,115,22,0.12)!important;color:var(--text)!important;}
.form-control[readonly]{background:#111320!important;border-color:#1e2030;color:var(--text3)!important;cursor:default}
.form-select option{background:#1a1c28!important;color:var(--text)!important}
label{font-size:11px;color:var(--text2);margin-bottom:4px;display:block;font-family:'JetBrains Mono',monospace;letter-spacing:.5px}
label.cyan{color:var(--cyan)} label.gold{color:var(--gold)}
#radarChart{max-height:300px}
.score-big{font-family:'Bebas Neue',sans-serif;font-size:80px;line-height:1;color:var(--cyan);transition:color .4s;}
.predikat-pill{display:inline-block;padding:6px 22px;border-radius:30px;font-family:'Bebas Neue',sans-serif;font-size:20px;letter-spacing:2px;border:2px solid;transition:all .3s;}
.pred-ELITE{border-color:var(--green);color:var(--green);background:rgba(46,204,113,0.1)}
.pred-READY{border-color:var(--cyan);color:var(--cyan);background:rgba(249,115,22,0.1)}
.pred-DEVELOPING{border-color:var(--gold);color:var(--gold);background:rgba(250,204,21,0.1)}
.pred-NOVICE{border-color:var(--red);color:var(--red);background:rgba(231,76,60,0.1)}
.reko-item{display:flex;gap:8px;align-items:flex-start;padding:7px 10px;border-radius:8px;margin-bottom:5px;background:rgba(249,115,22,0.05);border:1px solid rgba(249,115,22,0.12);font-size:11px;line-height:1.55;}
.rubrik-toggle{display:inline-flex;align-items:center;gap:6px;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--cyan);cursor:pointer;padding:4px 10px;border-radius:6px;border:1px solid rgba(249,115,22,0.2);transition:.2s;margin-top:10px;}
.rubrik-panel{margin-top:12px;border:1px solid var(--border2);border-radius:12px;overflow:hidden;}
.rubrik-header{background:linear-gradient(90deg,#3d1a00,#f97316);color:#000;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;display:grid;grid-template-columns:200px 1fr 1fr 1fr;}
.rubrik-header div,.rubrik-row div{padding:10px 12px}
.rubrik-tabs{display:flex;gap:4px;padding:8px 10px;background:var(--card2);border-bottom:1px solid var(--border)}
.rtab{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1px;padding:3px 10px;border-radius:12px;border:1px solid var(--border2);color:var(--text3);cursor:pointer;transition:.2s;}
.rtab.active,.rtab:hover{color:var(--text);background:rgba(255,255,255,0.06)}
.rubrik-row{display:grid;grid-template-columns:200px 1fr 1fr 1fr;border-top:1px solid var(--border);}
.rubrik-row:hover{background:rgba(255,255,255,0.02)}
.aspek-cell{background:var(--card2);border-right:2px solid var(--cyan)}
.aspek-name{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:var(--cyan);display:block;margin-bottom:2px}
.score-chip{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:9px;padding:2px 7px;border-radius:4px;border-left:3px solid;margin:1px 0;line-height:1.5;width:100%;}
.chip-green{border-left-color:var(--green);background:rgba(46,204,113,0.08);color:#9be8b5}
.chip-blue{border-left-color:var(--blue);background:rgba(96,165,250,0.08);color:#90c8f0}
.chip-yellow{border-left-color:var(--gold);background:rgba(250,204,21,0.08);color:#f5d08a}
.table-dark{--bs-table-bg:transparent;--bs-table-hover-bg:rgba(255,255,255,0.03)}
.table thead th{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--text3);font-weight:400;border-bottom:1px solid var(--border2)!important;padding:10px 12px;}
.table td{padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.04)!important;vertical-align:middle}
.toast-hpcs{position:fixed;top:18px;right:18px;z-index:9999;font-family:'JetBrains Mono',monospace;font-size:11px;padding:10px 18px;border-radius:8px;font-weight:600;box-shadow:0 4px 16px rgba(0,0,0,0.4);transition:opacity .4s;}
.no-print{display:block}
@media print{
  .no-print,.btn,.topbar,.filter-bar{display:none!important}
  body{background:#fff!important;color:#000!important}
}
</style>
{% endblock %}

{% block content %}
<div style="background:var(--bg);min-height:100vh;margin:-24px;padding:0">

<!-- TOPBAR -->
<div class="topbar no-print">
  <div class="topbar-brand">
    <div class="brand-mark">&#127936;</div>
    <div>
      <div class="brand-title">HPCS BASKETBALL</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:8px;color:var(--text3);letter-spacing:1.5px">HIGH PERFORMANCE BASKETBALL</div>
    </div>
  </div>
  <a href="{% url 'basketball:dashboard' %}" class="btn-dash">
    <i class="bi bi-speedometer2"></i> Dashboard
  </a>
</div>

<div class="main">
  <!-- PAGE HEADER -->
  <div class="d-flex align-items-center justify-content-between no-print" style="margin-bottom:16px;flex-wrap:wrap;gap:8px">
    <div>
      <div class="page-title">HPCS LEVEL 1 — CORE & MOBILITY</div>
      <div class="page-sub">Audit Fondasi Gerak &amp; Mobilitas Basketball · Coach {{ request.user.get_full_name|default:request.user.username }}</div>
    </div>
  </div>

  <!-- FILTER BAR -->
  <div class="filter-bar no-print">
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--text3);letter-spacing:1px">FILTER:</span>
    <button class="ftab ftab-all" onclick="filterKat('all',this)">SEMUA</button>
    <button class="ftab ftab-elite" onclick="filterKat('ELITE',this)">ELITE</button>
    <button class="ftab ftab-youth" onclick="filterKat('YOUTH',this)">YOUTH</button>
    <button class="ftab ftab-junior" onclick="filterKat('JUNIOR',this)">JUNIOR</button>
    <button class="ftab ftab-senior" onclick="filterKat('SENIOR',this)">SENIOR</button>
  </div>

  <!-- RUBRIK TOGGLE -->
  <div class="no-print">
    <button class="rubrik-toggle" onclick="toggleRubrik()">
      <i class="bi bi-journal-text"></i>
      <span>RUBRIK STANDAR SKORING</span>
      <i class="bi bi-chevron-down" id="rubrik-chevron"></i>
    </button>
    <div class="rubrik-panel no-print" id="rubrikPanel" style="display:none">
      <style>
      .l1doc{font-size:11px;color:var(--text2);line-height:1.55;padding:14px 16px}
      .l1doc h3{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:900;color:#f97316;text-transform:uppercase;letter-spacing:1.5px;border-left:3px solid #f97316;padding:5px 0 5px 10px;margin:18px 0 8px;background:rgba(249,115,22,0.06)}
      .l1doc h3:first-child{margin-top:0}
      .l1doc table{width:100%;border-collapse:collapse;margin-bottom:10px;font-size:10.5px}
      .l1doc th,.l1doc td{border:1px solid var(--border2);padding:6px 8px;text-align:left;vertical-align:middle}
      .l1doc th{background:#1a0a00;color:#f97316;font-weight:700;font-size:9.5px;text-transform:uppercase;letter-spacing:.5px}
      .l1doc td.kurang{background:rgba(255,107,107,0.06);color:#e89090}
      .l1doc td.cukup{background:rgba(255,179,0,0.06);color:#e8c870}
      .l1doc td.baik{background:rgba(0,255,136,0.06);color:#a0e4bc}
      .l1doc .catatan-box{background:rgba(249,115,22,0.06);border:1px solid rgba(249,115,22,0.25);border-radius:8px;padding:8px 12px;margin:6px 0 14px;font-size:10.5px;color:#fba96a}
      .l1doc .sop-test{background:rgba(255,255,255,0.02);border:1px solid var(--border2);border-radius:10px;padding:12px 14px;margin-bottom:10px}
      .l1doc .sop-test .judul{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--cyan);font-size:11px;margin-bottom:2px}
      .l1doc .sop-test ol{margin:0;padding-left:18px}
      .l1doc .sop-test li{margin-bottom:3px}
      </style>
      <div class="rubrik-tabs">
        <button class="rtab active" onclick="setRubrikKat('all',this)">SEMUA</button>
        <button class="rtab" onclick="setRubrikKat('ankle',this)">ANKLE</button>
        <button class="rtab" onclick="setRubrikKat('hip',this)">HIP</button>
        <button class="rtab" onclick="setRubrikKat('shoulder',this)">SHOULDER</button>
        <button class="rtab" onclick="setRubrikKat('stability',this)">STABILITY</button>
        <button class="rtab" onclick="setRubrikKat('postur',this)">POSTUR</button>
      </div>
      <div class="l1doc">

        <h3>📊 Rubrik Norma Penilaian & Skoring (1–10)</h3>
        <div style="font-size:10px;color:var(--text3);margin-bottom:10px">Standar norma khusus atlet basketball — berbeda dari combat sports karena tuntutan gerak vertikal, lateral, dan overhead yang dominan.</div>

        <!-- ANKLE -->
        <div class="score-chip chip-green kat-ankle kat-all" style="display:block;width:auto;margin-bottom:6px">
          <b style="font-size:10.5px;color:var(--text)">A. Ankle Mobility <span style="color:var(--text3);font-weight:400">(Weight-Bearing Lunge Test – cm)</span></b>
        </div>
        <table class="kat-ankle kat-all">
          <thead><tr><th>Kategori Usia</th><th>Gender</th><th>Kurang (1–4)</th><th>Cukup (5–7)</th><th>Baik/Ideal (8–10)</th></tr></thead>
          <tbody>
            <tr><td>Youth (9–12 thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 7 cm</td><td class="cukup">7 – 10 cm</td><td class="baik">&gt; 10 cm</td></tr>
            <tr><td>Junior (13–17 thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 9 cm</td><td class="cukup">9 – 12 cm</td><td class="baik">&gt; 12 cm</td></tr>
            <tr><td>Senior/Elite (18+ thn)</td><td>Putra</td><td class="kurang">&lt; 10 cm</td><td class="cukup">10 – 13 cm</td><td class="baik">&gt; 13 cm</td></tr>
            <tr><td>Senior/Elite (18+ thn)</td><td>Putri</td><td class="kurang">&lt; 9 cm</td><td class="cukup">9 – 12 cm</td><td class="baik">&gt; 12 cm</td></tr>
          </tbody>
        </table>
        <div class="catatan-box kat-ankle kat-all">⚠️ Ankle mobility KRITIS untuk basketball — gerakan cut, pivot, dan landing membutuhkan dorsifleksi minimal 10–12 cm. Di bawah threshold meningkatkan risiko ankle sprain dan ACL injury secara signifikan.</div>

        <!-- HIP -->
        <div class="score-chip chip-blue kat-hip kat-all" style="display:block;width:auto;margin-bottom:6px">
          <b style="font-size:10.5px;color:var(--text)">B. Hip Mobility <span style="color:var(--text3);font-weight:400">(Hip Flexion ROM – derajat°)</span></b>
        </div>
        <table class="kat-hip kat-all">
          <thead><tr><th>Kategori Usia</th><th>Gender</th><th>Kurang (1–4)</th><th>Cukup (5–7)</th><th>Baik/Ideal (8–10)</th></tr></thead>
          <tbody>
            <tr><td>Youth (9–12 thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 90°</td><td class="cukup">90° – 110°</td><td class="baik">&gt; 110°</td></tr>
            <tr><td>Junior (13–17 thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 100°</td><td class="cukup">100° – 120°</td><td class="baik">&gt; 120°</td></tr>
            <tr><td>Senior/Elite (18+ thn)</td><td>Putra</td><td class="kurang">&lt; 110°</td><td class="cukup">110° – 125°</td><td class="baik">&gt; 125°</td></tr>
            <tr><td>Senior/Elite (18+ thn)</td><td>Putri</td><td class="kurang">&lt; 115°</td><td class="cukup">115° – 130°</td><td class="baik">&gt; 130°</td></tr>
          </tbody>
        </table>
        <div class="catatan-box kat-hip kat-all">⚠️ Hip flexion ROM penting untuk posisi defensive stance, pick-and-roll, dan gerakan squat dalam basketball. Asimetri kiri-kanan &gt; 10° → penalti 1 poin otomatis.</div>

        <!-- SHOULDER -->
        <div class="score-chip chip-yellow kat-shoulder kat-all" style="display:block;width:auto;margin-bottom:6px">
          <b style="font-size:10.5px;color:var(--text)">C. Shoulder Mobility <span style="color:var(--text3);font-weight:400">(Shoulder Flexion ROM – derajat°)</span></b>
        </div>
        <table class="kat-shoulder kat-all">
          <thead><tr><th>Kategori Usia</th><th>Gender</th><th>Kurang (1–4)</th><th>Cukup (5–7)</th><th>Baik/Ideal (8–10)</th></tr></thead>
          <tbody>
            <tr><td>Youth (9–12 thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 150°</td><td class="cukup">150° – 170°</td><td class="baik">&gt; 170°</td></tr>
            <tr><td>Junior (13–17 thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 155°</td><td class="cukup">155° – 175°</td><td class="baik">&gt; 175°</td></tr>
            <tr><td>Senior/Elite (18+ thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 160°</td><td class="cukup">160° – 175°</td><td class="baik">&gt; 175°</td></tr>
          </tbody>
        </table>
        <div class="catatan-box kat-shoulder kat-all">⚠️ Shoulder flexion kritis untuk shooting mechanics dan layup. ROM &lt; 160° → kesulitan mempertahankan release point yang konsisten dan meningkatkan risiko rotator cuff injury.</div>

        <!-- STABILITY -->
        <div class="score-chip chip-green kat-stability kat-all" style="display:block;width:auto;margin-bottom:6px">
          <b style="font-size:10.5px;color:var(--text)">D. Balance & Stability <span style="color:var(--text3);font-weight:400">(Single Leg Stance, mata tertutup – detik)</span></b>
        </div>
        <table class="kat-stability kat-all">
          <thead><tr><th>Kategori Usia</th><th>Gender</th><th>Kurang (1–4)</th><th>Cukup (5–7)</th><th>Baik/Ideal (8–10)</th></tr></thead>
          <tbody>
            <tr><td>Youth (9–12 thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 4 det</td><td class="cukup">4 – 8 det</td><td class="baik">&gt; 8 det</td></tr>
            <tr><td>Junior (13–17 thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 7 det</td><td class="cukup">7 – 13 det</td><td class="baik">&gt; 13 det</td></tr>
            <tr><td>Senior/Elite (18+ thn)</td><td>Putra/Putri</td><td class="kurang">&lt; 10 det</td><td class="cukup">10 – 18 det</td><td class="baik">&gt; 18 det</td></tr>
          </tbody>
        </table>
        <div class="catatan-box kat-stability kat-all">⚠️ Single-leg stability sangat penting untuk landing phase setelah jump shot dan rebound. Asimetri kiri-kanan &gt; 3 detik → penalti 1 poin. Nilai diambil dari kaki terburuk.</div>

        <!-- POSTUR -->
        <div class="score-chip chip-yellow kat-postur kat-all" style="display:block;width:auto;margin-bottom:6px">
          <b style="font-size:10.5px;color:var(--text)">E. Postur & Spine <span style="color:var(--text3);font-weight:400">(Observasi Coach – skor 1–10)</span></b>
        </div>
        <table class="kat-postur kat-all">
          <thead><tr><th>Skor</th><th>Deskripsi</th><th>Indikator</th></tr></thead>
          <tbody>
            <tr><td class="baik">8–10</td><td>Postur Ideal</td><td>Kepala tegak, bahu sejajar, spine netral, tidak ada forward head posture</td></tr>
            <tr><td class="cukup">5–7</td><td>Postur Cukup</td><td>Slight forward head, bahu sedikit rounded, masih dapat dikoreksi dengan cueing</td></tr>
            <tr><td class="kurang">1–4</td><td>Postur Buruk</td><td>Forward head &gt;3 cm, rounded shoulders, hyperkyphosis, perlu program korektif intensif</td></tr>
          </tbody>
        </table>
        <div class="catatan-box kat-postur kat-all">⚠️ Postur buruk pada basketball → menurunkan efisiensi shooting (release point tidak konsisten), meningkatkan risiko cedera punggung dan leher, serta mempengaruhi field of vision saat dribble.</div>

        <h3>🔬 SOP Tes & Protokol</h3>
        <div class="sop-test">
          <div class="judul">1. Weight-Bearing Lunge Test (Ankle Mobility)</div>
          <div style="font-size:9.5px;color:var(--text3);margin-bottom:6px;font-style:italic">Alat: Penggaris/meteran, dinding, lantai datar</div>
          <ol>
            <li>Atlet berdiri menghadap dinding, jari kaki menyentuh dinding</li>
            <li>Dorong lutut ke depan menyentuh dinding tanpa mengangkat tumit</li>
            <li>Jika bisa, mundurkan kaki semakin jauh dari dinding</li>
            <li>Ukur jarak horizontal dari jari kaki ke dinding saat lutut BARU bisa menyentuh</li>
            <li>Lakukan kiri dan kanan, catat keduanya</li>
          </ol>
        </div>
        <div class="sop-test">
          <div class="judul">2. Hip Flexion ROM</div>
          <div style="font-size:9.5px;color:var(--text3);margin-bottom:6px;font-style:italic">Alat: Goniometer atau aplikasi goniometer HP</div>
          <ol>
            <li>Atlet berbaring telentang di matras</li>
            <li>Lutut kontralateral diluruskan (ASLR position)</li>
            <li>Fleksikan satu paha maksimal sambil lutut tetap fleksi 90°</li>
            <li>Ukur sudut yang terbentuk antara paha dan lantai</li>
            <li>Lakukan bilateral (kiri & kanan)</li>
          </ol>
        </div>
        <div class="sop-test">
          <div class="judul">3. Shoulder Flexion ROM</div>
          <div style="font-size:9.5px;color:var(--text3);margin-bottom:6px;font-style:italic">Alat: Goniometer, posisi berdiri tegak</div>
          <ol>
            <li>Atlet berdiri tegak, tangan di sisi tubuh</li>
            <li>Angkat satu lengan ke depan (sagittal plane) semaksimal mungkin</li>
            <li>Ukur sudut antara lengan dan batang tubuh dengan goniometer</li>
            <li>Catat nilai tertinggi (kiri & kanan)</li>
          </ol>
        </div>
        <div class="sop-test">
          <div class="judul">4. Single Leg Balance Test (mata tertutup)</div>
          <div style="font-size:9.5px;color:var(--text3);margin-bottom:6px;font-style:italic">Alat: Stopwatch, permukaan datar</div>
          <ol>
            <li>Atlet berdiri satu kaki, lutut sedikit fleksi (~10°), tangan di pinggul</li>
            <li>Tutup mata, mulai stopwatch</li>
            <li>Hentikan saat kaki angkat menyentuh tanah atau tangan lepas dari pinggul</li>
            <li>3 percobaan per kaki, ambil nilai terbaik</li>
            <li>Catat kiri dan kanan</li>
          </ol>
        </div>
      </div>
    </div>
  </div>

  <!-- MAIN GRID -->
  <div class="row g-3 mt-1">

    <!-- KOLOM KIRI: FORM INPUT -->
    <div class="col-xl-3 col-lg-4">
      <div class="card-x">
        <div class="card-title"><i class="bi bi-person-badge"></i> IDENTITAS ATLET</div>
        <form method="post" id="mainForm">
          {% csrf_token %}
          <div class="mb-3">
            <label>Pilih Atlet</label>
            <select name="atlet_id" class="form-select" id="atlet_select" onchange="loadAtlet(this.value)">
              <option value="">— Pilih Atlet —</option>
              {% for a in atlet_list %}
              <option value="{{ a.id }}" data-pos="{{ a.get_posisi_display|default:'-' }}" data-bb="{{ a.kelas_berat }}" data-tb="{{ a.tinggi_badan|default:'-' }}">{{ a.nama_atlet }}</option>
              {% endfor %}
            </select>
            <div style="font-size:10px;color:var(--text3);margin-top:4px" id="atlet_info">{{ atlet_list.count }} atlet ditemukan.</div>
          </div>
          <div class="row g-2 mb-2">
            <div class="col-6">
              <label>Kategori Usia (SOP)</label>
              <select name="kategori_usia" class="form-select" id="sel_kategori">
                <option value="ELITE">Elite (18+)</option>
                <option value="SENIOR">Senior (18–35)</option>
                <option value="JUNIOR">Junior (13–17)</option>
                <option value="YOUTH">Youth (9–12)</option>
              </select>
            </div>
            <div class="col-6">
              <label>Gender</label>
              <select name="gender" class="form-select" id="sel_gender">
                <option value="Putra">Putra</option>
                <option value="Putri">Putri</option>
              </select>
            </div>
          </div>
          <div class="row g-2 mb-2">
            <div class="col-6">
              <label>Posisi</label>
              <input type="text" class="form-control" id="disp_posisi" value="—" readonly>
            </div>
            <div class="col-6">
              <label>BB (kg)</label>
              <input type="text" class="form-control" id="disp_bb" value="—" readonly>
            </div>
          </div>
          <input type="hidden" name="posisi" id="h_posisi">

          <div style="border-top:1px solid var(--border);margin:14px 0 12px"></div>

          <!-- PILAR 1: ANKLE -->
          <div class="card-title"><i class="bi bi-arrow-down-circle"></i> PILAR ANALYSIS</div>

          <label class="cyan">Ankle Kiri (cm)</label>
          <input type="number" name="ankle_kiri_cm" class="form-control mb-2" step="0.5" placeholder="mis. 10.5" oninput="calcAnkle()">
          <label class="cyan">Ankle Kanan (cm)</label>
          <input type="number" name="ankle_kanan_cm" class="form-control mb-2" step="0.5" placeholder="mis. 11.0" oninput="calcAnkle()">
          <label>Skor Ankle Mobility (Otomatis)</label>
          <div class="input-group mb-3">
            <input type="number" name="score_ankle" id="score_ankle" class="form-control" step="0.1" min="0" max="10" readonly>
            <span class="input-group-text" style="background:#1a1c28;border-color:#2a2d3e;color:var(--text3);font-size:11px">/ 10</span>
          </div>

          <!-- PILAR 2: HIP -->
          <label class="cyan">Hip Fleksi Kiri (°)</label>
          <input type="number" name="hip_fleksi_kiri" class="form-control mb-2" step="1" placeholder="mis. 120" oninput="calcHip()">
          <label class="cyan">Hip Fleksi Kanan (°)</label>
          <input type="number" name="hip_fleksi_kanan" class="form-control mb-2" step="1" placeholder="mis. 118" oninput="calcHip()">
          <label>Skor Hip Mobility (Otomatis)</label>
          <div class="input-group mb-3">
            <input type="number" name="score_hip" id="score_hip" class="form-control" step="0.1" min="0" max="10" readonly>
            <span class="input-group-text" style="background:#1a1c28;border-color:#2a2d3e;color:var(--text3);font-size:11px">/ 10</span>
          </div>

          <!-- PILAR 3: SHOULDER -->
          <label class="cyan">Shoulder Fleksi (°)</label>
          <input type="number" name="shoulder_fleksi" class="form-control mb-2" step="1" placeholder="mis. 172" oninput="calcShoulder()">
          <label>Skor Shoulder Mobility (Otomatis)</label>
          <div class="input-group mb-3">
            <input type="number" name="score_shoulder" id="score_shoulder" class="form-control" step="0.1" min="0" max="10" readonly>
            <span class="input-group-text" style="background:#1a1c28;border-color:#2a2d3e;color:var(--text3);font-size:11px">/ 10</span>
          </div>

          <!-- PILAR 4: STABILITY -->
          <label class="cyan">Balance Kiri (detik)</label>
          <input type="number" name="balance_kiri_detik" class="form-control mb-2" step="0.5" placeholder="mis. 18" oninput="calcStability()">
          <label class="cyan">Balance Kanan (detik)</label>
          <input type="number" name="balance_kanan_detik" class="form-control mb-2" step="0.5" placeholder="mis. 16" oninput="calcStability()">
          <label>Skor Stability (Otomatis)</label>
          <div class="input-group mb-3">
            <input type="number" name="score_stability" id="score_stability" class="form-control" step="0.1" min="0" max="10" readonly>
            <span class="input-group-text" style="background:#1a1c28;border-color:#2a2d3e;color:var(--text3);font-size:11px">/ 10</span>
          </div>

          <!-- PILAR 5: POSTUR -->
          <label class="gold">Postur & Spine (Observasi Coach)</label>
          <select name="score_posture" id="score_posture" class="form-select mb-2" onchange="liveUpdate()">
            <option value="0">— Belum dinilai —</option>
            <option value="9">9 — Postur IDEAL (sempurna)</option>
            <option value="8">8 — Postur BAIK (minor issue)</option>
            <option value="7">7 — Postur CUKUP BAIK</option>
            <option value="6">6 — Ada forward head ringan</option>
            <option value="5">5 — Rounded shoulders moderate</option>
            <option value="4">4 — Perlu koreksi signifikan</option>
            <option value="3">3 — Hyperkyphosis jelas</option>
            <option value="2">2 — Postur buruk, risiko cedera</option>
            <option value="1">1 — Postur sangat buruk</option>
          </select>

          <label>Catatan Coach</label>
          <textarea name="catatan" class="form-control mb-3" rows="2" placeholder="Observasi tambahan..."></textarea>

          <button type="submit" class="btn w-100" style="background:linear-gradient(135deg,var(--cyan),#ea6c0a);color:#000;font-family:'Bebas Neue',sans-serif;font-size:18px;letter-spacing:2px;border:none;padding:10px;border-radius:10px;">
            <i class="bi bi-save2-fill me-2"></i>SAVE AUDIT
          </button>
        </form>
      </div>
    </div>

    <!-- KOLOM TENGAH: RADAR + HASIL -->
    <div class="col-xl-5 col-lg-4">
      <div class="card-x mb-3">
        <div class="card-title"><i class="bi bi-broadcast"></i> BIOMECHANICS RADAR</div>
        <canvas id="radarChart"></canvas>
      </div>
      <div class="card-x">
        <div class="card-title"><i class="bi bi-trophy"></i> AUDIT RESULT</div>
        <div class="text-center py-2">
          <div class="score-big" id="score_total_disp">0.0</div>
          <div id="predikat_disp" class="predikat-pill pred-NOVICE mt-2">NOVICE</div>
          <div style="font-size:11px;color:var(--text3);margin-top:10px;font-family:'JetBrains Mono',monospace" id="layak_disp">Isi data untuk melihat hasil audit</div>
        </div>
        <div style="border-top:1px solid var(--border);margin:14px 0 12px"></div>
        <div class="card-title"><i class="bi bi-lightbulb"></i> REKOMENDASI HPCS</div>
        <div id="reko_box"></div>
      </div>
    </div>

    <!-- KOLOM KANAN: HISTORY -->
    <div class="col-xl-4 col-lg-4">
      <div class="card-x">
        <div class="d-flex align-items-center justify-content-between mb-3 no-print">
          <div class="card-title mb-0"><i class="bi bi-clock-history"></i> DATABASE & HISTORY AUDIT</div>
          <div style="display:flex;gap:6px">
            <span class="ftab ftab-all" onclick="filterHistory('all',this)" style="cursor:pointer">SEMUA</span>
            <span class="ftab ftab-elite" onclick="filterHistory('ELITE',this)" style="cursor:pointer">ELITE</span>
            <span class="ftab ftab-youth" onclick="filterHistory('YOUTH',this)" style="cursor:pointer">YOUTH</span>
            <span class="ftab ftab-junior" onclick="filterHistory('JUNIOR',this)" style="cursor:pointer">JUNIOR</span>
            <span class="ftab ftab-senior" onclick="filterHistory('SENIOR',this)" style="cursor:pointer">SENIOR</span>
          </div>
        </div>
        <div class="table-responsive">
          <table class="table table-dark table-hover">
            <thead>
              <tr>
                <th>#</th><th>Tanggal</th><th>Atlet</th><th>Kat</th>
                <th>Ankle</th><th>Hip</th><th>Shoulder</th><th>Stab</th><th>Postur</th>
                <th>Total</th><th>Pred</th><th class="no-print">Aksi</th>
              </tr>
            </thead>
            <tbody id="history_body">
              {% for h in history %}
              <tr class="history-row" data-kat="{{ h.kategori_usia }}" id="row-{{ h.pk }}">
                <td class="mono" style="color:var(--text3)">{{ forloop.counter }}</td>
                <td class="mono" style="font-size:10px;color:var(--text3);white-space:nowrap">{{ h.timestamp|date:"d/m H:i" }}</td>
                <td style="font-weight:500">{{ h.atlet_name }}</td>
                <td><span style="font-size:9px;padding:2px 6px;border-radius:4px;background:rgba(249,115,22,0.1);color:var(--cyan);font-family:'JetBrains Mono',monospace">{{ h.kategori_usia }}</span></td>
                <td class="mono">{{ h.score_ankle }}</td>
                <td class="mono">{{ h.score_hip }}</td>
                <td class="mono">{{ h.score_shoulder }}</td>
                <td class="mono">{{ h.score_stability }}</td>
                <td class="mono">{{ h.score_posture }}</td>
                <td style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:var(--cyan)">{{ h.total_skor }}</td>
                <td>
                  <span class="predikat-pill pred-{{ h.predikat }}" style="font-size:10px;padding:2px 8px;border-radius:6px;border-width:1px">{{ h.predikat }}</span>
                </td>
                <td class="no-print">
                  <button onclick="cetakAuditBasket({{ h.pk }},'{{ h.atlet_name|escapejs }}','{{ h.kategori_usia }}','{{ h.gender }}',{{ h.score_ankle }},{{ h.score_hip }},{{ h.score_shoulder }},{{ h.score_stability }},{{ h.score_posture }},{{ h.total_skor }},'{{ h.predikat }}','{{ h.timestamp|date:"d/m/Y H:i" }}')"
                    style="background:transparent;border:1px solid rgba(249,115,22,0.3);color:var(--cyan);padding:3px 8px;border-radius:5px;font-size:11px;cursor:pointer;margin-right:4px">
                    <i class="bi bi-printer-fill"></i>
                  </button>
                  <button onclick="kirimWABasket('{{ h.atlet_name|escapejs }}','{{ h.kategori_usia }}',{{ h.total_skor }},'{{ h.predikat }}','{{ h.timestamp|date:"d/m/Y H:i" }}')"
                    style="background:transparent;border:1px solid rgba(37,211,102,0.3);color:#25D366;padding:3px 8px;border-radius:5px;font-size:11px;cursor:pointer;margin-right:4px">
                    <i class="bi bi-whatsapp"></i>
                  </button>
                  <a href="{% url 'basketball:hapus_l1' h.pk %}"
                     onclick="return confirm('Hapus data {{ h.atlet_name|escapejs }}?')"
                     style="background:transparent;border:1px solid rgba(231,76,60,0.3);color:var(--red);padding:3px 8px;border-radius:5px;font-size:11px;text-decoration:none">
                    <i class="bi bi-trash"></i>
                  </a>
                </td>
              </tr>
              {% empty %}
              <tr><td colspan="12" style="text-align:center;color:var(--text3);padding:30px;font-family:'JetBrains Mono',monospace;font-size:11px">
                🏀 Belum ada data audit L1 Basketball
              </td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// ── Radar Chart ──────────────────────────────────────────────────────
const radarCtx = document.getElementById('radarChart').getContext('2d');
const radarChart = new Chart(radarCtx, {
  type: 'radar',
  data: {
    labels: ['Ankle','Hip','Shoulder','Stability','Postur'],
    datasets: [{
      label: 'Skor', data: [0,0,0,0,0],
      borderColor: '#f97316', backgroundColor: 'rgba(249,115,22,0.12)',
      pointBackgroundColor: '#f97316', pointRadius: 5, borderWidth: 2,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      r: {
        min: 0, max: 10, ticks: { display: false, stepSize: 2 },
        grid: { color: 'rgba(255,255,255,0.07)' },
        angleLines: { color: 'rgba(255,255,255,0.07)' },
        pointLabels: { color: '#8892a8', font: { size: 11, family: "'JetBrains Mono'" } }
      }
    }
  }
});

// ── Auto-scoring fungsi ──────────────────────────────────────────────
function getKat(){ return document.getElementById('sel_kategori').value; }
function getGender(){ return document.getElementById('sel_gender').value; }

function scoreAnkle(cm, kat, gender){
  if(!cm) return 0;
  const thresholds = {
    'YOUTH':   {baik:10, cukup_min:7},
    'JUNIOR':  {baik:12, cukup_min:9},
    'ELITE':   gender==='Putri'?{baik:12,cukup_min:9}:{baik:13,cukup_min:10},
    'SENIOR':  gender==='Putri'?{baik:12,cukup_min:9}:{baik:13,cukup_min:10},
  };
  const t = thresholds[kat] || thresholds['ELITE'];
  if(cm >= t.baik) return Math.min(10, 8 + (cm - t.baik) * 0.4);
  if(cm >= t.cukup_min) return 5 + ((cm - t.cukup_min) / (t.baik - t.cukup_min)) * 3;
  return Math.max(1, cm / t.cukup_min * 4);
}

function calcAnkle(){
  const kiri = parseFloat(document.querySelector('[name=ankle_kiri_cm]').value)||0;
  const kanan = parseFloat(document.querySelector('[name=ankle_kanan_cm]').value)||0;
  if(!kiri || !kanan) return;
  const avg = (kiri + kanan) / 2;
  const asimetri = Math.abs(kiri - kanan);
  let skor = scoreAnkle(avg, getKat(), getGender());
  if(asimetri > 2) skor = Math.max(1, skor - 1);
  skor = Math.round(skor * 10) / 10;
  document.getElementById('score_ankle').value = skor;
  liveUpdate();
}

function scoreHip(deg, kat, gender){
  if(!deg) return 0;
  const t = {
    'YOUTH':   {baik:110, cukup_min:90},
    'JUNIOR':  {baik:120, cukup_min:100},
    'ELITE':   gender==='Putri'?{baik:130,cukup_min:115}:{baik:125,cukup_min:110},
    'SENIOR':  gender==='Putri'?{baik:130,cukup_min:115}:{baik:125,cukup_min:110},
  }[kat] || {baik:125, cukup_min:110};
  if(deg >= t.baik) return Math.min(10, 8 + (deg - t.baik) * 0.1);
  if(deg >= t.cukup_min) return 5 + ((deg - t.cukup_min) / (t.baik - t.cukup_min)) * 3;
  return Math.max(1, (deg / t.cukup_min) * 4);
}

function calcHip(){
  const kiri = parseFloat(document.querySelector('[name=hip_fleksi_kiri]').value)||0;
  const kanan = parseFloat(document.querySelector('[name=hip_fleksi_kanan]').value)||0;
  if(!kiri || !kanan) return;
  const min_val = Math.min(kiri, kanan);
  const asimetri = Math.abs(kiri - kanan);
  let skor = scoreHip(min_val, getKat(), getGender());
  if(asimetri > 10) skor = Math.max(1, skor - 1);
  skor = Math.round(skor * 10) / 10;
  document.getElementById('score_hip').value = skor;
  liveUpdate();
}

function scoreShoulder(deg){
  if(!deg) return 0;
  if(deg >= 175) return Math.min(10, 8 + (deg - 175) * 0.5);
  if(deg >= 160) return 5 + ((deg - 160) / 15) * 3;
  if(deg >= 140) return 3 + ((deg - 140) / 20) * 2;
  return Math.max(1, deg / 140 * 3);
}

function calcShoulder(){
  const deg = parseFloat(document.querySelector('[name=shoulder_fleksi]').value)||0;
  if(!deg) return;
  let skor = Math.round(scoreShoulder(deg) * 10) / 10;
  document.getElementById('score_shoulder').value = skor;
  liveUpdate();
}

function scoreStability(detik, kat){
  if(!detik) return 0;
  const t = {
    'YOUTH':  {baik:8, cukup_min:4},
    'JUNIOR': {baik:13, cukup_min:7},
    'ELITE':  {baik:18, cukup_min:10},
    'SENIOR': {baik:18, cukup_min:10},
  }[kat] || {baik:18, cukup_min:10};
  if(detik >= t.baik) return Math.min(10, 8 + (detik - t.baik) * 0.1);
  if(detik >= t.cukup_min) return 5 + ((detik - t.cukup_min) / (t.baik - t.cukup_min)) * 3;
  return Math.max(1, (detik / t.cukup_min) * 4);
}

function calcStability(){
  const kiri = parseFloat(document.querySelector('[name=balance_kiri_detik]').value)||0;
  const kanan = parseFloat(document.querySelector('[name=balance_kanan_detik]').value)||0;
  if(!kiri || !kanan) return;
  const min_val = Math.min(kiri, kanan);
  const asimetri = Math.abs(kiri - kanan);
  let skor = scoreStability(min_val, getKat());
  if(asimetri > 3) skor = Math.max(1, skor - 1);
  skor = Math.round(skor * 10) / 10;
  document.getElementById('score_stability').value = skor;
  liveUpdate();
}

// ── Live Update ──────────────────────────────────────────────────────
const REKO_DB = {
  Ankle: {
    low: ['Weighted-bearing lunge drill 3x10 reps setiap hari','Calf raise eccentric di tangga','Foam roll gastrocnemius + soleus 5 menit/sisi'],
    mid: ['Lunge depth progression drill','Single-leg squat dengan ankle focus','Band-assisted dorsiflexion mobilization'],
    high: ['Pertahankan ankle mobility dengan dynamic warm-up','Variasi plyometric landing: soft & stiff ankle']
  },
  Hip: {
    low: ['90-90 hip stretch 3x60 detik/sisi','Hip flexor lunge stretch 3x45 detik','Supine hip flexion CARs (Controlled Articular Rotations)'],
    mid: ['Deep squat hold progression','Single-leg hip hinge 3x10','Hip flow sequence sebelum latihan'],
    high: ['Pertahankan dengan lateral lunge variasi','Rotational hip warm-up sebelum game']
  },
  Shoulder: {
    low: ['Wall angel 3x10 reps slow','Doorway chest stretch 3x45 detik','Band pull-apart 3x15 reps'],
    mid: ['Overhead mobility progression dengan dowel','Sleeper stretch untuk posterior capsule','Face pull 3x15 reps untuk rotator cuff'],
    high: ['Shooting-specific shoulder warm-up','Rotator cuff strengthening 2x/minggu']
  },
  Stability: {
    low: ['Single-leg stance progression: mata terbuka → tertutup','Wobble board training 3x30 detik','Pertahankan dengan mini band lateral walk'],
    mid: ['Single-leg Romanian deadlift 3x8','Balance board squat progression','Y-Balance Test drill'],
    high: ['Reactive stability: single-leg catch & release','Plyometric landing mechanics: bilateral → unilateral']
  },
  Postur: {
    low: ['Chin tuck exercise 3x10 reps','Thoracic extension over foam roller','Scapular retraction & depression 3x15'],
    mid: ['Wall posture check & correction drill','Band row untuk scapular stabilizer','Core bracing & postur awareness'],
    high: ['Pertahankan dengan mobility routine pagi hari','Video feedback saat shooting untuk postur awareness']
  }
};

function liveUpdate(){
  const scores = {
    Ankle:     parseFloat(document.getElementById('score_ankle').value)||0,
    Hip:       parseFloat(document.getElementById('score_hip').value)||0,
    Shoulder:  parseFloat(document.getElementById('score_shoulder').value)||0,
    Stability: parseFloat(document.getElementById('score_stability').value)||0,
    Postur:    parseFloat(document.getElementById('score_posture').value)||0,
  };
  radarChart.data.datasets[0].data = Object.values(scores);
  radarChart.update('none');

  const vals = Object.values(scores).filter(v => v > 0);
  const total = vals.length ? (vals.reduce((a,b)=>a+b,0)/vals.length) : 0;
  const totalR = Math.round(total * 10) / 10;
  const pred = totalR >= 9 ? 'ELITE' : totalR >= 7 ? 'READY' : totalR >= 5 ? 'DEVELOPING' : 'NOVICE';

  const dispEl = document.getElementById('score_total_disp');
  dispEl.textContent = totalR.toFixed(1);
  dispEl.style.color = pred==='ELITE'?'#2ecc71':pred==='READY'?'#f97316':pred==='DEVELOPING'?'#facc15':'#e74c3c';

  const predEl = document.getElementById('predikat_disp');
  predEl.textContent = pred;
  predEl.className = 'predikat-pill pred-'+pred+' mt-2';

  const layak = totalR >= 7.0;
  const layakEl = document.getElementById('layak_disp');
  layakEl.textContent = layak
    ? '✅ LAYAK naik ke L2 — Kekuatan & Strength'
    : `⚠️ Skor ${totalR} < 7.0 — Belum layak ke L2. Wajib program korektif.`;
  layakEl.style.color = layak ? '#2ecc71' : '#facc15';

  // Rekomendasi
  const rekoBox = document.getElementById('reko_box');
  let html = '';
  Object.entries(scores).forEach(([k,v]) => {
    if(v === 0) return;
    const db = REKO_DB[k]; if(!db) return;
    const tips = v < 5.5 ? db.low : v < 7.5 ? db.mid : db.high;
    const c = v < 5.5 ? '#e74c3c' : v < 7.5 ? '#facc15' : '#2ecc71';
    const label = v < 5.5 ? 'PRIORITAS' : v < 7.5 ? 'PERHATIAN' : 'PERTAHANKAN';
    html += `<div style="margin-bottom:8px"><div style="font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;color:${c};letter-spacing:1px;margin-bottom:4px">${k.toUpperCase()} — ${v.toFixed(1)}/10 | ${label}</div>`;
    tips.forEach(t => {
      html += `<div class="reko-item"><span class="reko-icon">▸</span>${t}</div>`;
    });
    html += '</div>';
  });
  rekoBox.innerHTML = html || '<div style="color:var(--text3);font-size:11px;font-family:JetBrains Mono,monospace">Isi data pilar untuk melihat rekomendasi</div>';
}

// ── Load Atlet ──────────────────────────────────────────────────────
function loadAtlet(id){
  const sel = document.getElementById('atlet_select');
  const opt = sel.options[sel.selectedIndex];
  document.getElementById('disp_posisi').value = opt.dataset.pos || '—';
  document.getElementById('disp_bb').value = opt.dataset.bb ? opt.dataset.bb + ' kg' : '—';
  document.getElementById('h_posisi').value = opt.dataset.pos || '';
}

// ── Filter ──────────────────────────────────────────────────────────
function filterKat(kat, btn){
  document.querySelectorAll('.filter-bar .ftab').forEach(b=>b.style.opacity='.5');
  btn.style.opacity='1';
}
function filterHistory(kat, btn){
  document.querySelectorAll('#history_body .history-row').forEach(r=>{
    r.style.display = (kat==='all' || r.dataset.kat===kat) ? '' : 'none';
  });
}

// ── Rubrik Toggle ────────────────────────────────────────────────────
function toggleRubrik(){
  const p=document.getElementById('rubrikPanel'),c=document.getElementById('rubrik-chevron'),o=p.style.display==='none';
  p.style.display=o?'block':'none';
  c.className=o?'bi bi-chevron-up':'bi bi-chevron-down';
}
function setRubrikKat(kat,btn){
  document.querySelectorAll('.rtab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.l1doc table, .l1doc .catatan-box, .score-chip').forEach(el=>{
    el.style.display=(kat==='all'||el.classList.contains('kat-'+kat)||el.classList.contains('kat-all'))?'':'none';
  });
}

// ── Print & WA ──────────────────────────────────────────────────────
function cetakAuditBasket(id,nama,kat,gender,ankle,hip,shoulder,stability,postur,total,predikat,tgl){
  const warna={ELITE:'#10b981',READY:'#f97316',DEVELOPING:'#facc15',NOVICE:'#ef4444'}[predikat]||'#6b7280';
  const pilar=[
    {n:'Ankle Mobility',v:parseFloat(ankle)||0,icon:'🦶'},
    {n:'Hip Mobility',v:parseFloat(hip)||0,icon:'🔄'},
    {n:'Shoulder Mob.',v:parseFloat(shoulder)||0,icon:'💪'},
    {n:'Stability',v:parseFloat(stability)||0,icon:'⚖️'},
    {n:'Postur',v:parseFloat(postur)||0,icon:'🧍'},
  ];
  const pilarHTML=pilar.map(p=>{
    const pct=Math.min(100,(p.v/10)*100).toFixed(0);
    const c=p.v>=8?'#10b981':p.v>=6?'#f97316':p.v>=4?'#facc15':'#ef4444';
    return `<div style="flex:1;min-width:80px;text-align:center;background:#f8fafc;border:1.5px solid ${c};border-radius:10px;padding:10px 6px">
      <div style="font-size:16px">${p.icon}</div>
      <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:1px">${p.n}</div>
      <div style="font-size:24px;font-weight:900;color:${c}">${p.v.toFixed(1)}</div>
      <div style="height:4px;background:#e5e7eb;border-radius:2px;margin-top:4px;overflow:hidden">
      <div style="height:100%;width:${pct}%;background:${c};border-radius:2px"></div></div></div>`;
  }).join('');
  const terlemah = pilar.filter(p=>p.v>0).sort((a,b)=>a.v-b.v)[0];
  const terkuat = pilar.filter(p=>p.v>0).sort((a,b)=>b.v-a.v)[0];
  const pct=Math.min(100,(parseFloat(total)/10)*100).toFixed(0);
  const html=`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>L1 Basketball - ${nama}</title>
  <style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Segoe UI',sans-serif;background:#fff;color:#111;font-size:13px}@media print{@page{margin:15mm 12mm;size:A4}}</style>
  </head><body>
  <div style="background:linear-gradient(135deg,#0f172a,#1a0a00);color:#fff;padding:20px 28px;display:flex;justify-content:space-between;align-items:center">
    <div><div style="font-size:9px;letter-spacing:3px;color:#94a3b8;text-transform:uppercase">HIGH PERFORMANCE BASKETBALL SYSTEM</div>
    <div style="font-size:22px;font-weight:900;letter-spacing:2px">HPCS <span style="color:#f97316">BASKETBALL</span></div>
    <div style="font-size:11px;color:#cbd5e1">Audit Level 1 — Core & Mobility</div></div>
    <div style="background:${warna};color:#fff;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:800">${predikat}</div>
  </div>
  <div style="padding:14px 28px;background:#f8fafc;border-bottom:1px solid #e2e8f0">
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
    ${[['Nama Atlet',nama],['Kategori',kat],['Gender',gender],['Tanggal',tgl],['Cabang','Basketball 🏀'],['Level','L1 — Core & Mobility']].map(([l,v])=>
      `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px">
      <div style="font-size:9px;color:#94a3b8;text-transform:uppercase">${l}</div>
      <div style="font-size:15px;font-weight:700;color:#0f172a;margin-top:2px">${v}</div></div>`).join('')}
    </div>
  </div>
  <div style="padding:14px 28px;display:flex;align-items:center;gap:20px;background:#fff7ed;border-bottom:2px solid ${warna}">
    <div style="text-align:center;min-width:90px">
      <div style="font-size:9px;color:#555;text-transform:uppercase">Total Skor</div>
      <div style="font-size:52px;font-weight:900;color:${warna}">${parseFloat(total).toFixed(1)}</div>
    </div>
    <div style="flex:1">
      <div style="height:10px;background:#e5e7eb;border-radius:5px;overflow:hidden">
      <div style="height:100%;width:${pct}%;background:${warna};border-radius:5px"></div></div>
      <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
        ${terkuat?`<div style="background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:10px"><span style="color:#888">Terkuat:</span> <strong style="color:#10b981">${terkuat.n} (${terkuat.v.toFixed(1)})</strong></div>`:''}
        ${terlemah&&terlemah!==terkuat?`<div style="background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:10px"><span style="color:#888">Prioritas:</span> <strong style="color:#ef4444">${terlemah.n} (${terlemah.v.toFixed(1)})</strong></div>`:''}
      </div>
    </div>
  </div>
  <div style="padding:14px 28px"><div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#64748b;margin-bottom:10px">Skor Pilar Analysis</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap">${pilarHTML}</div></div>
  <div style="background:#0f172a;color:#94a3b8;padding:10px 28px;display:flex;justify-content:space-between;font-size:10px;margin-top:8px">
    <div>HPCS Basketball — High Performance Basketball System</div><div>${tgl}</div>
  </div>
  <div style="padding:14px 28px;display:flex;justify-content:flex-end">
    <div style="text-align:center;min-width:180px"><div style="border-top:1px solid #374151;padding-top:6px;margin-top:40px;font-size:10px;color:#555">Coach / Pelatih<br><span style="font-size:9px;color:#94a3b8">(__________________________)</span></div></div>
  </div>
  </body></html>`;
  const win=window.open('','_blank','width=960,height=800');
  if(!win){alert('Izinkan pop-up.');return;}
  win.document.write(html);win.document.close();win.focus();
  win.onload=()=>{setTimeout(()=>{win.print();win.onafterprint=()=>win.close();},600);};
}

function kirimWABasket(nama,kat,total,predikat,tgl){
  const meta=document.querySelector('meta[name="coach-hp"]');
  const noHp=meta?meta.content:'';
  let waNum=noHp.replace(/[^0-9]/g,'');
  if(waNum.startsWith('0'))waNum='62'+waNum.slice(1);
  else if(!waNum.startsWith('62')&&waNum.length>0)waNum='62'+waNum;
  const pesan=encodeURIComponent(
    '*LAPORAN AUDIT L1 - HPCS BASKETBALL*\n'+
    '━━━━━━━━━━━━━━━━━━━━\n'+
    '🏀 Atlet: '+nama+'\n'+
    '🏷 Kategori: '+kat+'\n'+
    '📅 Tanggal: '+tgl+'\n'+
    '━━━━━━━━━━━━━━━━━━━━\n'+
    '📊 Total Skor: *'+parseFloat(total).toFixed(1)+'/10*\n'+
    '🏆 Predikat: *'+predikat+'*\n'+
    '━━━━━━━━━━━━━━━━━━━━\n'+
    '_Dikirim otomatis oleh HPCS Basketball System_'
  );
  if(waNum.length>8){window.open('https://wa.me/'+waNum+'?text='+pesan,'_blank');}
  else{var n=prompt('Nomor WhatsApp tujuan:');if(!n)return;var num=n.replace(/[^0-9]/g,'');if(num.startsWith('0'))num='62'+num.slice(1);window.open('https://wa.me/'+num+'?text='+pesan,'_blank');}
}

function showToast(msg,type){
  const el=document.createElement('div');el.className='toast-hpcs';
  el.style.background=type==='success'?'#f97316':'#e74c3c';el.style.color='#fff';
  el.textContent=msg;document.body.appendChild(el);
  setTimeout(()=>{el.style.opacity='0';setTimeout(()=>el.remove(),420);},2800);
}
</script>
{% endblock %}
"""

with open("basketball/templates/basketball/l1_correction.html", "w", encoding="utf-8") as f:
    f.write(content)
print("OK: L1 Basketball berhasil dibuat!")