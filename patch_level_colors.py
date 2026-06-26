import re

CSS_OLD = """.level-grid-card:hover {
            border-color: var(--neon-blue);
            box-shadow: 0 8px 20px rgba(56,189,248,0.2);
            transform: translateY(-4px);
        }
        .level-top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .level-tag {
            font-size: 0.75rem; background: rgba(56,189,248,0.1);
            color: var(--neon-blue); padding: 3px 10px;
            border-radius: 12px; font-weight: 600;
        }

        /* Angka 01-04 dengan warna aksen transparan per level */
        .level-huge-num {
            font-size: 2.2rem; font-weight: 900;
            line-height: 1; opacity: 1;
            color: rgba(56,189,248,0.12);
        }
        .level-grid-card:nth-child(1) .level-huge-num { color: rgba(56,189,248,0.15); }
        .level-grid-card:nth-child(2) .level-huge-num { color: rgba(0,255,136,0.15); }
        .level-grid-card:nth-child(3) .level-huge-num { color: rgba(255,179,0,0.15); }
        .level-grid-card:nth-child(4) .level-huge-num { color: rgba(255,107,157,0.15); }

        /* Deskripsi level — line-height konsisten */
        .level-grid-card p.text-secondary {
            line-height: 1.55;
            font-size: 0.82rem;
            min-height: 38px;
        }

        /* Tombol audit — konsisten semua level pakai border neon-blue */
        .btn-action-audit {
            background: transparent;
            border: 1px solid rgba(56,189,248,0.35);
            color: rgba(56,189,248,0.85);
            font-weight: 600; border-radius: 6px;
            transition: all 0.2s; font-size: 0.85rem;
        }
        .btn-action-audit:hover,
        .level-grid-card:hover .btn-action-audit {
            background: var(--neon-blue);
            border-color: var(--neon-blue);
            color: var(--bg-dark);
            box-shadow: 0 4px 12px rgba(56,189,248,0.3);
        }"""

CSS_NEW = """.level-grid-card:hover {
            transform: translateY(-4px);
        }
        .level-top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .level-tag {
            font-size: 0.75rem; padding: 3px 10px;
            border-radius: 12px; font-weight: 600;
        }

        /* Warna per level sesuai karakter */
        /* L1 - Fondasi Gerak - Cyan/Biru Medis */
        .level-card-l1 {
            border-color: rgba(56,189,248,0.3);
            background: linear-gradient(135deg, rgba(56,189,248,0.06) 0%, rgba(56,189,248,0.01) 100%);
        }
        .level-card-l1:hover { border-color: #38bdf8; box-shadow: 0 8px 24px rgba(56,189,248,0.2); }
        .level-card-l1 .level-tag { background: rgba(56,189,248,0.12); color: #38bdf8; }
        .level-card-l1 .level-huge-num { color: rgba(56,189,248,0.18); }
        .level-card-l1 .btn-action-audit { border-color: rgba(56,189,248,0.4); color: #38bdf8; }
        .level-card-l1:hover .btn-action-audit { background: #38bdf8; color: #060b13; box-shadow: 0 4px 14px rgba(56,189,248,0.35); }

        /* L2 - Kekuatan Otot - Hijau Power */
        .level-card-l2 {
            border-color: rgba(74,222,128,0.3);
            background: linear-gradient(135deg, rgba(74,222,128,0.06) 0%, rgba(74,222,128,0.01) 100%);
        }
        .level-card-l2:hover { border-color: #4ade80; box-shadow: 0 8px 24px rgba(74,222,128,0.2); }
        .level-card-l2 .level-tag { background: rgba(74,222,128,0.12); color: #4ade80; }
        .level-card-l2 .level-huge-num { color: rgba(74,222,128,0.18); }
        .level-card-l2 h5 { color: #4ade80; }
        .level-card-l2 .btn-action-audit { border-color: rgba(74,222,128,0.4); color: #4ade80; }
        .level-card-l2:hover .btn-action-audit { background: #4ade80; color: #060b13; box-shadow: 0 4px 14px rgba(74,222,128,0.35); }

        /* L3 - Daya Ledak - Oranye Eksplosif */
        .level-card-l3 {
            border-color: rgba(251,146,60,0.3);
            background: linear-gradient(135deg, rgba(251,146,60,0.06) 0%, rgba(251,146,60,0.01) 100%);
        }
        .level-card-l3:hover { border-color: #fb923c; box-shadow: 0 8px 24px rgba(251,146,60,0.2); }
        .level-card-l3 .level-tag { background: rgba(251,146,60,0.12); color: #fb923c; }
        .level-card-l3 .level-huge-num { color: rgba(251,146,60,0.18); }
        .level-card-l3 h5 { color: #fb923c; }
        .level-card-l3 .btn-action-audit { border-color: rgba(251,146,60,0.4); color: #fb923c; }
        .level-card-l3:hover .btn-action-audit { background: #fb923c; color: #060b13; box-shadow: 0 4px 14px rgba(251,146,60,0.35); }

        /* L4 - Spesifik Ring - Pink Agresif */
        .level-card-l4 {
            border-color: rgba(244,114,182,0.3);
            background: linear-gradient(135deg, rgba(244,114,182,0.06) 0%, rgba(244,114,182,0.01) 100%);
        }
        .level-card-l4:hover { border-color: #f472b6; box-shadow: 0 8px 24px rgba(244,114,182,0.2); }
        .level-card-l4 .level-tag { background: rgba(244,114,182,0.12); color: #f472b6; }
        .level-card-l4 .level-huge-num { color: rgba(244,114,182,0.18); }
        .level-card-l4 h5 { color: #f472b6; }
        .level-card-l4 .btn-action-audit { border-color: rgba(244,114,182,0.4); color: #f472b6; }
        .level-card-l4:hover .btn-action-audit { background: #f472b6; color: #060b13; box-shadow: 0 4px 14px rgba(244,114,182,0.35); }

        /* Angka besar */
        .level-huge-num {
            font-size: 2.2rem; font-weight: 900; line-height: 1;
        }

        /* Deskripsi level */
        .level-grid-card p.text-secondary {
            line-height: 1.55; font-size: 0.82rem; min-height: 38px;
        }

        /* Tombol audit base */
        .btn-action-audit {
            background: transparent;
            font-weight: 600; border-radius: 6px;
            transition: all 0.2s; font-size: 0.85rem;
            border-width: 1px; border-style: solid;
        }"""

