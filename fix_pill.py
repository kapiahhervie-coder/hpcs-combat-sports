path = r'combat\templates\combat\report_card.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Fix grid kolom kiri lebih lebar agar L4 pill muat
c = c.replace(
    'grid-template-columns:220px 1fr 270px',
    'grid-template-columns:240px 1fr 270px'
)

# Fix level-scores jadi 2 baris x 2 kolom agar tidak terpotong
c = c.replace(
    '.level-scores { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 16px; }',
    '.level-scores { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 16px; }'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
