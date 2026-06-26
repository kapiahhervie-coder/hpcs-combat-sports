path = r'D:\LIBRERY\Phyton\HPCS Combat Sports\combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix URL hapus yang salah
old = 'fetch(/audit/hapus//'
new = 'fetch(/combat/l1-correction/hapus//'

if old in content:
    content = content.replace(old, new)
    print('DONE - URL hapus diperbaiki')
else:
    print('TIDAK DITEMUKAN - cek manual')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
