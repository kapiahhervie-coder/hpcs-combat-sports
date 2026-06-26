path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Cek berapa kali onAtletChange muncul
count = c.count('function onAtletChange')
print('Jumlah onAtletChange:', count)

# Cek juga input_atlet_id ada tidak
print('input_atlet_id ada:', 'input_atlet_id' in c)
print('h_kategori ada:', 'h_kategori' in c)

# Cek select_atlet onchange
import re
m = re.search(r'select id="select_atlet"[^>]*onchange="([^"]*)"', c)
print('onchange select_atlet:', m.group(1) if m else 'TIDAK ADA')
