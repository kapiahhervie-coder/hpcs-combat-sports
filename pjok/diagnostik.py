"""
Logika diagnostik akar masalah PJOK.

Filosofi: kalau skor teknik (Elemen Keterampilan Gerak) siswa rendah,
sistem menelusuri komponen fisik dasar (L1-L4, Elemen Pemanfaatan Gerak)
mana yang juga rendah, untuk membantu guru menemukan akar masalah —
bukan sekadar memberi angka tanpa konteks.
"""

AMBANG_BATAS_DEFAULT = 70


def hitung_skor_l1(plank_hold_detik, sit_and_reach_cm, referensi):
    """
    Hitung skor L1 (Core & Mobility) berdasarkan referensi TKJI fase siswa.
    `referensi` adalah dict berisi nilai acuan minimal/maksimal per fase.
    Placeholder sederhana — sesuaikan bobot & tabel norma per fase saat data resmi tersedia.
    """
    skor_plank = min(100, (plank_hold_detik / referensi.get('plank_target_detik', 60)) * 100)
    skor_fleksibilitas = min(100, (sit_and_reach_cm / referensi.get('reach_target_cm', 20)) * 100)
    return round((skor_plank + skor_fleksibilitas) / 2, 1)


def hitung_skor_l2(gantung_durasi_detik, sit_up_repetisi, referensi):
    """Skor L2 (Strength) berbasis norma TKJI: gantung siku tekuk + sit up."""
    skor_gantung = min(100, (gantung_durasi_detik / referensi.get('gantung_target_detik', 30)) * 100)
    skor_situp = min(100, (sit_up_repetisi / referensi.get('situp_target_repetisi', 25)) * 100)
    return round((skor_gantung + skor_situp) / 2, 1)


def hitung_skor_l3(vertical_jump_cm, referensi):
    """Skor L3 (Power) berbasis norma TKJI: loncat tegak."""
    return round(min(100, (vertical_jump_cm / referensi.get('vertical_jump_target_cm', 40)) * 100), 1)


def hitung_skor_l4(lari_cepat_detik, lari_menengah_detik, referensi):
    """
    Skor L4 (Speed & Agility) berbasis norma TKJI: lari jarak pendek + lari jarak menengah.
    Waktu lebih kecil = lebih baik, jadi skor dihitung terbalik.
    """
    target_cepat = referensi.get('lari_cepat_target_detik', 8)
    target_menengah = referensi.get('lari_menengah_target_detik', 180)
    skor_cepat = min(100, (target_cepat / lari_cepat_detik) * 100)
    skor_menengah = min(100, (target_menengah / lari_menengah_detik) * 100)
    return round((skor_cepat + skor_menengah) / 2, 1)


def diagnosa_akar_masalah(siswa, materi, ambang_batas=AMBANG_BATAS_DEFAULT):
    """
    Kalau skor teknik siswa untuk suatu materi rendah, cek komponen fisik L1-L4
    mana yang juga rendah, sebagai kandidat akar masalah.

    Mengembalikan list string penjelasan, atau None kalau skor teknik sudah baik.
    """
    teknik = (
        siswa.penilaian_teknik
        .filter(materi=materi)
        .order_by('-tanggal')
        .first()
    )
    fisik = siswa.penilaian_fisik.order_by('-tanggal_tes').first()

    if teknik is None or fisik is None:
        return None
    if teknik.skor >= ambang_batas:
        return None

    masalah = []
    if fisik.skor_l1 is not None and fisik.skor_l1 < ambang_batas:
        masalah.append(
            "Stabilitas & mobilitas dasar (L1) masih rendah — "
            "kemungkinan penyebab kontrol gerak/keseimbangan kurang baik."
        )
    if fisik.skor_l2 is not None and fisik.skor_l2 < ambang_batas:
        masalah.append(
            "Kekuatan (L2) masih rendah — "
            "kemungkinan penyebab gerakan yang butuh tenaga/kontak fisik lemah."
        )
    if fisik.skor_l3 is not None and fisik.skor_l3 < ambang_batas:
        masalah.append(
            "Power (L3) masih rendah — "
            "kemungkinan penyebab tendangan/lompatan/lemparan kurang bertenaga."
        )
    if fisik.skor_l4 is not None and fisik.skor_l4 < ambang_batas:
        masalah.append(
            "Kecepatan & kelincahan (L4) masih rendah — "
            "kemungkinan penyebab sulit mengejar/berkelit/bereaksi cepat."
        )

    if not masalah:
        masalah.append(
            "Skor teknik rendah tapi komponen fisik dasar normal — "
            "kemungkinan masalah ada di teknik/koordinasi gerak, bukan kondisi fisik."
        )
    return masalah


def rubrik_label(skor):
    """Ubah skor 0-100 jadi label rubrik + kelas warna untuk tampilan."""
    if skor is None:
        return {'label': 'Belum ada data', 'kelas': 'netral'}
    if skor >= 85:
        return {'label': 'Sangat Baik', 'kelas': 'baik'}
    if skor >= 70:
        return {'label': 'Baik', 'kelas': 'baik'}
    if skor >= 55:
        return {'label': 'Cukup', 'kelas': 'cukup'}
    return {'label': 'Perlu Perhatian', 'kelas': 'kurang'}


# Rekomendasi latihan konkret per komponen L1-L4 yang rendah.
# Ditujukan untuk guru praktikkan langsung di lapangan — bukan istilah teknis.
REKOMENDASI_LATIHAN = {
    'l1': [
        "Latihan plank progresif — 3 set x 15-30 detik",
        "Peregangan dinamis sebelum aktivitas inti (5-10 menit)",
        "Latihan keseimbangan satu kaki (single-leg stand) — 3 set x 20 detik per kaki",
    ],
    'l2': [
        "Push-up dengan modifikasi (bertumpu lutut/dinding) — 3 set x 8-12 repetisi",
        "Sit-up terpandu atau plank variasi — 3 set x 10-15 repetisi",
        "Latihan resistance band ringan untuk penguatan otot dasar",
    ],
    'l3': [
        "Lompat kotak rendah (box jump) — 3 set x 8 repetisi",
        "Lempar bola medicine ringan — 3 set x 10 repetisi",
        "Skipping / lompat tali — 3 set x 30 detik",
    ],
    'l4': [
        "Lari zig-zag antar cone — 4 set x 10 meter",
        "Ladder drill kecepatan kaki — 3 pola gerakan berbeda",
        "Permainan kejar-kejaran terstruktur (tag games) — 10 menit",
    ],
}

KOMPONEN_LABEL = {
    'l1': 'Core & Mobility',
    'l2': 'Strength',
    'l3': 'Power',
    'l4': 'Speed & Agility',
}


def rekomendasi_perbaikan(penilaian_fisik, ambang_batas=AMBANG_BATAS_DEFAULT):
    """
    Susun daftar rekomendasi latihan konkret untuk guru, berdasarkan
    komponen L1-L4 mana saja yang skornya di bawah ambang batas.
    """
    if penilaian_fisik is None:
        return []

    skor_map = {
        'l1': penilaian_fisik.skor_l1,
        'l2': penilaian_fisik.skor_l2,
        'l3': penilaian_fisik.skor_l3,
        'l4': penilaian_fisik.skor_l4,
    }

    hasil = []
    for kode, skor in skor_map.items():
        if skor is not None and skor < ambang_batas:
            hasil.append({
                'komponen': KOMPONEN_LABEL[kode],
                'skor': skor,
                'latihan': REKOMENDASI_LATIHAN[kode],
            })
    return hasil
