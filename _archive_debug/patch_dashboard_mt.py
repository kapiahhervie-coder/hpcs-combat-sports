"""
patch_dashboard_mt.py
Mengganti 2 baris terakhir di DashboardMuayThaiView yang masih
memakai CorrectionAuditL1 (lama) -> CorrectionAuditL1MT (baru).
Backup otomatis sebelum menulis ulang.
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('muaythai', 'views.py')

OLD_1 = "riwayat = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('timestamp')[:8]"
NEW_1 = "riwayat = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('timestamp')[:8]"

OLD_2 = "l1_last = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None"
NEW_2 = "l1_last = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None"

OLD_3 = "l1 = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first()"
NEW_3 = "l1 = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('-timestamp').first()"

def main():
    if not os.path.exists(FILEPATH):
        print(f"File tidak ditemukan: {FILEPATH}")
        return

    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    missing = []
    if content.count(OLD_1) != 1:
        missing.append(f"Baris riwayat (ditemukan {content.count(OLD_1)}x, perlu 1x)")
    if content.count(OLD_2) != 1:
        missing.append(f"Baris l1_last (ditemukan {content.count(OLD_2)}x, perlu 1x)")
    if content.count(OLD_3) != 1:
        missing.append(f"Baris l1 (ReportCard) (ditemukan {content.count(OLD_3)}x, perlu 1x)")

    if missing:
        print("Tidak bisa lanjut, masalah berikut ditemukan:")
        for m in missing:
            print(f"  - {m}")
        print("Tidak ada perubahan dilakukan.")
        return

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = FILEPATH + f'.backup-{timestamp}'
    shutil.copy2(FILEPATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    content = content.replace(OLD_1, NEW_1)
    content = content.replace(OLD_2, NEW_2)
    content = content.replace(OLD_3, NEW_3)

    with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print("Berhasil mengganti 3 baris (dashboard riwayat, l1_last, dan ReportCard l1).")
    print("Jalankan 'python manage.py check' untuk verifikasi.")

if __name__ == '__main__':
    main()
