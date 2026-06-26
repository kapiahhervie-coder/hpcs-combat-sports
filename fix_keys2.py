path = r'D:\LIBRERY\Phyton\HPCS Combat Sports\templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Baris 366 (index 365): logout ID -> tambahkan koma + key baru sebelum '},'
# Baris 381 (index 380): logout EN -> tambahkan koma + key baru sebelum '}'

new_id_keys = '''    logout:         'Keluar',
    stat_total_atlet: 'Total Atlet',
    stat_l1:          'Audit L1 \u2022 Correction',
    stat_l2:          'Audit L2 \u2022 Strength',
    stat_l3:          'Audit L3 \u2022 Power',
    level_1:          'LEVEL 1',
    level_2:          'LEVEL 2',
    level_3:          'LEVEL 3',
    level_4:          'LEVEL 4'
'''

new_en_keys = '''    logout:         'Logout',
    stat_total_atlet: 'Total Athletes',
    stat_l1:          'Audit L1 \u2022 Correction',
    stat_l2:          'Audit L2 \u2022 Strength',
    stat_l3:          'Audit L3 \u2022 Power',
    level_1:          'LEVEL 1',
    level_2:          'LEVEL 2',
    level_3:          'LEVEL 3',
    level_4:          'LEVEL 4'
'''

# Replace baris index 365 (logout Keluar)
if \"logout:         'Keluar'\" in lines[365]:
    lines[365] = new_id_keys
    print('Fixed ID block')
else:
    print('Baris 366 tidak cocok:', repr(lines[365]))

# Cari ulang index logout Logout setelah perubahan (karena lines bertambah)
for i, l in enumerate(lines):
    if \"logout:         'Logout'\" in l:
        lines[i] = new_en_keys
        print(f'Fixed EN block di baris {i+1}')
        break

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('DONE')
