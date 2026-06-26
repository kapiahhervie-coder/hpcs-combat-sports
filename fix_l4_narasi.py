path = r'combat\templates\combat\l4_speed_agility.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Tampilkan narasi meski hanya 1 pilar terisi
old = 'if (narL4 && narBoxL4 && filledL4.length > 0) {'
new = 'if (narL4 && narBoxL4 && a > 0) {'
if old in c:
    c = c.replace(old, new)
    print('OK 1: kondisi narasi dilonggarkan')
else:
    print('SKIP 1')

# FIX 2: Pastikan rekomendasi juga muncul meski pilar sedikit
old2 = 'sortedL4.slice(0,3).forEach(function(p){'
new2 = 'var topL4 = filledL4.length > 0 ? sortedL4.slice(0, Math.min(3,sortedL4.length)) : [];\n  topL4.forEach(function(p){'
if old2 in c:
    c = c.replace(old2, new2)
    print('OK 2: rekomendasi fix')
else:
    print('SKIP 2')

# FIX 3: Buat narasi_l4 sticky seperti L2
old3 = '<div id="narasi_l4" style="display:none;margin-top:10px;text-align:left;">'
new3 = '<div id="narasi_l4" style="display:none;margin-top:10px;text-align:left;max-height:350px;overflow-y:auto;">'
if old3 in c:
    c = c.replace(old3, new3)
    print('OK 3: narasi scrollable')
else:
    print('SKIP 3')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
