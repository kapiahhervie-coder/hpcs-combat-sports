# Jalankan: python fix_l2_full.py

path = r'combat\templates\combat\l2_strenght.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

results = []

# ════════════════════════════════════════════════════════════
# FIX 1: Ganti warna tema orange → hijau emerald
# ════════════════════════════════════════════════════════════
color_fixes = [
    # CSS variable utama
    ('--accent: #f59e0b',       '--accent: #10b981'),
    ('--accent: #F59E0B',       '--accent: #10b981'),
    # Warna-warna turunan orange
    ('rgba(245,158,11,',        'rgba(16,185,129,'),
    ('rgba(245, 158, 11,',      'rgba(16,185,129,'),
    ('#f59e0b',                 '#10b981'),
    ('#F59E0B',                 '#10b981'),
    ('#92400e',                 '#065f46'),
    ('#fef3c7',                 '#d1fae5'),
    ('#fbbf24',                 '#34d399'),
    ('#b45309',                 '#047857'),
    ('#78350f',                 '#064e3b'),
    ('text-warning',            'text-success'),
    # Print colors
    ('color: #92400e',          'color: #065f46'),
    ('border-left-color: #92400e', 'border-left-color: #10b981'),
    ('color: var(--accent); font-family', 'color: #10b981; font-family'),
]

n_color = 0
for old, new in color_fixes:
    if old in c:
        c = c.replace(old, new)
        n_color += 1

results.append(f'OK 1: {n_color} warna diganti ke hijau emerald')

# ════════════════════════════════════════════════════════════
# FIX 2: Sembunyikan Kategori, Gender, BB dari form
# (pakai display:none agar data masih terkirim dari hidden)
# ════════════════════════════════════════════════════════════
old2 = '''                        <div class="row g-2 mb-3">
                            <div class="col-4">
                                <label class="small text-white-50 mb-1">Kategori</label>
                                <select name="kategori_usia" id="usia_atlet" class="form-select" onchange="syncPrint()">
                                    <option>Elite</option>
                                    <option>Youth</option>
                                    <option>Junior</option>'''

# Cari dan wrap dengan div hidden
if old2 in c:
    # Cari penutup div row g-2 mb-3 ini (3 col-4 di dalamnya)
    start = c.find(old2)
    # Cari </div> penutup row g-2 mb-3
    search_from = start + len(old2)
    depth = 1
    i = search_from
    while i < len(c) and depth > 0:
        if c[i:i+4] == '<div': depth += 1; i += 4
        elif c[i:i+6] == '</div>': 
            depth -= 1
            if depth == 0: end = i + 6; break
            i += 6
        else: i += 1
    
    old_block = c[start:end]
    new_block = '<div style="display:none">' + old_block + '</div>'
    c = c.replace(old_block, new_block)
    results.append('OK 2: Kategori/Gender/BB disembunyikan dari form')
else:
    results.append('SKIP 2: blok Kategori tidak ditemukan persis')

# ════════════════════════════════════════════════════════════
# FIX 3: Sembunyikan input skor manual (score_lower, score_push, dll)
# ════════════════════════════════════════════════════════════
score_inputs = [
    'id="score_lower"',
    'id="score_push"',
    'id="score_pull"',
    'id="score_core"',
    'id="score_iso"',
]

n_hidden = 0
for sid in score_inputs:
    # Cari baris yang mengandung input ini dan tambahkan style="display:none" ke parent div
    if sid in c:
        # Ganti input visible menjadi hidden type
        # Cari dari awal baris input tersebut
        idx = c.find(sid)
        # Mundur ke < terdekat
        start_input = c.rfind('<input', 0, idx)
        end_input = c.find('>', idx) + 1
        old_input = c[start_input:end_input]
        
        # Ambil name attribute
        name_start = old_input.find('name="') + 6
        name_end = old_input.find('"', name_start)
        field_name = old_input[name_start:name_end] if name_start > 5 else ''
        
        new_input = f'<input type="hidden" name="{field_name}" {sid}>'
        c = c.replace(old_input, new_input, 1)
        n_hidden += 1

results.append(f'OK 3: {n_hidden} input skor dijadikan hidden')

