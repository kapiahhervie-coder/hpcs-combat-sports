path = r'combat\templates\combat\l4_speed_agility.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

import re

# FIX 1: Hapus kolom KONDISI dari header tabel
c = c.replace('<th>Kondisi</th>', '')
c = c.replace('<th>kondisi</th>', '')
c = c.replace('<th>KONDISI</th>', '')

# Cari th kondisi dengan variasi
c = re.sub(r'<th[^>]*>[Kk]ondisi[^<]*</th>', '', c)
print('OK 1: header KONDISI dihapus')

# FIX 2: Hapus kolom kondisi dari body tabel
c = c.replace(
    "<td>{{ item.get_kondisi_uji_display }}</td>",
    ""
)
c = c.replace(
    '<td style="font-size:11px;color:var(--text2);">{{ item.get_kondisi_uji_display }}</td>',
    ''
)
print('OK 2: data kondisi dihapus dari tabel')

# FIX 3: Fix lebar kolom tabel - tambah CSS
TABLE_CSS = '''
    .history-section table { table-layout: fixed; }
    .history-section thead th { white-space: nowrap; font-size: 9px; padding: 8px 6px; }
    .history-section tbody td { padding: 8px 6px; font-size: 11px; }
    .history-section tbody td:nth-child(2) { font-size: 10px; white-space: nowrap; }
'''
c = c.replace('</style>', TABLE_CSS + '\n</style>', 1)
print('OK 3: CSS tabel diperbaiki')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
