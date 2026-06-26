path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

import re

# FIX 1: Hapus huruf "C" yang bocor
c = re.sub(r'\n\s*[Cc]\s*\n(\s*<div class="pilar-card">)', r'\n\1', c)
print('OK 1: huruf C dihapus')

# FIX 2: Buat teks tabel lebih jelas - hapus opacity/transparansi
c = c.replace(
    'class="fw-bold">{{ item.atlet_name }}',
    'class="fw-bold" style="color:#e5e7eb;">{{ item.atlet_name }}'
)
# Fix kolom yang kabur
for field in ['item.kategori_usia', 'item.gender']:
    c = c.replace(
        '">{{ '+field+' }}',
        '" style="color:#9ca3af;">{{ '+field+' }}'
    )

# FIX 3: BB kabur karena nilai kosong - tampilkan lebih jelas
c = c.replace(
    '{{ item.kelas_berat|default:"—" }} kg',
    '<span style="color:{% if item.kelas_berat %}#9ca3af{% else %}#4b5563{% endif %}">{{ item.kelas_berat|default:"—" }} kg</span>'
)

# FIX 4: Predikat badge lebih jelas
c = c.replace(
    'class="predikat-badge" style="font-size:0.7rem;padding:2px 8px;">{{ item.predikat }}',
    'style="font-size:0.75rem;padding:3px 10px;font-weight:700;border-radius:12px;background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);">{{ item.predikat }}'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
