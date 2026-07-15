"""
muaythai/models.py
Model audit khusus Muay Thai. Model Atlet & lintas-cabang lain tetap
dipakai bersama dari app 'combat'.
"""
from django.db import models
from django.utils import timezone
from combat.models import Atlet, KATEGORI_USIA_CHOICES, GENDER_CHOICES, PREDIKAT_CHOICES


NEURAL_CHOICES = [
    (1, 'Cognitive'),
    (2, 'Associative'),
    (3, 'Autonomous'),
]


class CorrectionAuditL1MT(models.Model):
    """
    L1 Correction -- Muay Thai
    Fokus: Mobility, Stability, Fleksibilitas sebagai fondasi sebelum
    masuk ke teknik spesifik (pukulan, tendangan, siku, lutut, clinch).
    Setiap item punya skor kuantitatif (Q) + skor kualitas neural (N),
    mengikuti Motor Automaticity Scale (1=Cognitive, 2=Associative, 3=Autonomous).
    """
    # -- Identitas --------------------------------------------------
    atlet         = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='audit_l1_mt', verbose_name='Atlet')
    atlet_name    = models.CharField(max_length=150, blank=True, verbose_name='Nama Atlet (form)')
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True, verbose_name='Berat Badan (kg)')

    # -- 1. Hip Rotation ROM ------------------------------------------
    hip_rotasi_internal_kanan  = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kanan (derajat)')
    hip_rotasi_internal_kiri   = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kiri (derajat)')
    hip_rotasi_eksternal_kanan = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kanan (derajat)')
    hip_rotasi_eksternal_kiri  = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kiri (derajat)')
    skor_neural_hip_rotasi     = models.IntegerField(choices=NEURAL_CHOICES, default=1)

    # -- 2. Single-Leg Balance -----------------------------------------
    balance_durasi_mata_terbuka  = models.FloatField(null=True, blank=True, verbose_name='Balance Mata Terbuka (detik)')
    balance_durasi_mata_tertutup = models.FloatField(null=True, blank=True, verbose_name='Balance Mata Tertutup (detik)')
    skor_neural_balance          = models.IntegerField(choices=NEURAL_CHOICES, default=1)

    # -- 3. Ankle Dorsiflexion -------------------------------------------
    ankle_dorsifleksi_kanan_cm = models.FloatField(null=True, blank=True, verbose_name='Ankle Dorsiflexion Kanan (cm)')
    ankle_dorsifleksi_kiri_cm  = models.FloatField(null=True, blank=True, verbose_name='Ankle Dorsiflexion Kiri (cm)')
    skor_neural_ankle          = models.IntegerField(choices=NEURAL_CHOICES, default=1)

    # -- 4. Thoracic Spine Rotation ----------------------------------
    thoracic_rotasi_kanan = models.FloatField(null=True, blank=True, verbose_name='Thoracic Rotation Kanan (derajat)')
    thoracic_rotasi_kiri  = models.FloatField(null=True, blank=True, verbose_name='Thoracic Rotation Kiri (derajat)')
    skor_neural_thoracic  = models.IntegerField(choices=NEURAL_CHOICES, default=1)

    # -- 5. Shoulder Overhead Mobility --------------------------------
    shoulder_fleksi_kanan = models.FloatField(null=True, blank=True, verbose_name='Shoulder Flexion Kanan (derajat)')
    shoulder_fleksi_kiri  = models.FloatField(null=True, blank=True, verbose_name='Shoulder Flexion Kiri (derajat)')
    skor_neural_shoulder  = models.IntegerField(choices=NEURAL_CHOICES, default=1)

    # -- 6. Hip Hinge Pattern -----------------------------------------
    hip_hinge_pass       = models.BooleanField(default=False, verbose_name='Hip Hinge Pattern Benar?')
    skor_neural_hip_hinge = models.IntegerField(choices=NEURAL_CHOICES, default=1)

    # -- 7. Core Anti-Rotation Stability -------------------------------
    core_hold_durasi_detik = models.FloatField(null=True, blank=True, verbose_name='Pallof Press Hold (detik)')
    skor_neural_core       = models.IntegerField(choices=NEURAL_CHOICES, default=1)

    # -- 8. Dynamic Balance Recovery -----------------------------------
    recovery_waktu_detik  = models.FloatField(null=True, blank=True, verbose_name='Recovery Time (detik)')
    skor_neural_recovery  = models.IntegerField(choices=NEURAL_CHOICES, default=1)

    # -- AI --------------------------------------------------------
    ai_confidence_score = models.FloatField(null=True, blank=True)

    # -- Hasil --------------------------------------------------------
    total_skor         = models.FloatField(default=0, verbose_name='Total Skor Neural (0-10)')
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
    def skor_neural_list(self):
        return [
            self.skor_neural_hip_rotasi, self.skor_neural_balance,
            self.skor_neural_ankle, self.skor_neural_thoracic,
            self.skor_neural_shoulder, self.skor_neural_hip_hinge,
            self.skor_neural_core, self.skor_neural_recovery,
        ]

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet

        # Total skor neural mentah: 8 item x skor 1-3 -> max 24
        raw_total = sum(self.skor_neural_list)
        # Normalisasi ke skala 0-10 supaya konsisten dengan predikat lintas app
        self.total_skor = round((raw_total / 24) * 10, 1)

        if self.total_skor >= 8.3:       # setara skor neural rata-rata mendekati 3 (Autonomous)
            self.predikat = 'ELITE'
        elif self.total_skor >= 5.8:     # rata-rata mendekati 2-3 (Associative-Autonomous)
            self.predikat = 'READY'
        elif self.total_skor >= 4.2:     # rata-rata mendekati 2 (Associative)
            self.predikat = 'DEVELOPING'
        else:
            self.predikat = 'NOVICE'

        if self.predikat in ('ELITE', 'READY'):
            self.layak_naik = True
            self.alasan_tidak_layak = ''
        else:
            self.layak_naik = False
            self.alasan_tidak_layak = (
                f"Skor neural {self.total_skor}/10 (raw {raw_total}/24). "
                f"Item terlemah: {self.item_terlemah}. "
                f"Wajib program korektif mobility/stability sebelum lanjut."
            )

        super().save(*args, **kwargs)

    @property
    def item_terlemah(self):
        labels = {
            'Hip Rotation': self.skor_neural_hip_rotasi,
            'Single-Leg Balance': self.skor_neural_balance,
            'Ankle Dorsiflexion': self.skor_neural_ankle,
            'Thoracic Rotation': self.skor_neural_thoracic,
            'Shoulder Mobility': self.skor_neural_shoulder,
            'Hip Hinge': self.skor_neural_hip_hinge,
            'Core Anti-Rotation': self.skor_neural_core,
            'Dynamic Balance Recovery': self.skor_neural_recovery,
        }
        return min(labels, key=labels.get)

    @property
    def predikat_neural_label(self):
        skor = self.total_skor
        if skor >= 8.3:
            return 'Autonomous -- Siap lanjut ke L2'
        elif skor >= 5.8:
            return 'Associative-Autonomous -- Layak lanjut dengan catatan'
        elif skor >= 4.2:
            return 'Associative -- Perlu pembinaan tambahan'
        else:
            return 'Cognitive -- Belum layak lanjut, fokus koreksi dasar'

    @property
    def rekomendasi_auto(self):
        nama = self.item_terlemah
        if self.predikat == 'ELITE':
            return "Kontrol neuromuskular sangat matang di semua item. Lanjut ke L2 Strength Assessment."
        elif self.predikat == 'READY':
            return f"Layak ke L2. Tetap latih '{nama}' 2-3x/minggu untuk konsolidasi otomatisasi."
        elif self.predikat == 'DEVELOPING':
            return f"Tahan ke L2. Fokus 4-6 minggu perbaikan mobility/stability pada '{nama}'."
        return f"STOP lanjut ke teknik. Kontrol neuromuskular kritis pada '{nama}'. Wajib program korektif 8 minggu."
