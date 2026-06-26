path = r'combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
old = '/audit/hapus/'
new = '/combat/l1-correction/hapus/'
if old in c:
    c = c.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('DONE - URL hapus berhasil diperbaiki!')
else:
    print('TIDAK DITEMUKAN')
