"""
muaythai/models.py
Model audit L1 -- Koreksi Biomekanik Muay Thai.
Direvisi mengikuti "SOP & Rubrik Asesmen Level 1: Koreksi Biomekanik
Muay Thai -- REVISI 2 (Norma Terupdate)".

6 parameter tes sesuai SOP:
  1. Ankle Mobility            -- Weight-Bearing Lunge Test (WBLT), jarak (cm)
  2. Seated Thoracic Rotation  -- sudut rotasi trunk (derajat)
  3. Hip Rotation Mobility     -- Internal & External Rotation (derajat)
  4. ASLR                      -- Active Straight Leg Raise (derajat)
  5. Lumbar Extension          -- Modified Cobra + Clearing Gate nyeri
  6. Lateral Pelvic Stability  -- Single-Leg Squat (knee valgus/Trendelenburg)

Setiap parameter diskor 1-10 langsung oleh pelatih mengikuti rubrik norma
di SOP (Kurang 1-4 / Cukup 5-7 / Baik-Ideal 8-10). total_skor = rata-rata
ke-6 skor tsb (skala 0-10) -- TIDAK lagi memakai skala neural 1-3
(Cognitive/Associative/Autonomous) dari versi sebelumnya, karena rubrik
resmi Muay Thai Revisi 2 memakai skala 1-10 langsung per parameter.

Model Atlet & lintas-cabang lain tetap dipakai bersama dari app 'combat'.
"""
from django.db import models
from django.utils import timezone
from combat.models import Atlet, KATEGORI_USIA_CHOICES, GENDER_CHOICES, PREDIKAT_CHOICES


LUMBAR_KUALITAS_CHOICES = [
    ('MULUS', 'Ekstensi mulus, tanpa kompensasi'),
    ('KOMPENSASI', 'Ada kompensasi bahu/panggul terangkat'),
    ('TERBATAS', 'ROM sangat terbatas'),
]

PELVIC_STABILITY_CHOICES = [
    ('STABIL', 'Alignment lurus, panggul stabil (tanpa valgus)'),
    ('RINGAN', 'Lutut bergoyang ringan / kompensasi minim'),
    ('VALGUS', 'Knee valgus parah / panggul anjlok (Trendelenburg sign)'),
]


