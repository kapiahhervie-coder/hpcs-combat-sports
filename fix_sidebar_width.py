path = r'templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Fix nav-link-text agar tidak terpotong
c = c.replace(
    '.nav-link-text logout-link',
    'nav-link-text logout-link'
)

# Fix ukuran font nav-link saat expanded
if '.nav-link{display:flex' in c:
    c = c.replace(
        'font-size:12.5px;font-weight:500;transition:all .15s;border-left:3px solid transparent;}',
        'font-size:11.5px;font-weight:500;transition:all .15s;border-left:3px solid transparent;white-space:nowrap;overflow:hidden;}'
    )
    print('OK 1: font nav-link dikecilkan')

# Fix sidebar width sedikit lebih lebar
c = c.replace(
    '.sidebar{position:fixed;top:0;left:0;width:230px;',
    '.sidebar{position:fixed;top:0;left:0;width:240px;'
)
c = c.replace(
    '.main-wrapper { margin-left: 230px;',
    '.main-wrapper { margin-left: 240px;'
)
print('OK 2: sidebar diperlebar ke 240px')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
