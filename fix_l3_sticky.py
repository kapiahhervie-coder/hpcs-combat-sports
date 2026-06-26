path = r'combat\templates\combat\l3_power.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Update grid - buat lebih seimbang
c = c.replace(
    '.l3-grid{display:grid;grid-template-columns:340px 1fr 300px;gap:16px;margin-bottom:24px}',
    '.l3-grid{display:grid;grid-template-columns:340px 1fr 320px;gap:16px;margin-bottom:24px;align-items:start}'
)
print('OK 1: grid diupdate')

# FIX 2: Buat radar-wrap sticky agar ikut scroll
c = c.replace(
    '.radar-wrap{display:flex;flex-direction:column;align-items:center;height:100%}',
    '.radar-wrap{display:flex;flex-direction:column;align-items:center;position:sticky;top:16px}'
)
print('OK 2: radar sticky')

# FIX 3: Perbesar canvas radar
c = c.replace(
    '.radar-canvas-wrap{position:relative;width:100%;height:280px}',
    '.radar-canvas-wrap{position:relative;width:100%;height:340px}'
)
print('OK 3: canvas radar diperbesar')

# FIX 4: Kolom kanan juga sticky
c = c.replace(
    '<div class="l3-col-right">',
    '<div class="l3-col-right" style="position:sticky;top:16px;">'
)
print('OK 4: kolom kanan sticky')

# FIX 5: Kolom kiri bisa scroll independen
c = c.replace(
    '.l3-grid{display:grid;grid-template-columns:340px 1fr 320px;gap:16px;margin-bottom:24px;align-items:start}',
    '.l3-grid{display:grid;grid-template-columns:340px 1fr 320px;gap:16px;margin-bottom:24px;align-items:start}'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
