path = r"D:\LIBRERY\Phyton\HPCS Combat Sports\templates\base.html"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_id_keys = """    logout:         'Keluar',
    stat_total_atlet: 'Total Atlet',
    stat_l1:          'Audit L1 \u2022 Correction',
    stat_l2:          'Audit L2 \u2022 Strength',
    stat_l3:          'Audit L3 \u2022 Power',
    level_1:          'LEVEL 1',
    level_2:          'LEVEL 2',
    level_3:          'LEVEL 3',
    level_4:          'LEVEL 4'
"""

new_en_keys = """    logout:         'Logout',
    stat_total_atlet: 'Total Athletes',
    stat_l1:          'Audit L1 \u2022 Correction',
    stat_l2:          'Audit L2 \u2022 Strength',
    stat_l3:          'Audit L3 \u2022 Power',
    level_1:          'LEVEL 1',
    level_2:          'LEVEL 2',
    level_3:          'LEVEL 3',
    level_4:          'LEVEL 4'
"""

target_keluar = "logout:         'Keluar'"
target_logout = "logout:         'Logout'"

fixed_id = False
fixed_en = False

for i in range(len(lines)):
    if target_keluar in lines[i] and not fixed_id:
        lines[i] = new_id_keys
        fixed_id = True
        print("Fixed ID block at line", i+1)
        break

for i in range(len(lines)):
    if target_logout in lines[i] and not fixed_en:
        lines[i] = new_en_keys
        fixed_en = True
        print("Fixed EN block at line", i+1)
        break

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("DONE", fixed_id, fixed_en)
