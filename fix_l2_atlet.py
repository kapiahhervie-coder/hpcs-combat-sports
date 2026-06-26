path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Tambah hidden atlet_id setelah input atlet_name
old1 = '                                        <input type="hidden" name="atlet_name" id="input_nama"'
new1 = '                                        <input type="hidden" name="atlet_id" id="input_atlet_id">\n                                        <input type="hidden" name="atlet_name" id="input_nama"'

if old1 in c:
    c = c.replace(old1, new1)
    print('OK 1: atlet_id hidden input ditambahkan')
else:
    print('SKIP 1')

# FIX 2: Tambah atlet_id ke fungsi onAtletChange di JavaScript
old2 = "function onAtletChange(sel){"
new2 = "function onAtletChange(sel){document.getElementById('input_atlet_id').value=sel.value;"

if old2 in c:
    c = c.replace(old2, new2)
    print('OK 2: onAtletChange diupdate')
else:
    # Cari alternatif
    old2b = "onAtletChange"
    if old2b in c:
        print('SKIP 2: cek manual fungsi onAtletChange')
    else:
        print('SKIP 2: onAtletChange tidak ditemukan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE - FIX 1&2')
