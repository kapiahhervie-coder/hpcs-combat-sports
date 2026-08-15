"""
taekwondo/models.py — VERSI KOREKSI

PERUBAHAN dari versi sebelumnya:
1. Field skor_neural_* diubah dari IntegerField(choices=NEURAL_CHOICES 1-3)
   menjadi FloatField — sekarang diisi OTOMATIS oleh view (hasil kalkulasi
   dari data mentah + rubrik), BUKAN dari input manual coach.
2. total_skor sekarang = rata-rata 8 skor_neural_* (masing-masing sudah
   dalam skala 0-10 hasil rubrik) — TIDAK LAGI pakai rumus (raw/24)*10.
3. Threshold predikat (8.3/5.8/4.2) TETAP SAMA seperti sebelumnya, karena
   memang sudah tepat.

Field data mentah (hip_rotasi_*, balance_durasi_*, dll) TIDAK BERUBAH.
Field skor_neural_* TETAP ADA di model (dipakai untuk radar chart & histori)
tapi sekarang perannya sebagai HASIL KALKULASI, bukan input.

Timpa seluruh isi taekwondo/models.py dengan file ini.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from combat.models import Atlet, KATEGORI_USIA_CHOICES, GENDER_CHOICES, PREDIKAT_CHOICES


class CorrectionAuditL1TKD(models.Model):
    """
    L1 Correction — Taekwondo
    Fokus: Mobility, Stability, Fleksibilitas sebagai fondasi sebelum
    masuk ke teknik tendangan spesifik (dolyo chagi, ap chagi, dwi chagi,
    naeryo chagi, dolgae chagi). Dominan single-leg & rotational.

    Skor per item (skor_neural_*) DIHITUNG OTOMATIS oleh server dari data
    mentah hasil ukur (derajat/detik/cm) memakai rubrik per kategori usia
    — lihat RUBRIK_L1 & fungsi hitung_skor_l1_*() di taekwondo/views.py.
    Coach hanya input data mentah, bukan skor.
    """
    # -- Identitas --------------------------------------------------
    atlet         = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='audit_l1_tkd', verbose_name='Atlet')
    atlet_name    = models.CharField(max_length=150, blank=True, verbose_name='Nama Atlet (form)')
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True, verbose_name='Berat Badan (kg)')

    # -- 1. Hip Rotation ROM (roundhouse / hook kick) ------------------
    hip_rotasi_internal_kanan  = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kanan (derajat)')
    hip_rotasi_internal_kiri   = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kiri (derajat)')
    hip_rotasi_eksternal_kanan = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kanan (derajat)')
    hip_rotasi_eksternal_kiri  = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kiri (derajat)')
    skor_neural_hip_rotasi     = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- 2. Single-Leg Balance (kicking stance) -------------------------
    balance_durasi_mata_terbuka  = models.FloatField(null=True, blank=True, verbose_name='Balance Mata Terbuka (detik)')
    balance_durasi_mata_tertutup = models.FloatField(null=True, blank=True, verbose_name='Balance Mata Tertutup (detik)')
    skor_neural_balance          = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- 3. Ankle Dorsiflexion (chamber & pivot) -------------------------
    ankle_dorsifleksi_kanan_cm = models.FloatField(null=True, blank=True, verbose_name='Ankle Dorsiflexion Kanan (cm)')
    ankle_dorsifleksi_kiri_cm  = models.FloatField(null=True, blank=True, verbose_name='Ankle Dorsiflexion Kiri (cm)')
    skor_neural_ankle          = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- 4. Thoracic Spine Rotation (spinning / back kick) ----------------
    thoracic_rotasi_kanan = models.FloatField(null=True, blank=True, verbose_name='Thoracic Rotation Kanan (derajat)')
    thoracic_rotasi_kiri  = models.FloatField(null=True, blank=True, verbose_name='Thoracic Rotation Kiri (derajat)')
    skor_neural_thoracic  = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- 5. Hip Flexor / Hamstring Flexibility (kick height) ---------------
    asl_raise_kanan_derajat = models.FloatField(null=True, blank=True, verbose_name='Active Straight Leg Raise Kanan (derajat)')
    asl_raise_kiri_derajat  = models.FloatField(null=True, blank=True, verbose_name='Active Straight Leg Raise Kiri (derajat)')
    skor_neural_hamstring   = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- 6. Hip Hinge Pattern --------------------------------------------
    hip_hinge_pass        = models.BooleanField(default=False, verbose_name='Hip Hinge Pattern Benar?')
    skor_neural_hip_hinge = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- 7. Core Anti-Rotation Stability ----------------------------------
    core_hold_durasi_detik = models.FloatField(null=True, blank=True, verbose_name='Pallof Press Hold (detik)')
    skor_neural_core       = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- 8. Dynamic Balance Recovery (landing after kick) -------------------
    recovery_waktu_detik = models.FloatField(null=True, blank=True, verbose_name='Recovery Time (detik)')
    skor_neural_recovery = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- AI --------------------------------------------------------
    ai_confidence_score = models.FloatField(null=True, blank=True)

    # -- Hasil --------------------------------------------------------
    total_skor         = models.FloatField(default=0, verbose_name='Total Skor (0-10)')
    predikat           = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_naik         = models.BooleanField(default=False, verbose_name='Layak Naik ke L2?')
    alasan_tidak_layak = models.CharField(max_length=255, blank=True)

    # -- Metadata --------------------------------------------------
    catatan    = models.TextField(blank=True, null=True, verbose_name='Catatan Coach')
    timestamp  = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, blank=True, default='Coach Fanny')

    class Meta:
        ordering            = ['-timestamp']
        verbose_name        = 'L1 Correction Taekwondo'
        verbose_name_plural = 'L1 Correction Taekwondo'
        db_table            = 'taekwondo_correction_audit_l1'

    def __str__(self):
        return f"{self.atlet_name or self.atlet.nama_atlet} | {self.predikat} | {self.total_skor}"

    @property
    def skor_neural_list(self):
        return [
            self.skor_neural_hip_rotasi, self.skor_neural_balance,
            self.skor_neural_ankle, self.skor_neural_thoracic,
            self.skor_neural_hamstring, self.skor_neural_hip_hinge,
            self.skor_neural_core, self.skor_neural_recovery,
        ]

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet

        # NOTE: skor_neural_* SUDAH dihitung otomatis di view sebelum
        # instance ini dibuat (dari data mentah + rubrik), jadi di sini
        # tinggal dirata-rata. Masing-masing skor_neural_* sudah dalam
        # skala 0-10, jadi total_skor = rata-rata langsung (BUKAN dibagi
        # 24 lagi seperti versi lama).
        self.total_skor = round(sum(self.skor_neural_list) / 8, 1)

        if self.total_skor >= 8.3:
            self.predikat = 'ELITE'
        elif self.total_skor >= 5.8:
            self.predikat = 'READY'
        elif self.total_skor >= 4.2:
            self.predikat = 'DEVELOPING'
        else:
            self.predikat = 'NOVICE'

        if self.predikat in ('ELITE', 'READY'):
            self.layak_naik = True
            self.alasan_tidak_layak = ''
        else:
            self.layak_naik = False
            self.alasan_tidak_layak = (
                f"Skor {self.total_skor}/10. "
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
            'Hip Flexor/Hamstring Flexibility': self.skor_neural_hamstring,
            'Hip Hinge': self.skor_neural_hip_hinge,
            'Core Anti-Rotation': self.skor_neural_core,
            'Dynamic Balance Recovery': self.skor_neural_recovery,
        }
        return min(labels, key=labels.get)

    @property
    def predikat_neural_label(self):
        skor = self.total_skor
        if skor >= 8.3:
            return 'Autonomous — Siap lanjut ke L2'
        elif skor >= 5.8:
            return 'Associative-Autonomous — Layak lanjut dengan catatan'
        elif skor >= 4.2:
            return 'Associative — Perlu pembinaan tambahan'
        else:
            return 'Cognitive — Belum layak lanjut, fokus koreksi dasar'

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