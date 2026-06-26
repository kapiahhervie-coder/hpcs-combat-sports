path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Hapus seluruh blok messages dari template L2
# karena base.html sudah handle ini
import re
pattern = r'\s*{%\s*if messages\s*%\}.*?{%\s*endif\s*%\}'
match = re.search(pattern, c, re.DOTALL)
if match:
    print('Ditemukan:', match.group()[:80])
    c = c[:match.start()] + c[match.end():]
    print('OK: messages block dihapus dari L2')
else:
    print('SKIP: tidak ditemukan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
