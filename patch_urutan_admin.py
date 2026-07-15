"""
patch_urutan_admin.py
Mengganti verbose_name/verbose_name_plural di combat/models.py supaya
Django Admin menampilkan urutan L1, L2, L3, L4 secara berurutan
(Django mengurutkan sidebar berdasarkan abjad verbose_name_plural).
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('combat', 'models.py')

REPLACEMENTS = [
    (
        "CorrectionAuditL1 (L1)",
        "verbose_name        = 'Correction Audit L1'\n        verbose_name_plural = 'Correction Audit L1'",
        "verbose_name        = 'L1 - Correction'\n        verbose_name_plural = 'L1 - Correction'",
    ),
    (
        "StrengthAuditL2 (L2)",
        "verbose_name        = 'Strength Audit L2'\n        verbose_name_plural = 'Strength Audit L2'",
        "verbose_name        = 'L2 - Strength'\n        verbose_name_plural = 'L2 - Strength'",
    ),
    (
        "PowerAuditL3 (L3)",
        "verbose_name        = 'Power Audit L3'\n        verbose_name_plural = 'Power Audit L3'",
        "verbose_name        = 'L3 - Power'\n        verbose_name_plural = 'L3 - Power'",
    ),
    (
        "SpeedAgilityAuditL4 (L4)",
        "verbose_name        = 'Audit L4 \u2014 Speed & Agility'\n        verbose_name_plural = 'Audit L4 \u2014 Speed & Agility'",
        "verbose_name        = 'L4 - Speed & Agility'\n        verbose_name_plural = 'L4 - Speed & Agility'",
    ),
]


def main():
    if not os.path.exists(FILEPATH):
        print(f"File tidak ditemukan: {FILEPATH}")
        return

    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    original_content = content
    applied = []
    skipped = []
    warned = []

    for label, old, new in REPLACEMENTS:
        count = content.count(old)
        if count == 0:
            if content.count(new) >= 1:
                skipped.append(f"{label} (sudah benar)")
            else:
                warned.append(f"{label} (blok lama tidak ditemukan persis)")
        elif count == 1:
            content = content.replace(old, new)
            applied.append(label)
        else:
            warned.append(f"{label} (ditemukan {count}x, seharusnya 1x)")

    if content == original_content:
        print("Tidak ada perubahan dilakukan.")
    else:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = FILEPATH + f'.backup-{timestamp}'
        shutil.copy2(FILEPATH, backup_path)
        print(f"Backup dibuat: {backup_path}\n")

        with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"File ditulis ulang: {FILEPATH}\n")

    print("=== RINGKASAN ===")
    for a in applied:
        print(f"  [OK] {a}")
    for s in skipped:
        print(f"  [-]  {s}")
    for w in warned:
        print(f"  [!]  {w}")

    print("\nJalankan 'python manage.py makemigrations' lalu 'python manage.py migrate' untuk verifikasi.")


if __name__ == '__main__':
    main()
