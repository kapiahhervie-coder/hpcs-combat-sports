"""
perbaiki_encoding.py
Memperbaiki karakter rusak (U+FFFD / '<27>') di l2_strenght.html
berdasarkan konteks:
  1. Angka-<27>-angka/BW/reps (mis. "1.5<27> BW", "5<27> reps") -> tanda kali (x)
  2. Angka-<27>-angka (mis. "9<27>10", "1.0<27>1.49")            -> en dash (-)
  3. Sisanya (judul, placeholder, teks deskriptif)              -> em dash (--)

Membuat backup otomatis sebelum menulis ulang file.
"""
import os
import re
import shutil
from datetime import datetime

FILEPATH = os.path.join('boxing', 'templates', 'boxing', 'l2_strenght.html')

def main():
    if not os.path.exists(FILEPATH):
        print(f"File tidak ditemukan: {FILEPATH}")
        print("Pastikan script ini dijalankan dari root project Django Anda.")
        return

    # Backup dulu
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = FILEPATH + f'.backup-{timestamp}'
    shutil.copy2(FILEPATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    before_count = content.count('\ufffd')
    print(f"Karakter rusak ditemukan sebelum perbaikan: {before_count}")

    KALI = '\u00d7'   # x
    ENDASH = '\u2013' # -
    EMDASH = '\u2014' # --

    # 1. Angka diikuti char rusak lalu spasi+BW atau spasi+reps -> tanda kali (x)
    content = re.sub(r'(\d)\ufffd(\s*(?:BW|reps))', lambda m: m.group(1) + KALI + m.group(2), content)

    # 2. Angka - char rusak - angka (rentang) -> en dash
    content = re.sub(r'(\d)\ufffd(\d)', lambda m: m.group(1) + ENDASH + m.group(2), content)

    # 3. Sisa karakter rusak -> em dash
    content = content.replace('\ufffd', EMDASH)

    after_count = content.count('\ufffd')
    print(f"Karakter rusak tersisa setelah perbaikan: {after_count}")

    with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print(f"\nSelesai. File sudah ditulis ulang sebagai UTF-8: {FILEPATH}")
    print("Silakan cek hasilnya dengan python manage.py check dan refresh browser.")

if __name__ == '__main__':
    main()
