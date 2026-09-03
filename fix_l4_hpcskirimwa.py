"""
fix_l4_hpcskirimwa.py
Perbaiki bug newline mentah di fungsi hpcsKirimWA() di
l4_speed_agility.html -- pola sama persis dengan bug l3_power.html.
"""

fpath = "boxing/templates/boxing/l4_speed_agility.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

lama = """var pesan=encodeURIComponent('*LAPORAN AUDIT L4 - HPCS BOXING*
Atlet: '+nama+'
Tanggal: '+tgl+'
Dikirim otomatis HPCS System');"""

baru = """var pesan=encodeURIComponent('*LAPORAN AUDIT L4 - HPCS BOXING*\\nAtlet: '+nama+'\\nTanggal: '+tgl+'\\nDikirim otomatis HPCS System');"""

if lama in content:
    content = content.replace(lama, baru)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK: hpcsKirimWA() di l4_speed_agility.html berhasil diperbaiki.")
else:
    print("SKIP: pola tidak ditemukan persis -- kirim hasil Select-String biar disesuaikan.")
