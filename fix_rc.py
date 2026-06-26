path = r'combat\templates\combat\report_card.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Level pills - kurangi font size agar tidak terpotong
c = c.replace(
    '.lp-score { font-size: 20px; font-weight: 800; font-family: "DM Mono", monospace; line-height: 1; display: block; }',
    '.lp-score { font-size: 17px; font-weight: 800; font-family: "DM Mono", monospace; line-height: 1; display: block; }'
)
c = c.replace(
    '.lp-pred { font-size: 7px; font-weight: 700; letter-spacing: 1px; display: block; margin-top: 3px; }',
    '.lp-pred { font-size: 6px; font-weight: 700; letter-spacing: 0.5px; display: block; margin-top: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }'
)
print('OK 1: level pills diperbaiki')

# FIX 2: Performance Tier - gunakan overall_predikat dari context
# Sudah benar di template, masalahnya views.py mungkin belum kirim overall_predikat
# Cek views.py
with open(r'combat\views.py', 'r', encoding='utf-8') as f:
    v = f.read()
if 'overall_predikat' in v:
    print('OK 2: overall_predikat sudah ada di views')
else:
    print('SKIP 2: overall_predikat tidak ada di views - perlu ditambah')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
