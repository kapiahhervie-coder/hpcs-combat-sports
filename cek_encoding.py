"""
cek_encoding.py
Scan semua file .html di boxing/templates/boxing/ untuk menghitung
berapa banyak karakter rusak (U+FFFD, tampil sebagai '�') di tiap file.
TIDAK mengubah apapun -- murni untuk diagnosis dulu.
"""
import os
import glob

FOLDER = os.path.join('boxing', 'templates', 'boxing')

def main():
    pattern = os.path.join(FOLDER, '*.html')
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"Tidak ada file .html ditemukan di: {FOLDER}")
        print("Pastikan script ini dijalankan dari root project Django Anda.")
        return

    total_semua = 0
    for filepath in files:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        count = content.count('\ufffd')
        total_semua += count
        status = f"{count} karakter rusak" if count > 0 else "bersih"
        print(f"{os.path.basename(filepath):35s} -> {status}")

    print()
    print(f"Total karakter rusak di semua file: {total_semua}")

if __name__ == '__main__':
    main()
