path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

fixes = [
    ('#10b981', '#00e5b0'),
    ('rgba(16,185,129,', 'rgba(0,229,176,'),
    ('rgba(16, 185, 129,', 'rgba(0,229,176,'),
    ('#065f46', '#00a882'),
    ('#047857', '#00c49a'),
    ('#34d399', '#00e5b0'),
    ('#6ee7b7', '#7dffd8'),
]

n = 0
for old, new in fixes:
    if old in c:
        c = c.replace(old, new)
        n += 1
        print(f'OK: {old} -> {new}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print(f'DONE - {n} warna diganti ke Mint Fresh')