# ════════════════════════════════════════════════════════════
# FIX 4: Tambah fungsi auto-scoring di liveUpdate()
# Ganti/tambah logika kalkulasi skor otomatis dari data mentah
# ════════════════════════════════════════════════════════════
AUTO_SCORE_FUNC = """
// ── Auto Scoring dari Data Mentah ────────────────────────
function calcScoreLower(beban, bb) {
    if (!beban || !bb || bb <= 0) return 0;
    var ratio = beban / bb;
    if (ratio >= 1.5) return 9.5;
    if (ratio >= 1.25) return 8.5;
    if (ratio >= 1.0) return 7.5;
    if (ratio >= 0.75) return 6.0;
    if (ratio >= 0.6) return 5.0;
    return 3.0;
}
function calcScorePush(reps) {
    if (!reps) return 0;
    if (reps > 12) return 9.5;
    if (reps >= 10) return 8.5;
    if (reps >= 6) return 7.0;
    if (reps >= 3) return 5.5;
    return 3.0;
}
function calcScorePull(reps) {
    if (!reps) return 0;
    if (reps > 15) return 9.5;
    if (reps >= 12) return 8.5;
    if (reps >= 8) return 7.0;
    if (reps >= 4) return 5.5;
    return 3.0;
}
function calcScoreCore(detik) {
    if (!detik) return 0;
    if (detik > 90) return 9.5;
    if (detik >= 75) return 8.5;
    if (detik >= 60) return 7.0;
    if (detik >= 30) return 5.5;
    return 3.0;
}
function calcScoreIso(detik) {
    if (!detik) return 0;
    if (detik > 60) return 9.5;
    if (detik >= 50) return 8.5;
    if (detik >= 40) return 7.0;
    if (detik >= 20) return 5.5;
    return 3.0;
}

function autoCalcScores() {
    var bb     = parseFloat(document.getElementById('input_berat').value) || 0;
    var bebanL = parseFloat(document.getElementById('lower_5rm_beban').value) || 0;
    var repsPush = parseFloat(document.getElementById('push_5rm_beban').value) || 0;
    var repsPull = parseFloat(document.getElementById('pull_reps').value) || 0;
    var coreDetik = parseFloat(document.getElementById('core_durasi').value) || 0;
    var isoDetik  = parseFloat(document.getElementById('iso_durasi').value) || 0;

    var sL = calcScoreLower(bebanL, bb);
    var sP = calcScorePush(repsPush);
    var sPl = calcScorePull(repsPull);
    var sC = calcScoreCore(coreDetik);
    var sI = calcScoreIso(isoDetik);

    document.getElementById('score_lower').value    = sL.toFixed(1);
    document.getElementById('score_push').value     = sP.toFixed(1);
    document.getElementById('score_pull').value     = sPl.toFixed(1);
    document.getElementById('score_core').value     = sC.toFixed(1);
    document.getElementById('score_iso').value      = sI.toFixed(1);

    // Update display badge
    var badges = [
        {id:'badge_lower', val:sL},
        {id:'badge_push',  val:sP},
        {id:'badge_pull',  val:sPl},
        {id:'badge_core',  val:sC},
        {id:'badge_iso',   val:sI},
    ];
    badges.forEach(function(b) {
        var el = document.getElementById(b.id);
        if (el) {
            el.textContent = b.val.toFixed(1);
            el.style.color = b.val >= 9 ? '#10b981' : b.val >= 7 ? '#38bdf8' : b.val >= 5 ? '#f59e0b' : '#f87171';
        }
    });

    return [sL, sP, sPl, sC, sI];
}
"""

if 'function calcScoreLower' not in c:
    c = c.replace('function liveUpdate()', AUTO_SCORE_FUNC + '\nfunction liveUpdate()')
    results.append('OK 4: fungsi auto-scoring ditambahkan')
else:
    results.append('OK 4: auto-scoring sudah ada')

# ════════════════════════════════════════════════════════════
# FIX 5: Tambah panggilan autoCalcScores() di awal liveUpdate
# ════════════════════════════════════════════════════════════
old5 = 'function liveUpdate() {'
new5 = 'function liveUpdate() {\n    autoCalcScores();'

if old5 in c and 'autoCalcScores();' not in c:
    c = c.replace(old5, new5, 1)
    results.append('OK 5: autoCalcScores dipanggil di liveUpdate')
else:
    results.append('SKIP 5: sudah ada atau tidak ditemukan')

# ════════════════════════════════════════════════════════════
# FIX 6: Tambah badge skor otomatis di sebelah setiap input
# (tambahkan di bawah input beban lower)
# ════════════════════════════════════════════════════════════
BADGE_STYLE = '''<style>
.auto-score-badge {
    display:inline-block;
    font-family:'Barlow Condensed',sans-serif;
    font-size:1.1rem;
    font-weight:700;
    color:#10b981;
    background:rgba(16,185,129,0.1);
    border:1px solid rgba(16,185,129,0.3);
    border-radius:6px;
    padding:2px 10px;
    margin-top:4px;
}
.auto-score-label {
    font-size:0.65rem;
    color:#6b7280;
    text-transform:uppercase;
    letter-spacing:1px;
    margin-bottom:2px;
}
</style>'''

if '.auto-score-badge' not in c:
    c = c.replace('</style>', BADGE_STYLE + '\n</style>', 1)
    results.append('OK 6: style badge skor otomatis ditambahkan')

# ════════════════════════════════════════════════════════════
# FIX 7: Tambahkan oninput="liveUpdate()" ke semua input data mentah
# ════════════════════════════════════════════════════════════
raw_inputs = [
    'id="lower_5rm_beban"',
    'id="push_5rm_beban"',
    'id="pull_reps"',
    'id="core_durasi"',
    'id="iso_durasi"',
    'id="iso_tremor"',
    'id="input_berat"',
]

n_oninput = 0
for rid in raw_inputs:
    if rid in c and f'oninput' not in c[c.find(rid)-200:c.find(rid)+100]:
        idx = c.find(rid)
        end = c.find('>', idx)
        old_tag = c[idx:end]
        new_tag = old_tag + ' oninput="liveUpdate()"'
        c = c.replace(old_tag, new_tag, 1)
        n_oninput += 1

results.append(f'OK 7: {n_oninput} input diberi oninput=liveUpdate()')

# Simpan
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print()
print('='*55)
print('  HASIL FIX L2')
print('='*55)
for r in results:
    print(' ', r)
print('='*55)
print('  FILE TERSIMPAN')
print()
print('  Jalankan: python manage.py runserver')
print('='*55)
