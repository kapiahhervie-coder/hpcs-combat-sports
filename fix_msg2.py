path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Cari dan hapus blok messages yang kedua
first = c.find('{% if messages %}')
second = c.find('{% if messages %}', first + 1)
print('First messages di index:', first)
print('Second messages di index:', second)

if second > 0:
    # Cari awal div container sebelum second
    div_start = c.rfind('<div', 0, second)
    # Cari endif penutup
    endif_pos = c.find('{% endif %}', second) + 11
    # Cari </div> setelah endif
    end_div = c.find('</div>', endif_pos) + 6
    removed = c[div_start:end_div]
    print('Yang dihapus:', removed[:100])
    c = c[:div_start] + c[end_div:]
    print('OK: duplikasi messages dihapus')
else:
    print('Hanya ada satu messages block')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
