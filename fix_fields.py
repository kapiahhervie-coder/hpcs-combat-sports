path = r'combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

fixes = [
    ('name="rot_l"',    'name="score_rotation"'),
    ('name="rot_r"',    'name="score_rotation_r"'),
    ('name="sta_l"',    'name="score_stability"'),
    ('name="sta_r"',    'name="score_stability_r"'),
    ('name="ankle"',    'name="score_ankle"'),
    ('name="extension"','name="score_extension"'),
    ('name="posture"',  'name="score_posture"'),
    ('name="breathing"','name="score_breathing"'),
]

for old, new in fixes:
    if old in c:
        c = c.replace(old, new)
        print(f'DONE: {old} -> {new}')
    else:
        print(f'SKIP: {old} tidak ditemukan')

# Hapus duplikasi atlet_id - biarkan hanya satu
import re
c = re.sub(r'(<input type="hidden" name="atlet_id"[^>]*>)\s*\n\s*<input type="hidden" name="atlet_id"[^>]*>', r'\1', c)
print('DONE: duplikasi atlet_id dihapus')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('FILE TERSIMPAN')
