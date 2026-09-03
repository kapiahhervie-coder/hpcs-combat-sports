"""
fix_l3_hpcskirimwa.py
Perbaiki bug newline mentah di fungsi hpcsKirimWA() di l3_power.html
(fix sebelumnya salah tebak spasi -- "AUDIT L3" bukan "AUDITL3").
"""

fpath = "boxing/templates/boxing/l3_power.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

lama = """var pesan=encodeURIComponent('*LAPORAN AUDIT L3 - HPCS BOXING*
Atlet: '+nama+'
Tanggal: '+tgl+'
Dikirim otomatis HPCS System');"""

baru = """var pesan=encodeURIComponent('*LAPORAN AUDIT L3 - HPCS BOXING*\\nAtlet: '+nama+'\\nTanggal: '+tgl+'\\nDikirim otomatis HPCS System');"""

if lama in content:
    content = content.replace(lama, baru)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK: hpcsKirimWA() berhasil diperbaiki.")
else:
    print("MASIH SKIP: coba cek manual, mungkin ada beda whitespace lain.")
