path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Hapus JavaScript yang bocor ke dalam div col-6
import re

# Cari pola: <div class="col-6"> lalu langsung ada JS code
bad_pattern = '''                            <div class="col-6">
                                 });
        mpCamera.start();'''

# Cari dari titik itu sampai penutup </div> yang berpasangan
start_bad = c.find(bad_pattern)
if start_bad >= 0:
    # Cari akhir blok JS yang bocor - ditandai dengan input HTML berikutnya
    # Cari <input setelah posisi itu
    next_input = c.find('<input', start_bad + len(bad_pattern))
    next_div_open = c.rfind('<div', start_bad, next_input)
    
    # Yang benar: div col-6 langsung berisi input-group
    good_replacement = '''                            <div class="col-6">
                                <div class="input-group input-group-sm">
                                    <input'''
    
    # Ambil dari <input sampai akhir tag input
    input_end = c.find('>', next_input) + 1
    input_tag = c[next_input:input_end]
    
    # Ganti seluruh bagian rusak
    bad_section = c[start_bad:next_input]
    c = c.replace(bad_section, '                            <div class="col-6">\n                                <div class="input-group input-group-sm">\n                                    ')
    print('OK: bagian JavaScript bocor dihapus')
else:
    print('SKIP: pola rusak tidak ditemukan persis')
    # Coba cari dengan cara lain
    idx = c.find('mpCamera.start();')
    if idx > 0:
        # Cari div pembuka sebelumnya
        div_start = c.rfind('<div class="col-6">', 0, idx)
        # Cari input setelah JS
        next_inp = c.find('<input', idx)
        if div_start > 0 and next_inp > 0:
            bad = c[div_start:next_inp]
            good = '                            <div class="col-6">\n                                <div class="input-group input-group-sm">\n                                    '
            c = c.replace(bad, good)
            print('OK (alt): JavaScript bocor dihapus')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
