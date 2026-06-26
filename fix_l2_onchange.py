path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Tambah fungsi onAtletChange sebelum handlePrint
FUNC = """
function onAtletChange(sel) {
    var opt = sel.options[sel.selectedIndex];
    document.getElementById('input_atlet_id').value = sel.value;
    document.getElementById('input_nama').value     = opt.text.split(' — ')[0].trim();
    var kat  = opt.getAttribute('data-kategori') || 'Elite';
    var gen  = opt.getAttribute('data-gender')   || 'Putra';
    var brt  = opt.getAttribute('data-berat')    || '';
    document.getElementById('usia_atlet').value   = kat;
    document.getElementById('gender_atlet').value = gen;
    document.getElementById('input_berat').value  = brt;
    syncPrint();
}
"""

if 'function onAtletChange' not in c:
    c = c.replace('function handlePrint()', FUNC + '\nfunction handlePrint()')
    print('OK: fungsi onAtletChange ditambahkan')
else:
    print('SKIP: sudah ada')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
