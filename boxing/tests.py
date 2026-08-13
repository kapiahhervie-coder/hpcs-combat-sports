"""
Unit test untuk fungsi kalkulasi skor L4 — Speed & Agility (Boxing).

Mengunci formula (threshold rubrik NSCA/ACSM per kategori usia & gender) di
hitung_skor_hex / hitung_skor_punch / hitung_skor_yoyo supaya kalau ada yang
tidak sengaja mengubah angka threshold di masa depan, test ini langsung
gagal (bukan ketahuan pas production, dari keluhan pelatih kayak sebelumnya).

Cara jalankan:
    python manage.py test boxing.tests

Sesuaikan baris import di bawah ini dengan lokasi sebenarnya dari
hitung_skor_hex / hitung_skor_punch / hitung_skor_yoyo di project kamu
(saat ini ada di boxing/views.py).
"""
from django.test import SimpleTestCase

from boxing.views import (
    hitung_skor_hex,
    hitung_skor_punch,
    hitung_skor_yoyo,
    YOYO_JARAK_TABLE,
)


class HitungSkorHexTest(SimpleTestCase):
    """calcHex() versi Python — rata-rata 3 putaran -> skor 0-10 sesuai
    rubrik NSCA/ACSM (SOP L4, Agustus 2026), per kategori & gender."""

    def test_rata_rata_dihitung_benar(self):
        # (9.0 + 10.0 + 11.0) / 3 = 10.0
        skor, avg = hitung_skor_hex(9.0, 10.0, 11.0, 'SENIOR', 'Putra')
        self.assertEqual(avg, 10.0)

    def test_mengabaikan_putaran_kosong_atau_nol(self):
        # Hanya 2 dari 3 putaran diisi -> tetap dihitung dari yang valid
        skor, avg = hitung_skor_hex(10.0, None, 12.0, 'SENIOR', 'Putra')
        self.assertEqual(avg, 11.0)
        # avg 11.0 masuk bracket Senior Putra 10.01-11.50 -> Good (5.5)
        self.assertEqual(skor, 5.5)

    def test_semua_kosong_hasil_nol(self):
        skor, avg = hitung_skor_hex(None, None, None, 'SENIOR', 'Putra')
        self.assertEqual(skor, 0)
        self.assertIsNone(avg)

    def test_senior_putra_semua_ambang_batas(self):
        kasus = [
            (8.79, 9.5), (8.80, 9.5),                 # Superior
            (8.81, 7.5), (10.00, 7.5),                # Excellent
            (10.01, 5.5), (11.50, 5.5),                # Good
            (11.51, 3.5), (13.00, 3.5),                # Fair
            (13.01, 1.5), (20.00, 1.5),                # Novice
        ]
        for waktu, expected_skor in kasus:
            with self.subTest(waktu=waktu):
                skor, _ = hitung_skor_hex(waktu, waktu, waktu, 'SENIOR', 'Putra')
                self.assertEqual(skor, expected_skor)

    def test_senior_putri_beda_dari_putra(self):
        skor, _ = hitung_skor_hex(9.80, 9.80, 9.80, 'SENIOR', 'Putri')
        self.assertEqual(skor, 9.5)  # ambang Putri lebih longgar dari Putra

    def test_junior_beda_dari_senior(self):
        # 13.00 dtk -> Senior Putra = Fair (3.5), Junior Putra = Good (5.5)
        # (ambang Junior lebih longgar karena secara fisik belum dewasa penuh)
        skor_senior, _ = hitung_skor_hex(13.00, 13.00, 13.00, 'SENIOR', 'Putra')
        skor_junior, _ = hitung_skor_hex(13.00, 13.00, 13.00, 'JUNIOR', 'Putra')
        self.assertEqual(skor_senior, 3.5)
        self.assertEqual(skor_junior, 5.5)

    def test_youth_pakai_tabel_anak_anak(self):
        # 12.00 dtk -> Youth Putra Superior (<=12.00)
        skor, _ = hitung_skor_hex(12.00, 12.00, 12.00, 'YOUTH', 'Putra')
        self.assertEqual(skor, 9.5)

    def test_elite_pakai_tabel_senior(self):
        skor_elite, _ = hitung_skor_hex(9.00, 9.00, 9.00, 'ELITE', 'Putra')
        skor_senior, _ = hitung_skor_hex(9.00, 9.00, 9.00, 'SENIOR', 'Putra')
        self.assertEqual(skor_elite, skor_senior)