class CorrectionAuditL1MT(models.Model):
    """
    L1 Correction -- Muay Thai (SOP Revisi 2)
    Fokus: mobilitas thorakal & panggul, fleksibilitas ankle, kontrol
    lumbal, dan stabilitas panggul lateral sebagai fondasi sebelum masuk
    ke teknik spesifik (pukulan, tendangan, siku/Sok, lutut/Khao, clinch).
    """
    # -- Identitas --------------------------------------------------
    atlet         = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='audit_l1_mt', verbose_name='Atlet')
    atlet_name    = models.CharField(max_length=150, blank=True, verbose_name='Nama Atlet (form)')
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True, verbose_name='Berat Badan (kg)')

    # -- 1. Ankle Mobility (Weight-Bearing Lunge Test) -----------------
    wblt_jarak_kanan_cm = models.FloatField(null=True, blank=True, verbose_name='WBLT Kanan (cm)')
    wblt_jarak_kiri_cm  = models.FloatField(null=True, blank=True, verbose_name='WBLT Kiri (cm)')
    skor_ankle_mobility = models.IntegerField(default=5, verbose_name='Skor Ankle Mobility (1-10)')

    # -- 2. Seated Thoracic Rotation -----------------------------------
    thoracic_rotasi_kanan  = models.FloatField(null=True, blank=True, verbose_name='Thoracic Rotation Kanan (derajat)')
    thoracic_rotasi_kiri   = models.FloatField(null=True, blank=True, verbose_name='Thoracic Rotation Kiri (derajat)')
    skor_thoracic_rotation = models.IntegerField(default=5, verbose_name='Skor Thoracic Rotation (1-10)')

    # -- 3. Hip Rotation Mobility (IR & ER) ----------------------------
    hip_ir_kanan      = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kanan (derajat)')
    hip_ir_kiri       = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kiri (derajat)')
    hip_er_kanan      = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kanan (derajat)')
    hip_er_kiri       = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kiri (derajat)')
    skor_hip_rotation = models.IntegerField(default=5, verbose_name='Skor Hip Rotation IR/ER (1-10)')

    # -- 4. ASLR (Active Straight Leg Raise) ---------------------------
    aslr_kanan = models.FloatField(null=True, blank=True, verbose_name='ASLR Kanan (derajat)')
    aslr_kiri  = models.FloatField(null=True, blank=True, verbose_name='ASLR Kiri (derajat)')
    skor_aslr  = models.IntegerField(default=5, verbose_name='Skor ASLR (1-10)')

    # -- 5. Lumbar Extension (Modified Cobra / Clearing Gate) ----------
    lumbar_nyeri           = models.BooleanField(default=False, verbose_name='Nyeri saat Ekstensi? (Clearing Gate Gagal)')
    lumbar_kualitas        = models.CharField(max_length=20, choices=LUMBAR_KUALITAS_CHOICES, default='MULUS', verbose_name='Kualitas Ekstensi Thoracolumbar')
    skor_lumbar_extension  = models.IntegerField(default=5, verbose_name='Skor Lumbar Extension (1-10)')

    # -- 6. Lateral Pelvic Stability (Single-Leg Squat) ----------------
    pelvic_stability_kanan = models.CharField(max_length=20, choices=PELVIC_STABILITY_CHOICES, default='STABIL', verbose_name='Pelvic Stability Kanan')
    pelvic_stability_kiri  = models.CharField(max_length=20, choices=PELVIC_STABILITY_CHOICES, default='STABIL', verbose_name='Pelvic Stability Kiri')
    skor_pelvic_stability  = models.IntegerField(default=5, verbose_name='Skor Lateral Pelvic Stability (1-10)')

    # -- AI --------------------------------------------------------
    ai_confidence_score = models.FloatField(null=True, blank=True)

    # -- Hasil --------------------------------------------------------
    total_skor         = models.FloatField(default=0, verbose_name='Total Skor L1 (0-10)')
    predikat           = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_naik         = models.BooleanField(default=False, verbose_name='Layak Naik ke L2?')
    alasan_tidak_layak = models.CharField(max_length=255, blank=True)

    # -- Metadata --------------------------------------------------
    catatan    = models.TextField(blank=True, null=True, verbose_name='Catatan Coach')
    timestamp  = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, blank=True, default='Coach Fanny')

    class Meta:
        ordering            = ['-timestamp']
        verbose_name        = 'L1 Correction Muay Thai'
        verbose_name_plural = 'L1 Correction Muay Thai'
        db_table            = 'muaythai_correction_audit_l1'

    def __str__(self):
        return f"{self.atlet_name or self.atlet.nama_atlet} | {self.predikat} | {self.total_skor}"

    @property
    def skor_list(self):
        return [
            self.skor_ankle_mobility, self.skor_thoracic_rotation,
            self.skor_hip_rotation, self.skor_aslr,
            self.skor_lumbar_extension, self.skor_pelvic_stability,
        ]

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet

        # Clearing gate SOP: nyeri saat Lumbar Extension -> Skor 0, gagal (rujuk medis)
        if self.lumbar_nyeri:
            self.skor_lumbar_extension = 0

        # Total skor: rata-rata 6 parameter, tiap parameter sudah 1-10 (bukan raw/24 lagi)
        raw_total = sum(self.skor_list)
        self.total_skor = round(raw_total / 6, 1)

        if self.lumbar_nyeri:
            # Clearing gate gagal -> otomatis tidak layak, terlepas dari total skor item lain
            self.predikat = 'NOVICE'
        elif self.total_skor >= 8.3:
            self.predikat = 'ELITE'
        elif self.total_skor >= 5.8:
            self.predikat = 'READY'
        elif self.total_skor >= 4.2:
            self.predikat = 'DEVELOPING'
        else:
            self.predikat = 'NOVICE'

        if self.predikat in ('ELITE', 'READY') and not self.lumbar_nyeri:
            self.layak_naik = True
            self.alasan_tidak_layak = ''
        else:
            self.layak_naik = False
            if self.lumbar_nyeri:
                self.alasan_tidak_layak = (
                    "Clearing Gate GAGAL: nyeri tajam saat Lumbar Extension Test. "
                    "Wajib evaluasi medis sebelum lanjut program apapun."
                )
            else:
                self.alasan_tidak_layak = (
                    f"Skor L1 {self.total_skor}/10 (raw {raw_total}/60). "
                    f"Item terlemah: {self.item_terlemah}. "
                    f"Wajib program korektif mobility/stability sebelum lanjut."
                )

        super().save(*args, **kwargs)

    @property
    def item_terlemah(self):
        labels = {
            'Ankle Mobility (WBLT)':      self.skor_ankle_mobility,
            'Seated Thoracic Rotation':   self.skor_thoracic_rotation,
            'Hip Rotation (IR/ER)':       self.skor_hip_rotation,
            'ASLR':                       self.skor_aslr,
            'Lumbar Extension':           self.skor_lumbar_extension,
            'Lateral Pelvic Stability':   self.skor_pelvic_stability,
        }
        return min(labels, key=labels.get)

    @property
    def predikat_label(self):
        if self.lumbar_nyeri:
            return 'Clearing Gate GAGAL -- Evaluasi medis diperlukan'
        skor = self.total_skor
        if skor >= 8.3:
            return 'Baik / Ideal -- Siap lanjut ke L2'
        elif skor >= 5.8:
            return 'Baik-Cukup -- Layak lanjut dengan catatan'
        elif skor >= 4.2:
            return 'Cukup -- Perlu pembinaan tambahan'
        else:
            return 'Kurang -- Belum layak lanjut, fokus koreksi dasar'

    @property
    def rekomendasi_auto(self):
        nama = self.item_terlemah
        if self.lumbar_nyeri:
            return "STOP semua program pembebanan. Rujuk evaluasi medis untuk nyeri Lumbar Extension sebelum asesmen dilanjutkan."
        if self.predikat == 'ELITE':
            return "Mobilitas & stabilitas sangat matang di semua parameter. Lanjut ke L2 Strength Assessment."
        elif self.predikat == 'READY':
            return f"Layak ke L2. Tetap latih '{nama}' 2-3x/minggu sebagai bagian pemanasan/pendinginan."
        elif self.predikat == 'DEVELOPING':
            return f"Tahan ke L2. Fokus 4-6 minggu perbaikan corrective exercise pada '{nama}'."
        return f"STOP lanjut ke teknik. Prioritas corrective exercise tinggi pada '{nama}'. Hindari beban tinggi pada pola gerak terkait sampai ada perbaikan."