path = r'combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

fixes = [
    ('audit.tanggal_audit',  'audit.timestamp'),
    ('audit.total_score',    'audit.total_skor'),
    ('audit.rotation',       'audit.score_rotation'),
    ('audit.extension',      'audit.score_extension'),
    ('audit.stability',      'audit.score_stability'),
    ('audit.posture',        'audit.score_posture'),
    ('audit.breathing',      'audit.score_breathing'),
    ('audit.atlet.kategori_umur', 'audit.kategori_usia'),
]

for old, new in fixes:
    if old in c:
        c = c.replace(old, new)
        print(f'DONE: {old} -> {new}')
    else:
        print(f'SKIP: {old}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('FILE TERSIMPAN')
