path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Hapus duplikasi messages - cek berapa kali muncul
import re
count = c.count('{% for msg in messages %}')
print('Jumlah messages block:', count)

# Hapus yang kedua
if count > 1:
    first = c.find('{% for msg in messages %}')
    second = c.find('{% for msg in messages %}', first + 1)
    # Cari awal div sebelum second
    div_start = c.rfind('<div', 0, second)
    # Cari endfor penutupnya
    endfor = c.find('{% endfor %}', second) + 12
    # Cari penutup div
    end_div = c.find('</div>', endfor) + 6
    c = c[:div_start] + c[end_div:]
    print('OK 1: duplikasi messages dihapus')

# FIX 2: Fix tombol hapus terpotong - tambah min-width ke kolom aksi
old2 = '<td class="text-center">\n                            <button class="btn btn-sm btn-outline-danger py-0 px-2"'
new2 = '<td class="text-center" style="min-width:80px;">\n                            <button class="btn btn-sm btn-outline-danger py-0 px-2"'

if old2 in c:
    c = c.replace(old2, new2)
    print('OK 2: kolom aksi diperlebar')
else:
    print('SKIP 2: cari alternatif')
    old2b = "onclick=\"if(confirm('Hapus data"
    if old2b in c:
        idx = c.rfind('<td', 0, c.find(old2b))
        old_td = c[idx:c.find('>', idx)+1]
        new_td = old_td.replace('>', ' style="min-width:80px;">', 1)
        c = c.replace(old_td, new_td, 1)
        print('OK 2b: kolom aksi diperlebar')

# FIX 3: Tambah tombol hapus yang lebih jelas
old3 = "onclick=\"if(confirm('Hapus data {{ item.atlet_name }}?')) window.location='/combat/l2-strength/hapus/{{ item.pk }}/'\">"
new3 = "onclick=\"if(confirm('Hapus data {{ item.atlet_name }}?')) window.location='/combat/l2-strength/hapus/{{ item.pk }}/'\" style=\"white-space:nowrap;\">"

if old3 in c:
    c = c.replace(old3, new3)
    print('OK 3: tombol hapus diperbaiki')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
