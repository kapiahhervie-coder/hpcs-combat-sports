"""
patch_reportcard_mt.py
Mengganti baris terakhir di ReportCard view yang masih memakai
CorrectionAuditL1 (lama) -> CorrectionAuditL1MT (baru).
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('muaythai', 'views.py')

OLD = "l1 = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first()"
NEW = "l1 = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('-timestamp').first()"

def main():
    if not os.path.exists(FILEPATH):
        print(f"File tidak ditemukan: {FILEPATH}")
        return

    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    count = content.count(OLD)
    if count != 1:
        print(f"Baris target ditemukan {count}x (perlu tepat 1x). Tidak ada perubahan dilakukan.")
        return

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = FILEPATH + f'.backup-{timestamp}'
    shutil.copy2(FILEPATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    content = content.replace(OLD, NEW)

    with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print("Berhasil mengganti baris di ReportCard view.")
    print("Jalankan 'python manage.py check' untuk verifikasi.")

if __name__ == '__main__':
    main()
