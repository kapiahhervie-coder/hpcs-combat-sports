path = r'combat\views.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix indentation error di sekitar line 165
for i, line in enumerate(lines):
    if 'print("L2 POST:"' in line or 'print("POST DATA:"' in line:
        print(f'Ditemukan di line {i+1}: {line.rstrip()}')
        # Hapus baris debug yang bermasalah
        lines[i] = ''
        print(f'Dihapus')

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('DONE')
