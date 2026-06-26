path = r'combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = 'id="narasi_box" style="background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.2);border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.7;color:var(--text2);text-align:left;"'
new = 'id="narasi_box" style="background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.2);border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.7;color:var(--text2);text-align:left;max-height:320px;overflow-y:auto;"'

if old in c:
    c = c.replace(old, new)
    print('OK: narasi_box scrollable')
else:
    old2 = 'id="narasi_box" style="background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.2);border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.7;color:var(--text2);"'
    new2 = 'id="narasi_box" style="background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.2);border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.7;color:var(--text2);text-align:left;max-height:320px;overflow-y:auto;"'
    if old2 in c:
        c = c.replace(old2, new2)
        print('OK: narasi_box scrollable (v2)')
    else:
        print('SKIP - cari manual id narasi_box')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
