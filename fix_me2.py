path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Hapus sisa HTML bocor
bad_strings = [
    'me-2"> X\n\n',
    'me-2">\n',
    ' me-2">',
]
for bad in bad_strings:
    if bad in c:
        c = c.replace(bad, '')
        print(f'OK: hapus "{bad.strip()}"')

# Cari pattern lebih luas
import re
c = re.sub(r'me-2">\s*[^\n<]*\n', '', c)
print('OK: cleanup me-2 selesai')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
