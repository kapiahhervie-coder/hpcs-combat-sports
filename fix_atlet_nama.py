path = r'combat\templates\combat\l4_speed_agility.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Cari dan ganti option atlet - hapus kategori dari tampilan
import re

# Pattern: option dengan data-* dan teks "Nama — KATEGORI"
c = re.sub(
    r'({{ atlet\.nama_atlet }}) — {{ atlet\.[^}]+ }}',
    r'\1',
    c
)

# Juga fix jika formatnya berbeda
c = re.sub(
    r'({{ atlet\.nama_atlet }})\s*&mdash;\s*{{ atlet\.[^}]+ }}',
    r'\1',
    c
)

print('Cek hasil:')
idx = c.find('nama_atlet }}')
print(c[idx-20:idx+80])

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
