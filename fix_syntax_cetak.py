fpath = "boxing/templates/boxing/l1_correction.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

# Fix syntax error pada baris label
bad  = "const label=p.v<5.5?'PRIORITAS':'p.v<7.5?'PERLU PERHATIAN':'PERTAHANKAN';"
good = "const label=p.v<5.5?'PRIORITAS':p.v<7.5?'PERLU PERHATIAN':'PERTAHANKAN';"

if bad in content:
    content = content.replace(bad, good)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK: syntax error berhasil diperbaiki!")
else:
    print("Pattern tidak ditemukan, cek manual")
    # Cari baris yang mengandung label
    for i, line in enumerate(content.split('\n'), 1):
        if 'const label' in line:
            print(f"Baris {i}: {line[:80]}")
