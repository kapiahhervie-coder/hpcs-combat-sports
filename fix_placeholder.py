import os

files = [
    'muaythai/templates/muaythai/l1_correction.html',
    'muaythai/templates/muaythai/l2_strength.html',
    'muaythai/templates/muaythai/l3_power.html',
    'muaythai/templates/muaythai/l4_speed_agility.html',
]

for fpath in files:
    if not os.path.exists(fpath):
        continue
    with open(fpath, encoding='utf-8', errors='replace') as f:
        text = f.read()

    # Fix semua variasi placeholder rusak
    for bad in ['â€" Pilih Atlet â€"', 'â\x80\x93 Pilih Atlet â\x80\x93',
                '\u00e2\u20ac\u201c Pilih Atlet \u00e2\u20ac\u201c',
                'â€œ Pilih Atlet â€\x9d', '— Pilih Atlet —\u009d']:
        text = text.replace(bad, '— Pilih Atlet —')

    # Fix title tag
    text = text.replace('HPCS â€" Level 1', 'HPCS — Level 1')
    text = text.replace('HPCS â€" Level 2', 'HPCS — Level 2')
    text = text.replace('HPCS â€" Level 3', 'HPCS — Level 3')
    text = text.replace('HPCS â€" Level 4', 'HPCS — Level 4')
    text = text.replace('HPCS â\x80\x93 Level', 'HPCS — Level')

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(text)
    print('OK:', fpath)

print('Done!')
