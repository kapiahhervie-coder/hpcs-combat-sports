path = r'combat\views.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = '        try:\n            atlet_id = request.POST.get'
new = '        print("POST DATA:", dict(request.POST))\n        try:\n            atlet_id = request.POST.get'

if old in c:
    c = c.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('DONE - debug print ditambahkan')
else:
    print('TIDAK DITEMUKAN - cek manual')