class HitungSkorPunchTest(SimpleTestCase):
    """autoScorePunch() versi Python — jumlah pukulan/10 detik -> skor 0-10
    sesuai rubrik NSCA/ACSM, per kategori & gender."""

    def test_freq_kosong_hasil_nol(self):
        self.assertEqual(hitung_skor_punch(None, True, 'SENIOR', 'Putra'), 0)
        self.assertEqual(hitung_skor_punch(0, True, 'SENIOR', 'Putra'), 0)

    def test_senior_putra_semua_ambang_batas(self):
        kasus = [
            (89, 7.5), (90, 9.5), (91, 9.5),           # Excellent -> Superior
            (79, 7.5), (78, 5.5),                       # Excellent / Good
            (67, 5.5), (66, 3.5),                       # Good / Fair
            (55, 3.5), (54, 1.5),                       # Fair / Novice
        ]
        for freq, expected_skor in kasus:
            with self.subTest(freq=freq):
                self.assertEqual(hitung_skor_punch(freq, True, 'SENIOR', 'Putra'), expected_skor)

    def test_postur_salah_mengurangi_satu_tingkatan_skor(self):
        # 90 pukulan (postur benar) = Superior (9.5); postur salah -> -1 -> 8.5
        self.assertEqual(hitung_skor_punch(90, False, 'SENIOR', 'Putra'), 8.5)

    def test_postur_salah_tidak_boleh_di_bawah_novice(self):
        # 55 pukulan (postur benar) = Fair (3.5); postur salah -> 2.5 (masih >= Novice 1.5)
        skor = hitung_skor_punch(55, False, 'SENIOR', 'Putra')
        self.assertGreaterEqual(skor, 1.5)
        self.assertEqual(skor, 2.5)

    def test_gender_berbeda_threshold(self):
        skor_putra, _ = hitung_skor_punch(79, True, 'SENIOR', 'Putra'), None
        skor_putri = hitung_skor_punch(79, True, 'SENIOR', 'Putri')
        self.assertEqual(skor_putri, 9.5)  # 79 = Superior utk Putri (ambang lebih rendah)


class HitungSkorYoyoTest(SimpleTestCase):
    """calcYoYo() + calcVO2Max() versi Python -> skor 0-10 sesuai rubrik
    NSCA/ACSM (skor dari jarak tempuh), VO2 max cuma info tambahan."""

    def test_level_shuttle_kosong_hasil_nol(self):
        skor, vo2 = hitung_skor_yoyo(None, None, None, 'SENIOR', 'Putra')
        self.assertEqual(skor, 0)
        self.assertIsNone(vo2)

    def test_lookup_tabel_dipakai_jika_tersedia(self):
        # level 13, shuttle 4 -> 1280 m (lihat YOYO_JARAK_TABLE)
        self.assertEqual(YOYO_JARAK_TABLE[13][4], 1280)
        skor, vo2 = hitung_skor_yoyo(13, 4, None, 'SENIOR', 'Putra')
        # vo2 = 1280*0.0084 + 36.4 = 47.152 => dibulatkan 47.2 (info saja)
        self.assertAlmostEqual(vo2, 47.2, places=1)
        # 1280m Senior Putra -> antara Good(1200) & Excellent(1640) -> Good (5.5)
        self.assertEqual(skor, 5.5)

    def test_estimasi_kasar_jika_kombinasi_tidak_ada_di_tabel(self):
        # level 5, shuttle 9 tidak ada di tabel -> estimasi level*shuttle*20
        skor, vo2 = hitung_skor_yoyo(5, 9, None, 'SENIOR', 'Putra')
        jarak_estimasi = 5 * 9 * 20  # 900
        vo2_expected = round(jarak_estimasi * 0.0084 + 36.4, 1)
        self.assertAlmostEqual(vo2, vo2_expected, places=1)

    def test_jarak_manual_dipakai_jika_level_shuttle_kosong(self):
        skor, vo2 = hitung_skor_yoyo(None, None, 2000, 'SENIOR', 'Putra')
        vo2_expected = round(2000 * 0.0084 + 36.4, 1)
        self.assertAlmostEqual(vo2, vo2_expected, places=1)

    def test_senior_putra_semua_ambang_batas(self):
        kasus = [
            (2079, 7.5), (2080, 9.5),                  # Excellent -> Superior
            (1640, 7.5), (1639, 5.5),                  # Excellent / Good
            (1200, 5.5), (1199, 3.5),                  # Good / Fair
            (800, 3.5), (799, 1.5),                     # Fair / Novice
        ]
        for jarak, expected_skor in kasus:
            with self.subTest(jarak=jarak):
                skor, _ = hitung_skor_yoyo(None, None, jarak, 'SENIOR', 'Putra')
                self.assertEqual(skor, expected_skor)

    def test_jarak_negatif_atau_nol_ditolak(self):
        skor, vo2 = hitung_skor_yoyo(None, None, -100, 'SENIOR', 'Putra')
        self.assertEqual(skor, 0)
        self.assertIsNone(vo2)

    def test_youth_pakai_tabel_anak_anak(self):
        # Youth Putra Superior >= 920m
        skor, _ = hitung_skor_yoyo(None, None, 920, 'YOUTH', 'Putra')
        self.assertEqual(skor, 9.5)