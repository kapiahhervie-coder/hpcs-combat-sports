path = r'D:\LIBRERY\Phyton\HPCS Combat Sports\combat\templates\combat\dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

fixes = [
    ('<div class=\"stat-label\">Total Atlet</div>', '<div class=\"stat-label\" data-i18n=\"stat_total_atlet\">Total Atlet</div>'),
    ('<div class=\"stat-label\">Audit L1 &bull; Correction</div>', '<div class=\"stat-label\" data-i18n=\"stat_l1\">Audit L1 &bull; Correction</div>'),
    ('<div class=\"stat-label\">Audit L2 &bull; Strength</div>', '<div class=\"stat-label\" data-i18n=\"stat_l2\">Audit L2 &bull; Strength</div>'),
    ('<div class=\"stat-label\">Audit L3 &bull; Power</div>', '<div class=\"stat-label\" data-i18n=\"stat_l3\">Audit L3 &bull; Power</div>'),
    ('<div class=\"level-title\">LEVEL 1</div>', '<div class=\"level-title\" data-i18n=\"level_1\">LEVEL 1</div>'),
    ('<div class=\"level-title\">LEVEL 2</div>', '<div class=\"level-title\" data-i18n=\"level_2\">LEVEL 2</div>'),
    ('<div class=\"level-title\">LEVEL 3</div>', '<div class=\"level-title\" data-i18n=\"level_3\">LEVEL 3</div>'),
    ('<div class=\"level-title\">LEVEL 4</div>', '<div class=\"level-title\" data-i18n=\"level_4\">LEVEL 4</div>'),
]

count = 0
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        count += 1
    else:
        print(f'TIDAK DITEMUKAN: {old[:50]}')

print(f'DONE - {count}/{len(fixes)} berhasil ditambahkan data-i18n')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
