"""
HPCS Combat Sports — Models
High Performance Coaching System
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


# ══════════════════════════════════════════════════════════════════════
# CHOICES
# ══════════════════════════════════════════════════════════════════════

GENDER_CHOICES = [
    ('Putra', 'Putra'),
    ('Putri', 'Putri'),
]

KATEGORI_USIA_CHOICES = [
    ('ELITE',  'Elite'),
    ('YOUTH',  'Youth'),
    ('JUNIOR', 'Junior'),
    ('SENIOR', 'Senior'),
]

PREDIKAT_CHOICES = [
    ('ELITE',      'Elite'),
    ('READY',      'Ready'),
    ('DEVELOPING', 'Developing'),
    ('NOVICE',     'Novice'),
]

CABANG_CHOICES = [
    ('boxing',  'Boxing'),
    ('muaythai', 'Muay Thai'),
    ('tkd',     'Taekwondo'),
    ('krt',     'Karate'),
]

LTAD_CHOICES = [
    ('fundamental',   'FUNdamental (6-9 thn)'),
    ('learn_train',   'Learn to Train (9-12 thn)'),
    ('train_train',   'Train to Train (12-16 thn)'),
    ('train_compete', 'Train to Compete (16-19 thn)'),
    ('train_win',     'Train to Win (19+ thn)'),
    ('active_life',   'Active for Life'),
]


# ══════════════════════════════════════════════════════════════════════
# HELPER
# ══════════════════════════════════════════════════════════════════════

def _hitung_predikat(total_skor: float) -> str:
    if total_skor >= 9.0:
        return 'ELITE'
    elif total_skor >= 7.0:
        return 'READY'
    elif total_skor >= 5.0:
        return 'DEVELOPING'
    return 'NOVICE'


def _avg(*scores) -> float:
    valid = [s for s in scores if s is not None]
    if not valid:
        return 0.0
    return round(sum(valid) / len(valid), 1)


# ══════════════════════════════════════════════════════════════════════
# PROFIL PELATIH
# ══════════════════════════════════════════════════════════════════════

class ProfilPelatih(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Menunggu Persetujuan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]
    user        = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profil_pelatih'
    )
    cabang      = models.CharField(max_length=20, choices=CABANG_CHOICES, blank=True)
    no_hp       = models.CharField(max_length=20, blank=True)
    email       = models.EmailField(blank=True, verbose_name='Email')
    foto        = models.ImageField(upload_to='foto_pelatih/', blank=True, null=True, verbose_name='Foto Profil')
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    bio         = models.TextField(blank=True, verbose_name='Bio Singkat')
    sertifikasi = models.TextField(blank=True, verbose_name='Sertifikasi & Lisensi',
                                    help_text='Satu baris per sertifikasi')

    class Meta:
        verbose_name        = 'Profil Pelatih'
        verbose_name_plural = 'Profil Pelatih'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} — {self.get_status_display()}'

    @property
    def is_approved(self):
        return self.status == 'approved'


# ══════════════════════════════════════════════════════════════════════
# MODEL ATLET
# ══════════════════════════════════════════════════════════════════════

class Atlet(models.Model):
    # ── Identitas ────────────────────────────────────────────────────
    nama_atlet    = models.CharField(max_length=100, verbose_name='Nama Atlet')
    kategori_umur = models.CharField(
        max_length=10, choices=KATEGORI_USIA_CHOICES,
        verbose_name='Kategori Usia'
    )
    gender        = models.CharField(
        max_length=10, choices=GENDER_CHOICES,
        verbose_name='Gender'
    )
    kelas_berat   = models.FloatField(
        verbose_name='Berat Badan (kg)',
        help_text='Berat dalam Kg'
    )
    tanggal_lahir = models.DateField(null=True, blank=True, verbose_name='Tanggal Lahir')

    # ── Data Fisik ───────────────────────────────────────────────────
    tinggi_badan  = models.FloatField(null=True, blank=True, verbose_name='Tinggi Badan (cm)')

    # ── Data Olahraga ────────────────────────────────────────────────
    cabang        = models.CharField(
        max_length=20, choices=CABANG_CHOICES,
        blank=True, verbose_name='Cabang Olahraga'
    )
    tahap_ltad    = models.CharField(
        max_length=20, choices=LTAD_CHOICES,
        blank=True, verbose_name='Tahap LTAD'
    )
    pelatih       = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='atlet_binaan',
        verbose_name='Pelatih'
    )

    # ── Timestamp ────────────────────────────────────────────────────
    dibuat_pada   = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Atlet'
        verbose_name_plural = 'Atlet'
        ordering            = ['nama_atlet']

    def __str__(self):
        return f'{self.nama_atlet} ({self.get_kategori_umur_display()})'

    @property
    def bmi(self):
        if self.tinggi_badan and self.kelas_berat and self.tinggi_badan > 0:
            tinggi_m = self.tinggi_badan / 100
            return round(self.kelas_berat / (tinggi_m ** 2), 1)
        return None

    @property
    def umur(self):
        if self.tanggal_lahir:
            hari_ini = timezone.now().date()
            delta = hari_ini - self.tanggal_lahir
            return delta.days // 365
        return None

    @property
    def level_saat_ini(self):
        if self.audit_l3.filter(layak_naik=True).exists():
            return 'L3 — Siap Kompetisi'
        if self.audit_l2.filter(layak_naik=True).exists():
            return 'L2 — Menuju Power'
        if self.audit_l1.filter(layak_naik=True).exists():
            return 'L1 — Menuju Strength'
        return 'Belum Audit'

    @property
    def risiko_cedera(self):
        audit = self.audit_l1.order_by('-timestamp').first()
        if not audit:
            return 'Data Belum Ada'
        if audit.total_skor < 5.0:
            return 'TINGGI'
        elif audit.total_skor < 7.0:
            return 'SEDANG'
        return 'RENDAH'


# ══════════════════════════════════════════════════════════════════════
# AUDIT L1 — CORRECTION
# ══════════════════════════════════════════════════════════════════════

class CorrectionAuditL1(models.Model):
    # ── Identitas ────────────────────────────────────────────────────
    atlet         = models.ForeignKey(
        Atlet, on_delete=models.CASCADE,
        related_name='audit_l1', verbose_name='Atlet'
    )
    atlet_name    = models.CharField(max_length=150, blank=True, verbose_name='Nama Atlet (form)')
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True, verbose_name='Berat Badan (kg)')

    # ── Skor 5 Pilar ─────────────────────────────────────────────────
    score_rotation  = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Rotasi')
    score_extension = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Ekstensi')
    score_stability = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Stabilitas')
    score_posture   = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Postur')
    score_breathing = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='Skor Pernafasan')

    # ── AI ────────────────────────────────────────────────────────────
    ai_confidence_score = models.FloatField(null=True, blank=True, verbose_name='AI Confidence (%)')

    # ── Hasil ────────────────────────────────────────────────────────
    total_skor         = models.FloatField(default=0, verbose_name='Total Skor')
    predikat           = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_naik         = models.BooleanField(default=False, verbose_name='Layak Naik ke L2?')
    alasan_tidak_layak = models.CharField(max_length=255, blank=True)

    # ── Metadata ─────────────────────────────────────────────────────
    catatan    = models.TextField(blank=True, null=True, verbose_name='Catatan Coach')
    timestamp  = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, blank=True, default='Coach Fanny')

    class Meta:
        ordering            = ['-timestamp']
        verbose_name        = 'L1 - Correction'
        verbose_name_plural = 'L1 - Correction'
        db_table            = 'hpcs_correction_audit_l1'

    def __str__(self):
        return f"{self.atlet_name or self.atlet.nama_atlet} | {self.predikat} | {self.total_skor}"

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet
        self.total_skor = _avg(
            self.score_rotation, self.score_extension,
            self.score_stability, self.score_posture, self.score_breathing,
        )
        self.predikat = _hitung_predikat(self.total_skor)
        if self.total_skor >= 7.0:
            self.layak_naik        = True
            self.alasan_tidak_layak = ''
        else:
            self.layak_naik        = False
            self.alasan_tidak_layak = (
                f"Skor {self.total_skor} < 7.0. "
                f"Pilar terendah: {self.pilar_terendah}. "
                f"Wajib program korektif sebelum loading."
            )
        super().save(*args, **kwargs)

    @property
    def pilar_terendah(self):
        pilar = {
            'Rotasi': self.score_rotation, 'Ekstensi': self.score_extension,
            'Stabilitas': self.score_stability, 'Postur': self.score_posture,
            'Pernafasan': self.score_breathing,
        }
        return min(pilar, key=pilar.get)

    @property
    def rekomendasi_auto(self):
        nama_pilar = self.pilar_terendah
        if self.predikat == 'ELITE':
            return "Mobilitas sempurna. Lanjut ke L2 Strength Assessment."
        elif self.predikat == 'READY':
            return f"Layak ke L2. Perkuat pilar '{nama_pilar}' 2-3x/minggu."
        elif self.predikat == 'DEVELOPING':
            return f"TAHAN ke L2. Fokus 4-6 minggu perbaikan '{nama_pilar}'."
        return f"STOP loading. Skor kritis pada '{nama_pilar}'. Wajib program korektif 8 minggu."


# ══════════════════════════════════════════════════════════════════════
# AUDIT L2 — STRENGTH
# ══════════════════════════════════════════════════════════════════════

class StrengthAuditL2(models.Model):
    # ── Identitas ────────────────────────────────────────────────────
    atlet         = models.ForeignKey(
        Atlet, on_delete=models.CASCADE,
        related_name='audit_l2', null=True, blank=True, verbose_name='Atlet'
    )
    atlet_name    = models.CharField(max_length=150, verbose_name='Nama Atlet')
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='Elite')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True, verbose_name='Berat Badan (kg)')

    # ── Pilar 1: Lower Strength ───────────────────────────────────────
    lower_5rm_beban    = models.FloatField(null=True, blank=True, verbose_name='Lower 5RM Beban (kg)')
    lower_5rm_bw_ratio = models.FloatField(null=True, blank=True, verbose_name='5RM / BW Ratio')
    score_lower        = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Pilar 2: Upper Push ───────────────────────────────────────────
    push_5rm_beban = models.FloatField(null=True, blank=True, verbose_name='Push 5RM Beban (kg)')
    score_push     = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Pilar 3: Upper Pull ───────────────────────────────────────────
    pull_reps  = models.IntegerField(null=True, blank=True, verbose_name='Pull-Up Repetisi')
    score_pull = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Pilar 4: Core Bracing ─────────────────────────────────────────
    core_durasi_detik = models.IntegerField(null=True, blank=True, verbose_name='Weighted Plank Durasi (detik)')
    score_core        = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Pilar 5: Isometric + CNS ──────────────────────────────────────
    iso_durasi_detik       = models.IntegerField(null=True, blank=True, verbose_name='Split Squat Hold (detik)')
    iso_tremor_onset_detik = models.IntegerField(null=True, blank=True, verbose_name='Onset Tremor (detik)')
    iso_tremor_rasio       = models.FloatField(null=True, blank=True, verbose_name='Tremor Onset Ratio (%)')
    score_isometric        = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── AI ────────────────────────────────────────────────────────────
    ai_rep_count_lower  = models.IntegerField(null=True, blank=True)
    ai_rep_count_push   = models.IntegerField(null=True, blank=True)
    ai_rep_count_pull   = models.IntegerField(null=True, blank=True)
    ai_confidence_score = models.FloatField(null=True, blank=True)

    # ── Hasil ────────────────────────────────────────────────────────
    total_skor         = models.FloatField(default=0)
    predikat           = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_naik         = models.BooleanField(default=False, verbose_name='Layak Naik ke L3?')
    alasan_tidak_layak = models.CharField(max_length=255, blank=True)

    # ── Metadata ─────────────────────────────────────────────────────
    catatan    = models.TextField(blank=True, null=True)
    timestamp  = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, blank=True, default='Coach Fanny')

    class Meta:
        ordering            = ['-timestamp']
        verbose_name        = 'L2 - Strength'
        verbose_name_plural = 'L2 - Strength'
        db_table            = 'hpcs_strength_audit_l2'

    def __str__(self):
        return f"{self.atlet_name} | {self.predikat} | {self.total_skor}"

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet
        if self.lower_5rm_beban and self.kelas_berat and self.kelas_berat > 0:
            self.lower_5rm_bw_ratio = round(self.lower_5rm_beban / self.kelas_berat, 2)
        if self.iso_tremor_onset_detik and self.iso_durasi_detik and self.iso_durasi_detik > 0:
            self.iso_tremor_rasio = round((self.iso_tremor_onset_detik / self.iso_durasi_detik) * 100, 1)
        self.total_skor = _avg(self.score_lower, self.score_push, self.score_pull, self.score_core, self.score_isometric)
        self.predikat   = _hitung_predikat(self.total_skor)
        skor_cukup   = self.total_skor >= 7.0
        tremor_cukup = self.iso_tremor_rasio is not None and self.iso_tremor_rasio >= 65.0
        if skor_cukup and tremor_cukup:
            self.layak_naik        = True
            self.alasan_tidak_layak = ''
        else:
            self.layak_naik = False
            alasan = []
            if not skor_cukup:
                alasan.append(f"Skor {self.total_skor} < 7.0")
            if not tremor_cukup:
                alasan.append(f"CNS Tremor Ratio {self.iso_tremor_rasio or 0:.1f}% < 65%")
            self.alasan_tidak_layak = ' | '.join(alasan)
        super().save(*args, **kwargs)

    @property
    def cns_status(self):
        if self.iso_tremor_rasio is None:
            return 'Data tidak tersedia'
        if self.iso_tremor_rasio >= 85:
            return 'CNS Segar'
        elif self.iso_tremor_rasio >= 65:
            return 'CNS Cukup'
        return 'CNS Lelah — Risiko Cedera'

    @property
    def pilar_terendah(self):
        pilar = {
            'Lower': self.score_lower, 'Push': self.score_push,
            'Pull': self.score_pull, 'Core': self.score_core,
            'Isometric': self.score_isometric,
        }
        return min(pilar, key=pilar.get)

    @property
    def rekomendasi_auto(self):
        if self.predikat == 'ELITE':
            return "Kapasitas kekuatan elit. Lanjut L3 Power Assessment."
        elif self.predikat == 'READY':
            if not self.layak_naik:
                return f"Skor cukup tapi {self.cns_status}. Istirahat CNS 48-72 jam."
            return f"Layak ke L3. Fokus perkuat '{self.pilar_terendah}': progressive overload 3x/minggu."
        elif self.predikat == 'DEVELOPING':
            return f"Tahan ke L3. Prioritaskan '{self.pilar_terendah}': compound movement 3x/minggu."
        return f"STOP loading berat. Kekuatan dasar '{self.pilar_terendah}' kritis."


# ══════════════════════════════════════════════════════════════════════
# AUDIT L3 — POWER
# ══════════════════════════════════════════════════════════════════════

class PowerAuditL3(models.Model):
    # ── Identitas ────────────────────────────────────────────────────
    atlet         = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='audit_l3', verbose_name='Atlet')
    atlet_name    = models.CharField(max_length=150, blank=True, verbose_name='Nama Atlet (form)')
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True)
    jump_height_cm      = models.FloatField(null=True, blank=True, verbose_name='Tinggi Lompatan (cm)')
    sprint_30m_detik    = models.FloatField(null=True, blank=True, verbose_name='Sprint 30M (detik)')
    throw_jarak_m       = models.FloatField(null=True, blank=True, verbose_name='Jarak Lempar (m)')
    agility_ttest_detik = models.FloatField(null=True, blank=True, verbose_name='Agility T-Test (detik)')


    # ── Skor 5 Pilar ─────────────────────────────────────────────────
    score_jump    = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    score_sprint  = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    score_throw   = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    score_rsi     = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    score_agility = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Data Mentah RSI ───────────────────────────────────────────────
    rsi_jump_height  = models.FloatField(null=True, blank=True)
    rsi_contact_time = models.FloatField(null=True, blank=True)
    rsi_value        = models.FloatField(null=True, blank=True)

    # ── AI ────────────────────────────────────────────────────────────
    ai_rep_count        = models.IntegerField(null=True, blank=True)
    ai_confidence_score = models.FloatField(null=True, blank=True)

    # ── Hasil ────────────────────────────────────────────────────────
    total_skor         = models.FloatField(default=0)
    predikat           = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_naik         = models.BooleanField(default=False, verbose_name='Layak Kompetisi?')
    layak_bertahan     = models.BooleanField(default=False, verbose_name='Layak Bertahan di L3?')
    alasan_tidak_layak = models.CharField(max_length=255, blank=True)

    # ── Metadata ─────────────────────────────────────────────────────
    catatan    = models.TextField(blank=True, null=True)
    timestamp  = models.DateTimeField(default=timezone.now)
    created_by = models.CharField(max_length=100, blank=True, default='Coach Fanny')

    class Meta:
        ordering            = ['-timestamp']
        verbose_name        = 'L3 - Power'
        verbose_name_plural = 'L3 - Power'
        db_table            = 'hpcs_power_audit_l3'

    def __str__(self):
        return f"{self.atlet_name or self.atlet.nama_atlet} | {self.predikat} | {self.total_skor}"

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet
        if self.rsi_jump_height and self.rsi_contact_time and self.rsi_contact_time > 0:
            self.rsi_value = round(self.rsi_jump_height / self.rsi_contact_time, 3)
        self.total_skor    = _avg(self.score_jump, self.score_sprint, self.score_throw, self.score_rsi, self.score_agility)
        self.predikat      = _hitung_predikat(self.total_skor)
        self.layak_bertahan = self.total_skor >= 7.0
        self.layak_naik     = self.total_skor >= 9.0
        if not self.layak_naik:
            self.alasan_tidak_layak = f"Skor {self.total_skor} < 9.0. Pilar terlemah: {self.pilar_terendah}."
        else:
            self.alasan_tidak_layak = ''
        super().save(*args, **kwargs)

    @property
    def pilar_terendah(self):
        pilar = {
            'Jump': self.score_jump, 'Sprint': self.score_sprint,
            'Throw': self.score_throw, 'RSI': self.score_rsi, 'Agility': self.score_agility,
        }
        return min(pilar, key=pilar.get)

    @property
    def rekomendasi_auto(self):
        if self.predikat == 'ELITE':
            return "Power output ELITE. Atlet SIAP KOMPETISI."
        elif self.predikat == 'READY':
            return f"Belum layak kompetisi. Tingkatkan '{self.pilar_terendah}': plyometric 3x/minggu."
        elif self.predikat == 'DEVELOPING':
            return f"Kembali ke L2 Strength. Pilar terlemah: '{self.pilar_terendah}'."
        return f"Turun ke L1 evaluasi ulang mobilitas. Pilar kritis: '{self.pilar_terendah}'."


# ══════════════════════════════════════════════════════════════════════
# REKOMENDASI PROGRAM
# ══════════════════════════════════════════════════════════════════════

class RekomendasiProgram(models.Model):
    LEVEL_CHOICES = [
        ('L1', 'L1 — Correction'),
        ('L2', 'L2 — Strength'),
        ('L3', 'L3 — Power'),
    ]
    atlet           = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='rekomendasi')
    audit_level     = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    tanggal         = models.DateField(default=timezone.now)
    audit_l1_ref    = models.ForeignKey('CorrectionAuditL1', null=True, blank=True, on_delete=models.SET_NULL, related_name='rekomendasi')
    audit_l2_ref    = models.ForeignKey('StrengthAuditL2',   null=True, blank=True, on_delete=models.SET_NULL, related_name='rekomendasi')
    audit_l3_ref    = models.ForeignKey('PowerAuditL3',      null=True, blank=True, on_delete=models.SET_NULL, related_name='rekomendasi')
    isi_rekomendasi  = models.TextField()
    durasi_minggu    = models.PositiveIntegerField(default=4)
    sudah_dijalankan = models.BooleanField(default=False)
    dibuat_pada      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Rekomendasi Program'
        verbose_name_plural = 'Rekomendasi Program'
        ordering            = ['-tanggal']
        db_table            = 'hpcs_rekomendasi_program'

    def __str__(self):
        return f"Reko {self.audit_level} | {self.atlet.nama_atlet} | {self.tanggal}"


# ══════════════════════════════════════════════════════════════════════
# AUDIT L4 — SPEED, AGILITY & METABOLIC ENDURANCE
# ══════════════════════════════════════════════════════════════════════

class SpeedAgilityAuditL4(models.Model):
    # ── Identitas ────────────────────────────────────────────────────
    atlet         = models.ForeignKey('Atlet', on_delete=models.CASCADE, related_name='audit_l4')
    atlet_name    = models.CharField(max_length=150, blank=True)
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True)

    # ── Pilar 1: Hexagon Jump ─────────────────────────────────────────
    hex_waktu_putaran1 = models.FloatField(null=True, blank=True)
    hex_waktu_putaran2 = models.FloatField(null=True, blank=True)
    hex_waktu_putaran3 = models.FloatField(null=True, blank=True)
    hex_waktu_rata     = models.FloatField(null=True, blank=True)
    score_hex          = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Pilar 2: Punch Frequency (Boxing / Muay Thai / Karate) ────────
    punch_freq_10s         = models.IntegerField(null=True, blank=True)
    punch_postur_ok        = models.BooleanField(default=True)
    punch_reaction_time_ms = models.FloatField(null=True, blank=True)
    score_punch            = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Pilar 2 (alternatif): Kick Frequency (Taekwondo) ───────────────
    # Field terpisah dari punch_* karena instrumen berbeda (tendangan,
    # bukan pukulan). Cabang 'tkd' mengisi kick_*, cabang lain (boxing/
    # muaythai/karate) tetap mengisi punch_* seperti semula.
    kick_freq_10s         = models.IntegerField(null=True, blank=True)
    kick_postur_ok        = models.BooleanField(default=True)
    kick_reaction_time_ms = models.FloatField(null=True, blank=True)
    score_kick            = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Pilar 3: Yo-Yo IR ─────────────────────────────────────────────
    yoyo_level_tercapai  = models.IntegerField(null=True, blank=True)
    yoyo_shuttle_tercapai = models.IntegerField(null=True, blank=True)
    yoyo_total_jarak_m   = models.FloatField(null=True, blank=True)
    yoyo_vo2max_estimasi = models.FloatField(null=True, blank=True)
    score_yoyo           = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # ── Kondisi & Metadata ────────────────────────────────────────────
    kondisi_uji = models.CharField(
        max_length=50,
        choices=[
            ('FRESH',        'Fresh — Tanpa Pre-fatigue'),
            ('POST_SPARRING','Post-Sparring — Setelah Sparring 3 Ronde'),
            ('POST_CIRCUIT', 'Post-Circuit — Setelah Circuit Training'),
        ],
        default='FRESH'
    )
    catatan    = models.TextField(blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    # ── Hasil ────────────────────────────────────────────────────────
    total_skor         = models.FloatField(default=0)
    predikat           = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_kompetisi    = models.BooleanField(default=False)
    layak_bertahan     = models.BooleanField(default=False)
    rekomendasi_auto   = models.TextField(blank=True)
    alasan_tidak_layak = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'L4 - Speed & Agility'
        verbose_name_plural = 'L4 - Speed & Agility'
        ordering            = ['-timestamp']

    def __str__(self):
        return f"L4 {self.atlet_name} — {self.total_skor} ({self.predikat})"

    def hitung_hex_rata(self):
        times = [t for t in [self.hex_waktu_putaran1, self.hex_waktu_putaran2, self.hex_waktu_putaran3] if t]
        return round(sum(times) / len(times), 2) if times else None

    def hitung_vo2max(self):
        if self.yoyo_total_jarak_m:
            return round((self.yoyo_total_jarak_m * 0.0084) + 36.4, 1)
        return None

    @property
    def is_taekwondo(self):
        return bool(self.atlet_id and self.atlet.cabang == 'tkd')

    @property
    def score_pilar2(self):
        """Skor Pilar 2 (frekuensi serangan) — otomatis pilih score_kick untuk
        cabang Taekwondo ('tkd'), score_punch untuk cabang lain (Boxing/Muay
        Thai/Karate). Dipakai di kalkulasi_skor() agar total_skor selalu benar
        tanpa peduli field mana yang diisi form."""
        return self.score_kick if self.is_taekwondo else self.score_punch

    @property
    def pilar2_label(self):
        return 'Kick' if self.is_taekwondo else 'Punch'

    def kalkulasi_skor(self):
        scores = [self.score_hex, self.score_pilar2, self.score_yoyo]
        self.total_skor = round(sum(scores) / len(scores), 1)
        if self.total_skor >= 9.0:
            self.predikat       = 'ELITE'
            self.layak_kompetisi = True
            self.layak_bertahan  = True
            self.rekomendasi_auto = "Kapasitas Speed-Agility-Endurance Elit. Atlet siap kompetisi penuh."
        elif self.total_skor >= 7.0:
            self.predikat       = 'READY'
            self.layak_kompetisi = False
            self.layak_bertahan  = True
            self.rekomendasi_auto = "Kompeten. Target VO2 Max > 52 mL/kg/min dalam 8 minggu."
        elif self.total_skor >= 5.0:
            self.predikat       = 'DEVELOPING'
            self.layak_kompetisi = False
            self.layak_bertahan  = False
            self.rekomendasi_auto = "Dalam Pengembangan. Prioritaskan Yo-Yo Training dan Hexagon drill."
        else:
            self.predikat          = 'NOVICE'
            self.layak_kompetisi    = False
            self.layak_bertahan     = False
            self.alasan_tidak_layak = "Kembali perkuat L3 (Power) dan tambah volume aerobik base 4-6 minggu."
            self.rekomendasi_auto   = self.alasan_tidak_layak

    def save(self, *args, **kwargs):
        self.hex_waktu_rata      = self.hitung_hex_rata()
        self.yoyo_vo2max_estimasi = self.hitung_vo2max()
        self.kalkulasi_skor()
        super().save(*args, **kwargs)