# HTML cards - ganti class level-grid-card jadi spesifik per level
HTML_CARDS_OLD = [
    # L1
    ('        <!-- LEVEL 1 -->\n        <div class="col-12 col-md-6 col-lg-3">\n            <div class="level-grid-card">',
     '        <!-- LEVEL 1 -->\n        <div class="col-12 col-md-6 col-lg-3">\n            <div class="level-grid-card level-card-l1">'),
    # L2
    ('        <!-- LEVEL 2 -->\n        <div class="col-12 col-md-6 col-lg-3">\n            <div class="level-grid-card">',
     '        <!-- LEVEL 2 -->\n        <div class="col-12 col-md-6 col-lg-3">\n            <div class="level-grid-card level-card-l2">'),
    # L3
    ('        <!-- LEVEL 3 -->\n        <div class="col-12 col-md-6 col-lg-3">\n            <div class="level-grid-card">',
     '        <!-- LEVEL 3 -->\n        <div class="col-12 col-md-6 col-lg-3">\n            <div class="level-grid-card level-card-l3">'),
    # L4 - punya style inline
    ('            <div class="level-grid-card" style="border-color:rgba(74,222,128,0.3)">',
     '            <div class="level-grid-card level-card-l4">'),
]

# Hapus inline style pada L4 yang sudah tidak diperlukan
L4_OVERRIDES_OLD = [
    '<span class="level-tag" style="background:rgba(74,222,128,0.1);color:var(--neon-green)">Spesifik Ring</span>',
    '<div class="level-huge-num" style="color:rgba(74,222,128,0.1)">04</div>',
    '<h5 class="fw-bold mb-1" style="color:var(--neon-green)">LEVEL 4</h5>',
    'style="border-color:var(--neon-green);color:#fff"',
]
L4_OVERRIDES_NEW = [
    '<span class="level-tag">Spesifik Ring</span>',
    '<div class="level-huge-num">04</div>',
    '<h5 class="fw-bold mb-1">LEVEL 4</h5>',
    '',
]

files = [
    'D:/LIBRERY/Phyton/HPCS Combat Sports/combat/templates/combat/dashboard_boxing.html',
    'D:/LIBRERY/Phyton/HPCS Combat Sports/combat/templates/combat/dashboard_muaythai.html',
]

import os
for fpath in files:
    if not os.path.exists(fpath):
        print(f"SKIP (tidak ditemukan): {fpath}")
        continue

    content = open(fpath, 'r', encoding='utf-8').read()

    # 1. Ganti CSS
    if CSS_OLD in content:
        content = content.replace(CSS_OLD, CSS_NEW)
        print(f"CSS diganti: {os.path.basename(fpath)}")
    else:
        print(f"WARN: CSS lama tidak ditemukan di {os.path.basename(fpath)}")

    # 2. Ganti class HTML cards
    for old, new in HTML_CARDS_OLD:
        content = content.replace(old, new)

    # 3. Bersihkan inline style L4
    for old, new in zip(L4_OVERRIDES_OLD, L4_OVERRIDES_NEW):
        content = content.replace(old, new)

    open(fpath, 'w', encoding='utf-8').write(content)
    print(f"Selesai: {os.path.basename(fpath)}")

print("\nDone.")
