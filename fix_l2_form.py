path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Hapus label "Skor (0-10):"
old1 = '                            <label class="small text-white-50">Skor (0' + chr(8211) + '10):</label>'
if old1 in c:
    c = c.replace(old1, '')
    print('OK 1a: label Skor dihapus')
else:
    old1b = '<label class="small text-white-50">Skor (0'
    idx = c.find(old1b)
    if idx > 0:
        end = c.find('</label>', idx) + 8
        c = c[:idx] + c[end:]
        print('OK 1b: label Skor dihapus')
    else:
        print('SKIP 1: label tidak ditemukan')

# FIX 2: Sembunyikan div display Skor yang masih keliatan
for lbl in ['Skor (0', 'Skor:', 'skor (0']:
    while lbl in c:
        idx = c.find(lbl)
        start = c.rfind('<', 0, idx)
        end = c.find('>', idx) + 1
        tag = c[start:end]
        if 'label' in tag or 'div' in tag:
            full_end = c.find('</', end) + c[end:].find('>') + end + 2
            c = c[:start] + c[full_end:]
            print(f'OK: hapus elemen "{lbl}"')
            break
        else:
            break

# FIX 3: Sembunyikan blok Kategori/Gender/BB
# Cari div style display:none yang sudah dibuat
if 'display:none"><div class="row g-2 mb-3">' not in c:
    # Cari blok row g-2 mb-3 yang berisi Kategori
    import re
    pattern = r'(<div class="row g-2 mb-3">.*?<select name="kategori_usia")'
    m = re.search(pattern, c, re.DOTALL)
    if m:
        start = m.start()
        # Cari penutup div row ini
        depth = 0; i = start; end_idx = -1
        while i < len(c):
            if c[i:i+4] == '<div': depth += 1; i += 4
            elif c[i:i+6] == '</div>':
                depth -= 1
                if depth == 0: end_idx = i + 6; break
                i += 6
            else: i += 1
        if end_idx > 0:
            blok = c[start:end_idx]
            c = c.replace(blok, '<div style="display:none">' + blok + '</div>')
            print('OK 3: Kategori/Gender/BB disembunyikan')
        else:
            print('SKIP 3: penutup div tidak ditemukan')
    else:
        print('SKIP 3: blok tidak ditemukan')
else:
    print('OK 3: sudah disembunyikan sebelumnya')

# FIX 4: Tambah hidden inputs untuk kategori/gender/kelas_berat
# agar data dari admin tetap terkirim via onAtletChange
old4 = '                        <input type="hidden" name="atlet_id" id="input_atlet_id">'
new4 = '''                        <input type="hidden" name="atlet_id" id="input_atlet_id">
                        <input type="hidden" name="kategori_usia" id="h_kategori">
                        <input type="hidden" name="gender" id="h_gender">
                        <input type="hidden" name="kelas_berat" id="h_berat">'''
if old4 in c and 'id="h_kategori"' not in c:
    c = c.replace(old4, new4)
    print('OK 4: hidden inputs kategori/gender/berat ditambahkan')
else:
    print('SKIP 4')

# FIX 5: Update onAtletChange untuk isi hidden inputs
old5 = "function onAtletChange(sel) {\n    var opt = sel.options[sel.selectedIndex];\n    document.getElementById('input_atlet_id').value = sel.value;\n    document.getElementById('input_nama').value     = opt.text.split(' " + chr(8212) + " ')[0].trim();\n    var kat  = opt.getAttribute('data-kategori') || 'Elite';\n    var gen  = opt.getAttribute('data-gender')   || 'Putra';\n    var brt  = opt.getAttribute('data-berat')    || '';\n    document.getElementById('usia_atlet').value   = kat;\n    document.getElementById('gender_atlet').value = gen;\n    document.getElementById('input_berat').value  = brt;\n    syncPrint();\n}"

new5 = """function onAtletChange(sel) {
    var opt = sel.options[sel.selectedIndex];
    document.getElementById('input_atlet_id').value = sel.value;
    document.getElementById('input_nama').value = opt.getAttribute('data-nama') || opt.text.trim();
    var kat = opt.getAttribute('data-kategori') || 'Elite';
    var gen = opt.getAttribute('data-gender')   || 'Putra';
    var brt = opt.getAttribute('data-berat')    || '';
    // Isi hidden inputs untuk dikirim ke server
    var hKat = document.getElementById('h_kategori');
    var hGen = document.getElementById('h_gender');
    var hBrt = document.getElementById('h_berat');
    if (hKat) hKat.value = kat;
    if (hGen) hGen.value = gen;
    if (hBrt) hBrt.value = brt;
    // Isi juga yg visible jika ada
    var elKat = document.getElementById('usia_atlet');
    var elGen = document.getElementById('gender_atlet');
    var elBrt = document.getElementById('input_berat');
    if (elKat) elKat.value = kat;
    if (elGen) elGen.value = gen;
    if (elBrt) elBrt.value = brt;
    syncPrint();
}"""

if old5 in c:
    c = c.replace(old5, new5)
    print('OK 5: onAtletChange diupdate')
else:
    # Ganti apapun yang ada
    import re
    c = re.sub(r'function onAtletChange\(sel\)\s*\{[^}]+\}', new5, c)
    print('OK 5: onAtletChange diupdate (regex)')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
