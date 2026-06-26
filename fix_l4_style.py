path = r'combat\templates\combat\l4_speed_agility.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

import re

# FIX 1: Hapus kotak Kondisi Uji yang masih muncul di kolom tengah
c = re.sub(
    r'<div[^>]*>\s*<div[^>]*>[Kk]ondisi [Uu]ji</div>.*?</div>\s*</div>',
    '', c, flags=re.DOTALL
)
# Cari dan hapus div kondisi_display
c = re.sub(
    r'<div[^>]*margin-top:20px[^>]*>.*?kondisi_display.*?</div>\s*</div>',
    '', c, flags=re.DOTALL
)
print('OK 1: kotak kondisi dihapus')

# FIX 2: Warna tema L4 - Pink/Magenta untuk Speed & Agility
# Ganti cyan (#06b6d4) dengan pink-magenta (#e879f9)
COLOR_CSS = '''
    :root {
      --l4-primary: #e879f9;
      --l4-primary-dim: rgba(232,121,249,0.15);
      --l4-primary-border: rgba(232,121,249,0.3);
      --l4-secondary: #c026d3;
    }
    /* Override warna cyan L4 ke magenta */
    .badge-l4, .hdr-actions .btn-outline-cyan {
      border-color: var(--l4-primary) !important;
      color: var(--l4-primary) !important;
    }
    .result-score { color: var(--l4-primary) !important; }
    .rb-elite { border-color: #e879f9 !important; color: #e879f9 !important; background: rgba(232,121,249,0.08) !important; }
    .card-title { color: var(--l4-primary) !important; }
    .pilar-name { color: var(--l4-primary) !important; }
    .btn-save { background: linear-gradient(135deg, #9d174d, #e879f9) !important; color: #fff !important; }
    .score-pill { background: rgba(232,121,249,0.08) !important; border-color: rgba(232,121,249,0.25) !important; color: var(--l4-primary) !important; }
    .skor-bar-fill { background: var(--l4-primary) !important; }
    .history-count { background: rgba(232,121,249,0.08) !important; border-color: rgba(232,121,249,0.2) !important; color: var(--l4-primary) !important; }
    thead th { color: var(--l4-primary) !important; }
    .val { color: var(--l4-primary) !important; }
    .page-title span { color: var(--l4-primary) !important; }
    .badge-l4 { background: rgba(232,121,249,0.1) !important; border-color: rgba(232,121,249,0.3) !important; color: var(--l4-primary) !important; }
    .fc:focus { border-color: var(--l4-primary) !important; box-shadow: 0 0 0 3px rgba(232,121,249,0.1) !important; }
    .narasi_l4 div, #narasi_l4 { border-color: rgba(232,121,249,0.2) !important; }
    #narasi_box_l4 { background: rgba(232,121,249,0.05) !important; border-color: rgba(232,121,249,0.2) !important; }
    .rekomendasi { background: rgba(232,121,249,0.04) !important; border-color: rgba(232,121,249,0.15) !important; }
    .rek-title { color: var(--l4-primary) !important; }
    .btn-print-sm { color: var(--l4-primary) !important; border-color: rgba(232,121,249,0.25) !important; }
    .btn-del-sm { background: rgba(239,68,68,0.08) !important; }
    .pill { background: rgba(232,121,249,0.08) !important; color: var(--l4-primary) !important; }
    .rub-label { color: var(--l4-primary) !important; }
    .rub-head { background: linear-gradient(90deg, #4a0072, #7b2d8b) !important; }
    .history-section { border-color: rgba(232,121,249,0.15) !important; }
    .HPCS-speed { color: var(--l4-primary); }
'''
c = c.replace('</style>', COLOR_CSS + '\n</style>', 1)
print('OK 2: warna magenta/pink diterapkan')

# FIX 3: Buat kolom tengah & kanan sticky
c = c.replace(
    '<div class="col-mid">',
    '<div class="col-mid" style="position:sticky;top:16px;">'
)
c = c.replace(
    '<div class="col-right">',
    '<div class="col-right" style="position:sticky;top:16px;">'
)
print('OK 3: kolom sticky')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
