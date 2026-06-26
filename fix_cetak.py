path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = '<i class="bi bi-trash3-fill"></i>\n                            </button>'
new = '<i class="bi bi-trash3-fill"></i>\n                            </button>\n                            <button class="btn btn-sm btn-outline-info py-0 px-2 ms-1" onclick="window.print()" title="Cetak PDF"><i class="bi bi-printer-fill"></i></button>'

if old in c:
    c = c.replace(old, new)
    print('OK: tombol cetak ditambahkan')
else:
    print('SKIP')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
