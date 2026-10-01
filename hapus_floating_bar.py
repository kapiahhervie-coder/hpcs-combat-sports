"""
hapus_floating_bar.py
Hapus floating action bar (Download PDF / Kirim WhatsApp / Print) di
bagian bawah halaman L1-L4 Boxing -- karena udah redundan sama tombol
print/WA per-baris yang ada di tabel history.

Yang dihapus: <div id="hpcs-action-bar">...</div> + spacer div +
<script id="hpcs-action-script">...</script> secara utuh.

Fungsi getNamaAtlet/hpcsPrint/hpcsDownloadPDF/hpcsKirimWA di dalam
script ini TIDAK dipakai di tempat lain (tombol per-baris pakai
cetakL3Row/kirimWARow dkk yang terima parameter langsung dari
template), jadi aman dihapus total.
"""
import re

files = [
    "boxing/templates/boxing/l1_correction.html",
    "boxing/templates/boxing/l2_strenght.html",
    "boxing/templates/boxing/l3_power.html",
    "boxing/templates/boxing/l4_speed_agility.html",
]

pattern = re.compile(
    r'<div id="hpcs-action-bar".*?</script>\s*',
    re.DOTALL
)

for fpath in files:
    try:
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"SKIP (file tidak ada): {fpath}")
        continue

    new_content, jumlah = pattern.subn('', content)

    if jumlah > 0:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"OK ({jumlah} blok dihapus): {fpath}")
    else:
        print(f"SKIP (floating bar tidak ditemukan, mungkin memang tidak ada): {fpath}")

print("\nSELESAI.")
