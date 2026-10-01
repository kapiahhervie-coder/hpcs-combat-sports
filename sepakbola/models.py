from django.db import models
from combat.models import Atlet, ProfilPelatih

KATEGORI_USIA_CHOICES = [
    ('YOUTH', 'Youth (6-12)'),
    ('JUNIOR', 'Junior (13-17)'),
    ('SENIOR', 'Senior (18-35)'),
    ('ELITE', 'Elite'),
]

GENDER_CHOICES = [
    ('PUTRA', 'Putra'),
    ('PUTRI', 'Putri'),
]


class CorrectionAuditL1SB(models.Model):
    """L1 - Mobility & Movement Correction (Sepak Bola) — struktur mengikuti pola L1 Boxing"""
    atlet = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='l1_sepakbola')
    kategori_usia = models.CharField(max_length=10, choices=KATEGORI_USIA_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Pilar 1: Ankle Mobility (numerik bilateral)
    ankle_kiri_cm = models.FloatField(null=True, blank=True)
    ankle_kanan_cm = models.FloatField(null=True, blank=True)
    score_ankle = models.FloatField(null=True, blank=True)

    # Pilar 2: ASLR (numerik bilateral)
    aslr_kiri_derajat = models.FloatField(null=True, blank=True)
    aslr_kanan_derajat = models.FloatField(null=True, blank=True)
    score_aslr = models.FloatField(null=True, blank=True)

    # Pilar 3: Hip Rotation (numerik bilateral + penalti asimetri)
    hip_kiri_derajat = models.FloatField(null=True, blank=True)
    hip_kanan_derajat = models.FloatField(null=True, blank=True)
    score_hip = models.FloatField(null=True, blank=True)
    kena_penalti_asimetri = models.BooleanField(default=False)

    # Pilar 4: Trunk Rotation (kualitatif — dropdown observasi)
    skor_trunk = models.FloatField(null=True, blank=True)

    # Pilar 5: Postur - Plumb Line (kualitatif)
    skor_postur = models.FloatField(null=True, blank=True)

    # Pilar 6: Napas - Hi-Lo Test (kualitatif)
    skor_napas = models.FloatField(null=True, blank=True)

    total_skor = models.FloatField(default=0)
    predikat = models.CharField(max_length=15, blank=True)  # ELITE/READY/DEVELOPING/NOVICE
    rekomendasi = models.TextField(blank=True)
    pilar_terendah = models.CharField(max_length=50, blank=True)
    catatan_pelatih = models.TextField(blank=True)

    class Meta:
        db_table = 'sepakbola_correction_audit_l1'
        ordering = ['-timestamp']


class StrengthAuditL2SB(models.Model):
    """L2 - Strength (Sepak Bola) — struktur mengikuti pola L2 Boxing"""
    atlet = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='l2_sepakbola')
    kategori_usia = models.CharField(max_length=10, choices=KATEGORI_USIA_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    berat_badan_kg = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Pilar 1: Lower Body - Back Squat 5RM
    lower_5rm_kg = models.FloatField(null=True, blank=True)
    score_lower = models.FloatField(null=True, blank=True)

    # Pilar 2: Posterior Chain - Romanian Deadlift 5RM
    posterior_5rm_kg = models.FloatField(null=True, blank=True)
    score_posterior = models.FloatField(null=True, blank=True)

    # Pilar 3: Single-Leg Strength - Bulgarian Split Squat 5RM per kaki
    singleleg_kiri_kg = models.FloatField(null=True, blank=True)
    singleleg_kanan_kg = models.FloatField(null=True, blank=True)
    score_singleleg = models.FloatField(null=True, blank=True)
    kena_penalti_asimetri = models.BooleanField(default=False)

    # Pilar 4: Core - Weighted Plank
    core_durasi_detik = models.FloatField(null=True, blank=True)
    score_core = models.FloatField(null=True, blank=True)

    # Pilar 5: Isometric - Wall Sit Hold
    iso_durasi_detik = models.FloatField(null=True, blank=True)
    iso_tremor_onset_detik = models.FloatField(null=True, blank=True)
    score_isometric = models.FloatField(null=True, blank=True)

    total_skor = models.FloatField(default=0)
    predikat = models.CharField(max_length=15, blank=True)
    pilar_terendah = models.CharField(max_length=50, blank=True)
    catatan_pelatih = models.TextField(blank=True)

    class Meta:
        db_table = 'sepakbola_strength_audit_l2'
        ordering = ['-timestamp']


class PowerAuditL3SB(models.Model):
    """L3 - Power (Sepak Bola) — struktur mengikuti pola L3 Boxing"""
    atlet = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='l3_sepakbola')
    kategori_usia = models.CharField(max_length=10, choices=KATEGORI_USIA_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    jump_height_cm = models.FloatField(null=True, blank=True)
    score_jump = models.FloatField(null=True, blank=True)

    sprint_30m_detik = models.FloatField(null=True, blank=True)
    score_sprint = models.FloatField(null=True, blank=True)

    broad_jump_m = models.FloatField(null=True, blank=True)
    score_broad = models.FloatField(null=True, blank=True)

    rsi_jump_height_cm = models.FloatField(null=True, blank=True)
    rsi_contact_time_ms = models.FloatField(null=True, blank=True)
    rsi_value = models.FloatField(null=True, blank=True)
    score_rsi = models.FloatField(null=True, blank=True)

    agility_ttest_detik = models.FloatField(null=True, blank=True)
    score_agility = models.FloatField(null=True, blank=True)

    total_skor = models.FloatField(default=0)
    predikat = models.CharField(max_length=15, blank=True)
    pilar_terendah = models.CharField(max_length=50, blank=True)
    catatan_pelatih = models.TextField(blank=True)

    class Meta:
        db_table = 'sepakbola_power_audit_l3'
        ordering = ['-timestamp']


class SpeedAgilityAuditL4SB(models.Model):
    """L4 - Speed & Agility (Sepak Bola) — struktur mengikuti pola L4 Boxing"""
    atlet = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='l4_sepakbola')
    kategori_usia = models.CharField(max_length=10, choices=KATEGORI_USIA_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    kondisi_uji = models.CharField(max_length=20, default='FRESH')
    timestamp = models.DateTimeField(auto_now_add=True)

    hex_waktu_putaran1 = models.FloatField(null=True, blank=True)
    hex_waktu_putaran2 = models.FloatField(null=True, blank=True)
    hex_waktu_putaran3 = models.FloatField(null=True, blank=True)
    hex_avg = models.FloatField(null=True, blank=True)
    score_hex = models.FloatField(null=True, blank=True)

    ladder_touch_10s = models.IntegerField(null=True, blank=True)
    ladder_postur_ok = models.BooleanField(default=True)
    score_ladder = models.FloatField(null=True, blank=True)

    yoyo_level_tercapai = models.IntegerField(null=True, blank=True)
    yoyo_shuttle_tercapai = models.IntegerField(null=True, blank=True)
    yoyo_total_jarak_m = models.FloatField(null=True, blank=True)
    vo2max_estimasi = models.FloatField(null=True, blank=True)
    score_yoyo = models.FloatField(null=True, blank=True)

    total_skor = models.FloatField(default=0)
    predikat = models.CharField(max_length=15, blank=True)
    pilar_terendah = models.CharField(max_length=50, blank=True)
    catatan_pelatih = models.TextField(blank=True)

    class Meta:
        db_table = 'sepakbola_speedagility_audit_l4'
        ordering = ['-timestamp']



