"""
fix_l3_multiline_string.py
Perbaiki bug newline mentah di dalam string JavaScript (hpcsKirimWA
dan kirimWARow) di boxing/l3_power.html -- newline mentah bikin
SyntaxError: Unterminated string literal, yang bikin SELURUH
<script> block gagal parse.
"""
import re

fpath = "boxing/templates/boxing/l3_power.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

perubahan = 0

# --- Fix 1: hpcsKirimWA() -----------------------------------------
lama_1 = """var pesan=encodeURIComponent('*LAPORAN AUDITL3 - HPCS BOXING*
Atlet: '+nama+'
Tanggal: '+tgl+'
Dikirim otomatis HPCS System');"""

baru_1 = """var pesan=encodeURIComponent('*LAPORAN AUDIT L3 - HPCS BOXING*\\nAtlet: '+nama+'\\nTanggal: '+tgl+'\\nDikirim otomatis HPCS System');"""

if lama_1 in content:
    content = content.replace(lama_1, baru_1)
    perubahan += 1
    print("OK: hpcsKirimWA() diperbaiki.")
else:
    print("SKIP: pola hpcsKirimWA() tidak ditemukan persis (mungkin sudah beda).")

# --- Fix 2: kirimWARow() -------------------------------------------
lama_2 = """  var pesan=encodeURIComponent(
    "*LAPORAN AUDIT L3 - HPCS BOXING*
"+
    "========================
"+
    "Atlet: "+nama+"
"+
    "Kategori: "+kat+"
"+
    "Tanggal: "+tgl+"
"+
    "========================
"+
    "Total Skor: "+parseFloat(total).toFixed(1)+"/10
"+
    "Predikat: "+predikat+"
"+
    "========================
"+
    "Dikirim otomatis oleh HPCS Boxing System"
  );"""

baru_2 = """  var pesan=encodeURIComponent(
    "*LAPORAN AUDIT L3 - HPCS BOXING*\\n"+
    "========================\\n"+
    "Atlet: "+nama+"\\n"+
    "Kategori: "+kat+"\\n"+
    "Tanggal: "+tgl+"\\n"+
    "========================\\n"+
    "Total Skor: "+parseFloat(total).toFixed(1)+"/10\\n"+
    "Predikat: "+predikat+"\\n"+
    "========================\\n"+
    "Dikirim otomatis oleh HPCS Boxing System"
  );"""

if lama_2 in content:
    content = content.replace(lama_2, baru_2)
    perubahan += 1
    print("OK: kirimWARow() diperbaiki.")
else:
    print("SKIP: pola kirimWARow() tidak ditemukan persis (mungkin sudah beda).")

if perubahan > 0:
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nSELESAI: {perubahan} fungsi diperbaiki dan disimpan ke {fpath}")
else:
    print("\nTIDAK ADA PERUBAHAN -- cek manual, pola tidak cocok.")