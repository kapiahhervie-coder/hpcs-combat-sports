"""
Helper untuk fitur Impor Siswa Massal (CSV).

Filosofi: satu file bisa berisi baris valid dan tidak valid sekaligus —
guru tidak perlu file 100% sempurna. Baris valid tetap disimpan, baris
error dilaporkan dengan nomor baris & alasannya supaya gampang diperbaiki.
"""

import csv
import io
from datetime import datetime

KOLOM_WAJIB = ['nama', 'kelas', 'jenis_kelamin', 'tanggal_lahir']


def _deteksi_delimiter(konten):
    """
    Deteksi otomatis apakah file pakai koma (,) atau titik-koma (;) sebagai pemisah kolom.
    Excel versi Indonesia/Eropa biasanya export CSV pakai titik-koma (karena koma
    dipakai untuk desimal), sedangkan Excel versi Inggris/US pakai koma.
    """
    baris_pertama = konten.split('\n', 1)[0]
    return ';' if baris_pertama.count(';') >= baris_pertama.count(',') else ','


def baca_csv_siswa(file_upload):
    """
    Baca file upload CSV dan hasilkan list dict per baris (mentah, belum divalidasi).
    Menerima file dengan header kolom: nama, kelas, jenis_kelamin, tanggal_lahir
    (urutan kolom bebas, huruf besar/kecil tidak masalah, pemisah koma ATAU titik-koma).
    """
    konten = file_upload.read().decode('utf-8-sig')  # utf-8-sig biar aman kalau ada BOM dari Excel
    delimiter = _deteksi_delimiter(konten)
    reader = csv.DictReader(io.StringIO(konten), delimiter=delimiter)

    if reader.fieldnames is None:
        return [], ['File CSV kosong atau tidak punya baris header.']

    header_lower = [h.strip().lower() for h in reader.fieldnames]
    kolom_hilang = [k for k in KOLOM_WAJIB if k not in header_lower]
    if kolom_hilang:
        return [], [f"Kolom wajib tidak ditemukan di header: {', '.join(kolom_hilang)}. "
                     f"Kolom yang ada: {', '.join(reader.fieldnames)}"]

    # Normalisasi nama kolom jadi lowercase supaya konsisten diakses
    baris_list = []
    for row in reader:
        baris_normal = {k.strip().lower(): (v or '').strip() for k, v in row.items()}
        baris_list.append(baris_normal)

    return baris_list, []


def validasi_baris_siswa(baris_list):
    """
    Validasi tiap baris siswa. Mengembalikan (baris_valid, daftar_error).
    baris_valid: list dict siap dipakai untuk membuat objek Siswa.
    daftar_error: list string "Baris N: alasan".
    """
    baris_valid = []
    daftar_error = []

    for nomor, baris in enumerate(baris_list, start=2):  # mulai dari 2 karena baris 1 = header
        nama = baris.get('nama', '')
        kelas = baris.get('kelas', '')
        jk_mentah = baris.get('jenis_kelamin', '').upper()
        tanggal_mentah = baris.get('tanggal_lahir', '')

        error_baris = []

        if not nama:
            error_baris.append('nama kosong')
        if not kelas:
            error_baris.append('kelas kosong')

        if jk_mentah not in ('L', 'P'):
            error_baris.append(f"jenis_kelamin harus 'L' atau 'P' (ditemukan: '{jk_mentah}')")

        tanggal_lahir = None
        if not tanggal_mentah:
            error_baris.append('tanggal_lahir kosong')
        else:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    tanggal_lahir = datetime.strptime(tanggal_mentah, fmt).date()
                    break
                except ValueError:
                    continue
            if tanggal_lahir is None:
                error_baris.append(f"format tanggal_lahir tidak dikenali: '{tanggal_mentah}' "
                                     f"(pakai format YYYY-MM-DD, contoh: 2015-08-17)")

        if error_baris:
            daftar_error.append(f"Baris {nomor}: {', '.join(error_baris)}")
        else:
            baris_valid.append({
                'nama': nama,
                'kelas': kelas,
                'jenis_kelamin': jk_mentah,
                'tanggal_lahir': tanggal_lahir,
            })

    return baris_valid, daftar_error


def buat_template_csv():
    """
    Hasilkan konten CSV template kosong (dengan 2 baris contoh) untuk diunduh guru.
    Pakai titik-koma (;) sebagai pemisah karena itu yang dikenali otomatis oleh
    Excel versi Indonesia saat file dibuka langsung (double-click) — bukan cuma
    lewat menu Import. BOM (\\ufeff) ditambahkan supaya Excel tidak salah baca
    karakter (misalnya kalau nanti ada nama siswa berhuruf non-standar).
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['nama', 'kelas', 'jenis_kelamin', 'tanggal_lahir'])
    writer.writerow(['Contoh: Budi Santoso', '5A', 'L', '2015-08-17'])
    writer.writerow(['Contoh: Siti Aminah', '5A', 'P', '2015-03-22'])
    return '\ufeff' + output.getvalue()