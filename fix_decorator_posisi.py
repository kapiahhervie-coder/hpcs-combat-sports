"""
fix_decorator_posisi.py
Memperbaiki posisi @admin.register(Atlet) yang ter-pisah dari
class AtletAdmin akibat penyisipan fungsi export_ke_excel di antaranya.
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('combat', 'admin.py')

def main():
    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    DECORATOR = "@admin.register(Atlet)\n"
    CLASS_LINE = "class AtletAdmin(admin.ModelAdmin):"

    if content.count(DECORATOR) != 1:
        print(f"Peringatan: '{DECORATOR.strip()}' ditemukan {content.count(DECORATOR)}x, perlu tepat 1x. Dibatalkan.")
        return

    if content.count(CLASS_LINE) != 1:
        print(f"Peringatan: '{CLASS_LINE}' ditemukan {content.count(CLASS_LINE)}x, perlu tepat 1x. Dibatalkan.")
        return

    # Cek: apakah decorator SUDAH tepat di atas class (kondisi sudah benar)?
    idx_class = content.find(CLASS_LINE)
    before_class = content[:idx_class]
    if before_class.rstrip().endswith("@admin.register(Atlet)"):
        print("Sudah benar -- decorator sudah tepat di atas class AtletAdmin. Tidak ada perubahan.")
        return

    # Hapus decorator dari posisi lamanya, sisipkan tepat sebelum class
    content_no_decorator = content.replace(DECORATOR, "", 1)
    content_fixed = content_no_decorator.replace(CLASS_LINE, DECORATOR + CLASS_LINE, 1)

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = FILEPATH + f'.backup-{timestamp}'
    shutil.copy2(FILEPATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
        f.write(content_fixed)

    print("Berhasil memindahkan @admin.register(Atlet) ke posisi yang benar (tepat di atas class AtletAdmin).")
    print("Jalankan 'python manage.py check' untuk verifikasi.")

if __name__ == '__main__':
    main()
