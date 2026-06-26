path = r'combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = "  var fokus=layak\n    ?'Fondasi biomekanik cukup kuat. Fokus perkuat <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> selama L2.'\n    :'Jalankan korektif 4&#8211;6 minggu, fokus <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> dan <strong>'+(lemah[1]?lemah[1].nama:'-')+'</strong>.';"

new = "  var fokus=semuaPrima\n    ?'Pertahankan performa di semua pilar. Atlet siap masuk program L2 Strength dengan beban penuh.'\n    :layak\n    ?'Fondasi biomekanik cukup kuat. Fokus perkuat <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> selama L2.'\n    :'Jalankan korektif 4&#8211;6 minggu, fokus <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> dan <strong>'+(lemah[1]?lemah[1].nama:'-')+'</strong>.';"

if old in c:
    c = c.replace(old, new)
    print('OK: kesimpulan diperbaiki')
else:
    print('SKIP')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
