"""
Unit test untuk fungsi kalkulasi skor L4 — Speed & Agility (Boxing).

Tujuan: mengunci formula (threshold) hitung_skor_hex / hitung_skor_punch /
hitung_skor_yoyo supaya kalau ada yang tidak sengaja mengubah angka
threshold di masa depan, test ini langsung gagal (bukan ketahuan pas
production, dari keluhan pelatih kayak sebelumnya).

Cara jalankan:
    python manage.py test boxing.tests.test_l4_scoring
atau kalau file ini berdiri sendiri (bukan bagian dari Django test runner):
    python manage.py shell -c "import boxing.tests.test_l4_scoring"
    (atau taruh di boxing/tests/test_l4_scoring.py sesuai struktur project)

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
    """calcHex() versi Python — rata-rata 3 putaran -> skor 0-10."""

    def test_rata_rata_dihitung_benar(self):
        # (9.0 + 10.0 + 11.0) / 3 = 10.0
        skor, avg = hitung_skor_hex(9.0, 10.0, 11.0)
        self.assertEqual(avg, 10.0)

    def test_mengabaikan_putaran_kosong_atau_nol(self):
        # Hanya 2 dari 3 putaran diisi -> tetap dihitung dari yang valid
        skor, avg = hitung_skor_hex(10.0, None, 12.0)
        self.assertEqual(avg, 11.0)
        # avg 11.0 masuk bracket "< 11.5" -> skor 7
        self.assertEqual(skor, 7)

    def test_semua_kosong_hasil_nol(self):
        skor, avg = hitung_skor_hex(None, None, None)
        self.assertEqual(skor, 0)
        self.assertIsNone(avg)

    def test_threshold_batas_atas_skor_10(self):
        # < 10 detik => skor 10
        skor, _ = hitung_skor_hex(9.9, 9.9, 9.9)
        self.assertEqual(skor, 10)

    def test_threshold_tepat_10_masuk_skor_9(self):
        # >= 10 dan < 10.5 => skor 9
        skor, _ = hitung_skor_hex(10.0, 10.0, 10.0)
        self.assertEqual(skor, 9)

    def test_semua_ambang_batas(self):
        kasus = [
            (9.99, 10),
            (10.0, 9), (10.49, 9),
            (10.5, 8), (10.99, 8),
            (11.0, 7), (11.49, 7),
            (11.5, 6), (11.99, 6),
            (12.0, 5), (12.99, 5),
            (13.0, 4), (13.99, 4),
            (14.0, 3), (20.0, 3),
        ]
        for waktu, expected_skor in kasus:
            with self.subTest(waktu=waktu):
                skor, _ = hitung_skor_hex(waktu, waktu, waktu)
                self.assertEqual(skor, expected_skor)


class HitungSkorPunchTest(SimpleTestCase):
    """autoScorePunch() versi Python — jumlah pukulan/10 detik -> skor 0-10."""

    def test_freq_kosong_hasil_nol(self):
        self.assertEqual(hitung_skor_punch(None, True), 0)
        self.assertEqual(hitung_skor_punch(0, True), 0)

    def test_semua_ambang_batas_postur_ok(self):
        kasus = [
            (25, 10), (30, 10),
            (22, 9), (24, 9),
            (20, 8), (21, 8),
            (18, 7), (19, 7),
            (16, 6), (17, 6),
            (14, 5), (15, 5),
            (12, 4), (13, 4),
            (11, 3), (1, 3),
        ]
        for freq, expected_skor in kasus:
            with self.subTest(freq=freq):
                self.assertEqual(hitung_skor_punch(freq, True), expected_skor)

    def test_postur_salah_mengurangi_1_poin(self):
        self.assertEqual(hitung_skor_punch(25, False), 9)
        self.assertEqual(hitung_skor_punch(20, False), 7)

    def test_postur_salah_tidak_boleh_minus(self):
        # skor terendah formula adalah 3, dikurangi 1 -> 2, tidak boleh di bawah 0
        skor = hitung_skor_punch(1, False)
        self.assertGreaterEqual(skor, 0)
        self.assertEqual(skor, 2)


class HitungSkorYoyoTest(SimpleTestCase):
    """calcYoYo() + calcVO2Max() versi Python -> skor 0-10."""

    def test_level_shuttle_kosong_hasil_nol(self):
        skor, vo2 = hitung_skor_yoyo(None, None, None)
        self.assertEqual(skor, 0)
        self.assertIsNone(vo2)

    def test_lookup_tabel_dipakai_jika_tersedia(self):
        # level 13, shuttle 4 -> 1280 m (lihat YOYO_JARAK_TABLE)
        self.assertEqual(YOYO_JARAK_TABLE[13][4], 1280)
        skor, vo2 = hitung_skor_yoyo(13, 4, None)
        # vo2 = 1280*0.0084 + 36.4 = 47.152 => dibulatkan 47.2
        self.assertAlmostEqual(vo2, 47.2, places=1)
        self.assertEqual(skor, 5)

    def test_estimasi_kasar_jika_kombinasi_tidak_ada_di_tabel(self):
        # level 5, shuttle 9 tidak ada di tabel -> estimasi level*shuttle*20
        skor, vo2 = hitung_skor_yoyo(5, 9, None)
        jarak_estimasi = 5 * 9 * 20  # 900
        vo2_expected = round(jarak_estimasi * 0.0084 + 36.4, 1)
        self.assertAlmostEqual(vo2, vo2_expected, places=1)

    def test_jarak_manual_dipakai_jika_level_shuttle_kosong(self):
        skor, vo2 = hitung_skor_yoyo(None, None, 2000)
        vo2_expected = round(2000 * 0.0084 + 36.4, 1)
        self.assertAlmostEqual(vo2, vo2_expected, places=1)

    def test_semua_ambang_batas_vo2(self):
        kasus = [
            (60.0, 10), (65.0, 10),
            (57.0, 9), (59.9, 9),
            (55.0, 8), (56.9, 8),
            (52.0, 7), (54.9, 7),
            (50.0, 6), (51.9, 6),
            (47.0, 5), (49.9, 5),
            (44.0, 4), (46.9, 4),
            (43.9, 3), (40.0, 3),
        ]
        for vo2_target, expected_skor in kasus:
            with self.subTest(vo2_target=vo2_target):
                # balik dari rumus vo2 = jarak*0.0084 + 36.4 -> cari jarak
                jarak = (vo2_target - 36.4) / 0.0084
                skor, _ = hitung_skor_yoyo(None, None, jarak)
                self.assertEqual(skor, expected_skor)

    def test_jarak_negatif_atau_nol_ditolak(self):
        # VO2 minimum secara fisik adalah 36.4 (di jarak 0m), jadi jarak
        # negatif tidak valid dan harus menghasilkan skor 0, bukan skor 3.
        skor, vo2 = hitung_skor_yoyo(None, None, -100)
        self.assertEqual(skor, 0)
        self.assertIsNone(vo2)