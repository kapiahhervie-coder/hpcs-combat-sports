path = r'templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Hapus menu Report Center dari sidebar
import re
c = re.sub(
    r'\s*<a href="[^"]*report_center[^"]*"[^>]*>.*?</a>',
    '',
    c, flags=re.DOTALL
)
print('OK 1: menu Report Center dihapus dari sidebar')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
