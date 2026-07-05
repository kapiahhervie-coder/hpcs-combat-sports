"""
lihat_konteks.py
Menampilkan potongan teks di sekitar tiap karakter rusak (U+FFFD)
di l2_strenght.html, supaya bisa diverifikasi manual sebelum
dilakukan penggantian massal. TIDAK mengubah apapun.
"""
import os

FILEPATH = os.path.join('boxing', 'templates', 'boxing', 'l2_strenght.html')

def main():
    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    total = content.count('\ufffd')
    print(f"Total karakter rusak ditemukan: {total}\n")

    idx = 0
    n = 0
    while True:
        idx = content.find('\ufffd', idx)
        if idx == -1:
            break
        n += 1
        start = max(0, idx - 25)
        end = min(len(content), idx + 25)
        snippet = content[start:end].replace('\n', ' ')
        print(f"[{n}] ...{snippet}...")
        idx += 1

    print(f"\nTotal ditampilkan: {n}")

if __name__ == '__main__':
    main()
