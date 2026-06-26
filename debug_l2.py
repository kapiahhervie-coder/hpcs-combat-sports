path = r'combat\views.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = "        try:\n            atlet_id = request.POST.get('atlet_id')\n            atlet    = get_object_or_404(Atlet, pk=atlet_id) if atlet_id else None\n            def to_float(key):"

new = "        print('L2 POST:', dict(request.POST))\n        try:\n            atlet_id = request.POST.get('atlet_id')\n            atlet    = get_object_or_404(Atlet, pk=atlet_id) if atlet_id else None\n            def to_float(key):"

if old in c:
    c = c.replace(old, new)
    print('OK')
else:
    print('TIDAK DITEMUKAN')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
