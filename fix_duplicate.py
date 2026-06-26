"""
Script pembersih duplikat class DashboardMuayThaiView di combat/views.py

CARA PAKAI:
1. Pastikan file ini disimpan sebagai fix_duplicate.py di root project
   (folder yang sama dengan manage.py)
2. Jalankan: python fix_duplicate.py
3. Script akan otomatis backup dulu, lalu membersihkan
"""

import re
import shutil

SOURCE = "combat/views.py"
BACKUP = "combat/views_BACKUP_auto.py"

# 1. Backup dulu
shutil.copy(SOURCE, BACKUP)
print(f"Backup dibuat: {BACKUP}")

with open(SOURCE, "r", encoding="utf-8") as f:
    content = f.read()

# 2. Pola untuk menangkap SATU blok lengkap:
#    komentar divider + class DashboardMuayThaiView + isinya sampai
#    "return render(request, self.template_name, context)"
pattern = re.compile(
    r"\n*# ═+\n"
    r"# DASHBOARD MUAY THAI \(L1\)\n"
    r"# ═+\n"
    r"\nclass DashboardMuayThaiView\(LoginRequiredMixin, View\):\n"
    r"(?:.*?\n)*?"
    r"        return render\(request, self\.template_name, context\)\n",
)

matches = list(pattern.finditer(content))
print(f"Ditemukan {len(matches)} blok DashboardMuayThaiView")

if len(matches) == 0:
    print("Tidak ada yang cocok dengan pola. Tidak ada perubahan dilakukan.")
elif len(matches) == 1:
    print("Hanya ada 1 blok. Tidak ada duplikat untuk dihapus.")
else:
    # Simpan blok PERTAMA, hapus sisanya (mulai dari yang terakhir
    # supaya index tidak bergeser)
    keep = matches[0]
    remove = matches[1:]

    new_content = content
    for m in reversed(remove):
        new_content = new_content[: m.start()] + new_content[m.end():]

    # Bersihkan baris kosong berlebih (3+ newline jadi 2)
    new_content = re.sub(r"\n{3,}", "\n\n", new_content)

    with open(SOURCE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Berhasil! Menyisakan 1 blok, menghapus {len(remove)} duplikat.")
    print("Jalankan ulang Select-String untuk verifikasi.")
