content = open("combat/templates/combat/tambah_atlet.html", "r", encoding="utf-8").read()
import re

# Hitung berapa kali select tahap_ltad muncul
count = content.count('name="tahap_ltad"')
print(f"Jumlah select tahap_ltad: {count}")

# Tampilkan konteks sekitar kemunculan kedua jika ada
if count > 1:
    idx = content.find('name="tahap_ltad"')
    idx2 = content.find('name="tahap_ltad"', idx+1)
    print("Kemunculan ke-2 di sekitar:")
    print(repr(content[max(0,idx2-100):idx2+200]))
