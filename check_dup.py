path = r'D:\LIBRERY\Phyton\HPCS Combat Sports\combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Cek baris 297-303
for i in range(296, 303):
    print(f'{i+1}|{repr(lines[i])}')
