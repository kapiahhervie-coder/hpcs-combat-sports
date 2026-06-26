path1 = r'templates\base.html'
path2 = r'combat\templates\combat\l2_strenght.html'

# === FIX BASE.HTML ===
with open(path1, 'r', encoding='utf-8') as f:
    c = f.read()

# Hapus logout-icon yang muncul saat collapsed
c = c.replace('<span class="logout-icon">&#9747;</span>', '')
c = c.replace('<span class="logout-icon" style="font-size:14px;">&#9747;</span>', '')
# Ganti dengan versi bersih
c = c.replace(
    '>&#9747; Logout</a>',
    ' title="Logout">&#9747; Logout</a>'
)
# Sembunyikan seluruh logout saat collapsed via CSS saja
if '.sidebar.collapsed .sidebar-footer a' not in c:
    c = c.replace(
        '.sidebar.collapsed .user-name { display: none !important; }',
        '.sidebar.collapsed .user-name { display: none !important; }\n    .sidebar.collapsed .sidebar-footer a { display: none !important; }'
    )
    print('OK 1: X logout disembunyikan')

with open(path1, 'w', encoding='utf-8') as f:
    f.write(c)

# === FIX L2 TEMPLATE ===
with open(path2, 'r', encoding='utf-8') as f:
    c = f.read()

# Hapus huruf C yang bocor
import re
c = re.sub(r'\n\s+[Cc]\s*\n(\s+<div class="pilar-card")', r'\n\1', c)
c = re.sub(r'(<\/div>\s*)\n\s+[Cc]\s*\n(\s+<div class="pilar-card")', r'\1\n\2', c)
print('OK 2: huruf C dihapus')

# Hapus tombol cetak duplikat - pastikan hanya ada satu
count = c.count('bi-printer-fill')
print(f'Jumlah tombol cetak: {count}')
if count > 1:
    # Hapus semua, tambah satu saja
    c = re.sub(
        r'\s*<button[^>]*onclick="window\.print\(\)"[^>]*>.*?</button>',
        '',
        c,
        flags=re.DOTALL
    )
    # Tambah satu tombol cetak setelah tombol hapus
    c = c.replace(
        '<i class="bi bi-trash3-fill"></i>\n                            </button>',
        '<i class="bi bi-trash3-fill"></i>\n                            </button>\n                            <button class="btn btn-sm btn-outline-info py-0 px-2 ms-1" onclick="window.print()" title="Cetak PDF"><i class="bi bi-printer-fill"></i></button>'
    )
    print('OK 3: tombol cetak deduplikasi')

with open(path2, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
