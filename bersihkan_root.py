"""
bersihkan_root.py
Memindahkan file-file debug/patch sisa proses debugging sesi ini
ke folder _archive_debug/ -- TIDAK dihapus permanen, cuma dipindah
keluar dari root supaya rapi. Aman dijalankan berkali-kali.
"""
import os
import shutil

ARCHIVE_DIR = '_archive_debug'

# Kelompok A: file yang dibuat & sudah selesai dipakai di sesi ini (aman dipindah)
FILES_TO_ARCHIVE = [
    'cek_encoding.py',
    'lihat_konteks.py',
    'perbaiki_encoding.py',
    'perbaiki_encoding (2).py',
    'fix_typo_h.py',
    'fix_all_l1mt.py',
    'patch_muaythai_views.py',
    'patch_dashboard_mt.py',
    'patch_reportcard_mt.py',
    'muaythai_models_l1 (1).py',
    'l3_power_clean.html',
    os.path.join('muaythai', 'templates', 'muaythai', 'l1_correction_OLD.html'),

    # Kelompok B: file tidak dikenal dari sesi kerja sebelumnya, user tidak yakin
    # masih dipakai -- diarsipkan juga demi kerapian, tidak dihapus permanen.
    'audit_ltad.py',
    'cek_ltad2.py',
    'cek_ltad3.py',
    'fix_ltad_dup.py',
    'fix_validasi_usia.py',
    'views_combat_FIXED.py',
    'tambah_atlet_current.html',
]

def main():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    moved = []
    not_found = []

    for filepath in FILES_TO_ARCHIVE:
        if os.path.exists(filepath):
            dest_name = os.path.basename(filepath)
            dest_path = os.path.join(ARCHIVE_DIR, dest_name)
            # Hindari overwrite kalau nama sama sudah ada di arsip
            counter = 1
            base, ext = os.path.splitext(dest_name)
            while os.path.exists(dest_path):
                dest_path = os.path.join(ARCHIVE_DIR, f"{base}_{counter}{ext}")
                counter += 1
            shutil.move(filepath, dest_path)
            moved.append(f"{filepath}  ->  {dest_path}")
        else:
            not_found.append(filepath)

    print("=== DIPINDAHKAN ===")
    for m in moved:
        print(f"  [OK] {m}")

    if not_found:
        print("\n=== TIDAK DITEMUKAN (mungkin sudah dipindah/dihapus sebelumnya) ===")
        for n in not_found:
            print(f"  [-]  {n}")

    print(f"\nSelesai. Semua file dipindah ke folder: {ARCHIVE_DIR}/")
    print("File TIDAK dihapus permanen -- masih ada di folder arsip kalau sewaktu-waktu dibutuhkan.")

if __name__ == '__main__':
    main()
