files = [
    'muaythai/templates/muaythai/l1_correction.html',
    'muaythai/templates/muaythai/l2_strength.html',
    'muaythai/templates/muaythai/l3_power.html',
    'muaythai/templates/muaythai/l4_speed_agility.html',
    'muaythai/templates/muaythai/report_card.html',
    'muaythai/templates/muaythai/dashboard_muaythai.html',
]
bad = [
    ('â€"', '\u2014'),
    ('â€™', '\u2019'),
    ('â€œ', '\u201c'),
    ('Â·', '\u00b7'),
    ('Ã‚Â·', '\u00b7'),
]
for f in files:
    try:
        t = open(f, encoding='utf-8', errors='replace').read()
        for b, g in bad:
            t = t.replace(b, g)
        open(f, 'w', encoding='utf-8').write(t)
        print('OK:', f)
    except Exception as e:
        print('ERR:', f, e)
print('Selesai!')
