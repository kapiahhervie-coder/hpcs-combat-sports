"""
karate/models.py
Model audit khusus Karate. Model Atlet & lintas-cabang lain tetap
dipakai bersama dari app 'combat'.

REVISI 1 (SOP Rubrik Asesmen HPCS Level 1 - Karate):
L1 Correction diganti dari skema 8-pilar (skor manual 1-3, Motor
Automaticity Scale) menjadi skema 6-pilar sesuai SOP resmi, dengan skor
0-10 dihitung OTOMATIS di server dari data pengukuran mentah -- pola yang
sama seperti combat.CorrectionAuditL1 (Boxing).

6 Pilar SOP Karate:
  1. Ankle Mobility (WBLT)             -> cm
  2. Seated Thoracic Rotation          -> derajat
  3. Hip Rotation Mobility             -> derajat (internal+eksternal per sisi)
  4. ASLR / Fleksibilitas Tungkai      -> derajat
  5. Lumbar Extension                  -> kualitatif (observasi, clearing gate nyeri)
  6. Lateral Pelvic Stability          -> kualitatif (observasi knee valgus)

Field-field pilar LAMA yang di-drop dari SOP baru (Balance, Hip Hinge,
Core Anti-Rotation, Dynamic Balance Recovery) SENGAJA TIDAK DIHAPUS dari
model -- supaya histori audit lama yang sudah tersimpan di database tetap
aman & bisa diakses, meskipun form & kalkulasi baru tidak memakainya lagi.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from combat.models import Atlet, KATEGORI_USIA_CHOICES, GENDER_CHOICES, PREDIKAT_CHOICES


NEURAL_CHOICES = [
    (1, 'Cognitive'),
    (2, 'Associative'),
    (3, 'Autonomous'),
]


class CorrectionAuditL1KRT(models.Model):
    """
    L1 Correction -- Karate (SOP Revisi 1)
    Fokus: mobilitas ankle & panggul untuk kedalaman kuda-kuda (Zenkutsu,
    Kokutsu, Kiba Dachi), fleksibilitas thorakal & rotasi panggul untuk
    pelepasan tenaga (Koshino Kaiten) saat Gyaku Zuki/Mawashi Geri, serta
    stabilitas postur bawah-atas untuk mencegah cedera spesifik Karate
    (patellofemoral pain, hip impingement, ankle sprain).
    """
    # -- Identitas --------------------------------------------------
    atlet         = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='audit_l1_krt', verbose_name='Atlet')
    atlet_name    = models.CharField(max_length=150, blank=True, verbose_name='Nama Atlet (form)')
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True, verbose_name='Berat Badan (kg)')

    # ══════════════════════════════════════════════════════════════
    # 6 PILAR SOP REVISI 1 -- data mentah + skor 0-10 (dihitung server)
    # ══════════════════════════════════════════════════════════════

    # -- 1. Ankle Mobility (Weight-Bearing Lunge Test) -------------------
    ankle_dorsifleksi_kanan_cm = models.FloatField(null=True, blank=True, verbose_name='Ankle Dorsiflexion Kanan (cm)')
    ankle_dorsifleksi_kiri_cm  = models.FloatField(null=True, blank=True, verbose_name='Ankle Dorsiflexion Kiri (cm)')
    score_ankle = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Ankle Mobility')

    # -- 2. Seated Thoracic Rotation -------------------------------------
    thoracic_rotasi_kanan = models.FloatField(null=True, blank=True, verbose_name='Thoracic Rotation Kanan (derajat)')
    thoracic_rotasi_kiri  = models.FloatField(null=True, blank=True, verbose_name='Thoracic Rotation Kiri (derajat)')
    score_thoracic_rotation = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Thoracic Rotation')

    # -- 3. Hip Rotation Mobility (internal + eksternal per sisi) --------
    hip_rotasi_internal_kanan  = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kanan (derajat)')
    hip_rotasi_internal_kiri   = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kiri (derajat)')
    hip_rotasi_eksternal_kanan = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kanan (derajat)')
    hip_rotasi_eksternal_kiri  = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kiri (derajat)')
    score_hip_rotation = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Hip Rotation Mobility')

    # -- 4. ASLR / Fleksibilitas Tungkai (Hamstring & Hip Flexor) --------
    asl_raise_kanan_derajat = models.FloatField(null=True, blank=True, verbose_name='Active Straight Leg Raise Kanan (derajat)')
    asl_raise_kiri_derajat  = models.FloatField(null=True, blank=True, verbose_name='Active Straight Leg Raise Kiri (derajat)')
    score_aslr = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor ASLR')

    # -- 5. Lumbar Extension (Modified Cobra / Clearing Gate) ------------
    # Kualitatif -- pelatih memilih kondisi hasil observasi langsung
    # (Baik=9 / Cukup=6 / Kurang=3 / Nyeri=0 clearing gate), server hanya
    # validasi & clamp skornya, sama pola dengan Boxing.
    score_lumbar_extension = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Lumbar Extension')

    # -- 6. Lateral Pelvic Stability (Single-Leg Squat Assessment) -------
    # Kualitatif -- observasi knee valgus / Trendelenburg sign.
    score_lateral_pelvic = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Lateral Pelvic Stability')

    # ══════════════════════════════════════════════════════════════
    # PILAR LAMA (SKEMA 8-PILAR, DEPRECATED) -- dipertahankan hanya
    # untuk histori data lama, TIDAK dipakai form/kalkulasi baru.
    # ══════════════════════════════════════════════════════════════
    balance_durasi_mata_terbuka  = models.FloatField(null=True, blank=True, verbose_name='[Lama] Balance Mata Terbuka (detik)')
    balance_durasi_mata_tertutup = models.FloatField(null=True, blank=True, verbose_name='[Lama] Balance Mata Tertutup (detik)')
    skor_neural_balance          = models.IntegerField(choices=NEURAL_CHOICES, default=1, verbose_name='[Lama] Skor Neural Balance')

    hip_hinge_pass        = models.BooleanField(default=False, verbose_name='[Lama] Hip Hinge Pattern Benar?')
    skor_neural_hip_hinge = models.IntegerField(choices=NEURAL_CHOICES, default=1, verbose_name='[Lama] Skor Neural Hip Hinge')

    core_hold_durasi_detik = models.FloatField(null=True, blank=True, verbose_name='[Lama] Pallof Press Hold (detik)')
    skor_neural_core       = models.IntegerField(choices=NEURAL_CHOICES, default=1, verbose_name='[Lama] Skor Neural Core')

    recovery_waktu_detik = models.FloatField(null=True, blank=True, verbose_name='[Lama] Recovery Time (detik)')
    skor_neural_recovery = models.IntegerField(choices=NEURAL_CHOICES, default=1, verbose_name='[Lama] Skor Neural Recovery')

    # skor_neural_hip_rotasi/ankle/thoracic/hamstring versi LAMA (skala
    # 1-3) juga dipertahankan apa adanya untuk histori, terpisah dari
    # score_hip_rotation/score_ankle/dst (skala 0-10) versi baru di atas.
    skor_neural_hip_rotasi = models.IntegerField(choices=NEURAL_CHOICES, default=1, verbose_name='[Lama] Skor Neural Hip Rotasi (skala 1-3)')
    skor_neural_ankle      = models.IntegerField(choices=NEURAL_CHOICES, default=1, verbose_name='[Lama] Skor Neural Ankle (skala 1-3)')
    skor_neural_thoracic   = models.IntegerField(choices=NEURAL_CHOICES, default=1, verbose_name='[Lama] Skor Neural Thoracic (skala 1-3)')
    skor_neural_hamstring  = models.IntegerField(choices=NEURAL_CHOICES, default=1, verbose_name='[Lama] Skor Neural Hamstring (skala 1-3)')

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
        verbose_name        = 'L1 Correction Karate'
        verbose_name_plural = 'L1 Correction Karate'
        db_table            = 'karate_correction_audit_l1'

    def __str__(self):
        return f"{self.atlet_name or self.atlet.nama_atlet} | {self.predikat} | {self.total_skor}"

    # -- (Dipertahankan untuk histori skema lama, tidak dipakai lagi) ----
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

        # Total skor SOP Revisi 1: rata-rata 6 pilar (skala 0-10 langsung,
        # BUKAN skala 1-3/24 seperti skema lama).
        self.total_skor = round(sum([
            self.score_ankle, self.score_thoracic_rotation,
            self.score_hip_rotation, self.score_aslr,
            self.score_lumbar_extension, self.score_lateral_pelvic,
        ]) / 6, 1)

        # Ambang predikat disamakan dengan standar HPCS lintas cabang
        # (combat.CorrectionAuditL1 / Boxing) untuk konsistensi platform.
        if self.total_skor >= 9.0:
            self.predikat = 'ELITE'
        elif self.total_skor >= 7.0:
            self.predikat = 'READY'
        elif self.total_skor >= 5.0:
            self.predikat = 'DEVELOPING'
        else:
            self.predikat = 'NOVICE'

        if self.total_skor >= 7.0:
            self.layak_naik        = True
            self.alasan_tidak_layak = ''
        else:
            self.layak_naik        = False
            self.alasan_tidak_layak = (
                f"Skor {self.total_skor}/10 < 7.0. "
                f"Pilar terlemah: {self.item_terlemah}. "
                f"Wajib program korektif mobility/stability sebelum lanjut ke L2."
            )

        super().save(*args, **kwargs)

    @property
    def item_terlemah(self):
        pilar = {
            'Ankle Mobility': self.score_ankle,
            'Seated Thoracic Rotation': self.score_thoracic_rotation,
            'Hip Rotation Mobility': self.score_hip_rotation,
            'ASLR / Fleksibilitas Tungkai': self.score_aslr,
            'Lumbar Extension': self.score_lumbar_extension,
            'Lateral Pelvic Stability': self.score_lateral_pelvic,
        }
        return min(pilar, key=pilar.get)

    @property
    def predikat_neural_label(self):
        skor = self.total_skor
        if skor >= 9.0:
            return 'Excellent -- Siap lanjut ke L2'
        elif skor >= 7.0:
            return 'Ready -- Layak lanjut ke L2'
        elif skor >= 5.0:
            return 'Developing -- Perlu pembinaan tambahan'
        else:
            return 'Novice -- Belum layak lanjut, fokus koreksi dasar'

    @property
    def rekomendasi_auto(self):
        nama = self.item_terlemah
        if self.predikat == 'ELITE':
            return "Mobilitas & stabilitas sangat matang di semua pilar. Lanjut ke L2 Strength Assessment."
        elif self.predikat == 'READY':
            return f"Layak ke L2. Tetap latih '{nama}' 2-3x/minggu untuk konsolidasi."
        elif self.predikat == 'DEVELOPING':
            return f"Tahan ke L2. Fokus 4-6 minggu perbaikan '{nama}'."
        return f"STOP lanjut ke teknik. Skor kritis pada '{nama}'. Wajib program korektif 8 minggu."