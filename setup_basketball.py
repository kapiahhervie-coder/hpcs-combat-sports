import os

# 1. apps.py
open("basketball/apps.py","w",encoding="utf-8").write("""from django.apps import AppConfig

class BasketballConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'basketball'
    verbose_name = 'Basketball'
""")
print("OK: apps.py")

# 2. urls.py
open("basketball/urls.py","w",encoding="utf-8").write("""from django.urls import path
from . import views

app_name = 'basketball'

urlpatterns = [
    path('dashboard/', views.DashboardBasketballView.as_view(), name='dashboard'),
    path('daftar-atlet/', views.DaftarAtletBasketView.as_view(), name='daftar_atlet'),
    path('l1-correction/', views.L1CorrectionBasketView.as_view(), name='l1_correction'),
    path('l1-correction/hapus/<int:pk>/', views.hapus_l1_basket, name='hapus_l1'),
    path('l2-strength/', views.L2StrengthBasketView.as_view(), name='l2_strength'),
    path('l2-strength/hapus/<int:pk>/', views.hapus_l2_basket, name='hapus_l2'),
    path('l3-power/', views.L3PowerBasketView.as_view(), name='l3_power'),
    path('l3-power/hapus/<int:pk>/', views.hapus_l3_basket, name='hapus_l3'),
    path('l4-specific/', views.L4SpecificBasketView.as_view(), name='l4_specific'),
    path('l4-specific/hapus/<int:pk>/', views.hapus_l4_basket, name='hapus_l4'),
]
""")
print("OK: urls.py")

# 3. models.py
open("basketball/models.py","w",encoding="utf-8").write("""\"\"\"
HPCS Basketball — Models
High Performance Coaching System
\"\"\"
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

GENDER_CHOICES = [('Putra','Putra'),('Putri','Putri')]
KATEGORI_CHOICES = [('ELITE','Elite'),('YOUTH','Youth'),('JUNIOR','Junior'),('SENIOR','Senior')]
PREDIKAT_CHOICES = [('ELITE','Elite'),('READY','Ready'),('DEVELOPING','Developing'),('NOVICE','Novice')]
POSISI_CHOICES = [
    ('PG','Point Guard'),('SG','Shooting Guard'),('SF','Small Forward'),
    ('PF','Power Forward'),('C','Center'),
]
LTAD_CHOICES = [
    ('fundamental','FUNdamental (6-9 thn)'),('learn_train','Learn to Train (9-12 thn)'),
    ('train_train','Train to Train (12-16 thn)'),('train_compete','Train to Compete (16-19 thn)'),
    ('train_win','Train to Win (19+ thn)'),
]

def _avg(*scores):
    valid = [s for s in scores if s is not None and s > 0]
    return round(sum(valid)/len(valid),1) if valid else 0.0

def _predikat(skor):
    if skor >= 9.0: return 'ELITE'
    if skor >= 7.0: return 'READY'
    if skor >= 5.0: return 'DEVELOPING'
    return 'NOVICE'


class AtletBasket(models.Model):
    nama_atlet    = models.CharField(max_length=100)
    kategori_umur = models.CharField(max_length=10, choices=KATEGORI_CHOICES)
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES)
    posisi        = models.CharField(max_length=5, choices=POSISI_CHOICES, blank=True)
    kelas_berat   = models.FloatField(verbose_name='Berat Badan (kg)')
    tinggi_badan  = models.FloatField(null=True, blank=True, verbose_name='Tinggi Badan (cm)')
    wingspan      = models.FloatField(null=True, blank=True, verbose_name='Wingspan (cm)')
    tanggal_lahir = models.DateField(null=True, blank=True)
    tahap_ltad    = models.CharField(max_length=20, choices=LTAD_CHOICES, blank=True)
    pelatih       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='atlet_basket')
    dibuat_pada   = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Atlet Basket'
        verbose_name_plural = 'Atlet Basket'
        ordering = ['nama_atlet']

    def __str__(self):
        return f'{self.nama_atlet} ({self.get_posisi_display() or "-"})'

    @property
    def tinggi_badan_display(self):
        return f'{self.tinggi_badan} cm' if self.tinggi_badan else '-'

    @property
    def wingspan_ratio(self):
        if self.wingspan and self.tinggi_badan and self.tinggi_badan > 0:
            return round(self.wingspan / self.tinggi_badan, 2)
        return None


class BasketL1Correction(models.Model):
    \"\"\"L1 - Fondasi Gerak: Mobilitas, Stabilitas, Postur\"\"\"
    atlet         = models.ForeignKey(AtletBasket, on_delete=models.CASCADE, related_name='audit_l1')
    atlet_name    = models.CharField(max_length=150, blank=True)
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    posisi        = models.CharField(max_length=5, choices=POSISI_CHOICES, blank=True)

    # Pilar 1: Ankle Mobility
    ankle_kiri_cm  = models.FloatField(null=True, blank=True)
    ankle_kanan_cm = models.FloatField(null=True, blank=True)
    score_ankle    = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 2: Hip Mobility
    hip_fleksi_kiri  = models.FloatField(null=True, blank=True)
    hip_fleksi_kanan = models.FloatField(null=True, blank=True)
    score_hip        = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 3: Shoulder Mobility
    shoulder_fleksi = models.FloatField(null=True, blank=True)
    score_shoulder  = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 4: Stability / Balance
    balance_kiri_detik  = models.FloatField(null=True, blank=True)
    balance_kanan_detik = models.FloatField(null=True, blank=True)
    score_stability     = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 5: Postur & Spine
    score_posture = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Hasil
    total_skor  = models.FloatField(default=0)
    predikat    = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_naik  = models.BooleanField(default=False)
    catatan     = models.TextField(blank=True)
    timestamp   = models.DateTimeField(default=timezone.now)
    created_by  = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Basket L1 Correction'
        db_table = 'hpcs_basket_l1'

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet
        self.total_skor = _avg(self.score_ankle, self.score_hip, self.score_shoulder, self.score_stability, self.score_posture)
        self.predikat = _predikat(self.total_skor)
        self.layak_naik = self.total_skor >= 7.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'L1 Basket {self.atlet_name} | {self.predikat} | {self.total_skor}'


class BasketL2Strength(models.Model):
    \"\"\"L2 - Kekuatan Otot: Lower, Upper, Core\"\"\"
    atlet         = models.ForeignKey(AtletBasket, on_delete=models.CASCADE, related_name='audit_l2')
    atlet_name    = models.CharField(max_length=150, blank=True)
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    posisi        = models.CharField(max_length=5, choices=POSISI_CHOICES, blank=True)
    kelas_berat   = models.FloatField(null=True, blank=True)

    # Pilar 1: Lower Body
    squat_1rm       = models.FloatField(null=True, blank=True, verbose_name='Squat 1RM (kg)')
    squat_bw_ratio  = models.FloatField(null=True, blank=True)
    score_lower     = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 2: Upper Push
    bench_1rm      = models.FloatField(null=True, blank=True, verbose_name='Bench Press 1RM (kg)')
    score_upper    = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 3: Core
    plank_detik    = models.IntegerField(null=True, blank=True)
    score_core     = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 4: Single Leg (penting untuk basket)
    single_leg_squat_kiri  = models.IntegerField(null=True, blank=True)
    single_leg_squat_kanan = models.IntegerField(null=True, blank=True)
    score_single_leg       = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 5: Grip Strength
    grip_kiri_kg  = models.FloatField(null=True, blank=True)
    grip_kanan_kg = models.FloatField(null=True, blank=True)
    score_grip    = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    total_skor  = models.FloatField(default=0)
    predikat    = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_naik  = models.BooleanField(default=False)
    catatan     = models.TextField(blank=True)
    timestamp   = models.DateTimeField(default=timezone.now)
    created_by  = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Basket L2 Strength'
        db_table = 'hpcs_basket_l2'

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet
        if self.squat_1rm and self.kelas_berat and self.kelas_berat > 0:
            self.squat_bw_ratio = round(self.squat_1rm / self.kelas_berat, 2)
        self.total_skor = _avg(self.score_lower, self.score_upper, self.score_core, self.score_single_leg, self.score_grip)
        self.predikat = _predikat(self.total_skor)
        self.layak_naik = self.total_skor >= 7.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'L2 Basket {self.atlet_name} | {self.predikat} | {self.total_skor}'


class BasketL3Power(models.Model):
    \"\"\"L3 - Daya Ledak: Vertical Jump, Sprint, Agility\"\"\"
    atlet         = models.ForeignKey(AtletBasket, on_delete=models.CASCADE, related_name='audit_l3')
    atlet_name    = models.CharField(max_length=150, blank=True)
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    posisi        = models.CharField(max_length=5, choices=POSISI_CHOICES, blank=True)

    # Pilar 1: Vertical Jump (kritis untuk basket)
    vertical_jump_cm   = models.FloatField(null=True, blank=True)
    standing_reach_cm  = models.FloatField(null=True, blank=True)
    max_reach_cm       = models.FloatField(null=True, blank=True)
    score_jump         = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 2: Sprint
    sprint_30m_detik   = models.FloatField(null=True, blank=True)
    sprint_court_detik = models.FloatField(null=True, blank=True, verbose_name='Sprint Full Court (detik)')
    score_sprint       = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 3: Agility (Lane Agility Test)
    lane_agility_detik = models.FloatField(null=True, blank=True)
    score_agility      = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 4: Reactive Strength
    drop_jump_cm       = models.FloatField(null=True, blank=True)
    rsi_value          = models.FloatField(null=True, blank=True)
    score_rsi          = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 5: Change of Direction
    cod_detik          = models.FloatField(null=True, blank=True, verbose_name='COD T-Test (detik)')
    score_cod          = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    total_skor     = models.FloatField(default=0)
    predikat       = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_naik     = models.BooleanField(default=False)
    layak_bertahan = models.BooleanField(default=False)
    catatan        = models.TextField(blank=True)
    timestamp      = models.DateTimeField(default=timezone.now)
    created_by     = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Basket L3 Power'
        db_table = 'hpcs_basket_l3'

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet
        self.total_skor = _avg(self.score_jump, self.score_sprint, self.score_agility, self.score_rsi, self.score_cod)
        self.predikat = _predikat(self.total_skor)
        self.layak_naik = self.total_skor >= 9.0
        self.layak_bertahan = self.total_skor >= 7.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'L3 Basket {self.atlet_name} | {self.predikat} | {self.total_skor}'


class BasketL4Specific(models.Model):
    \"\"\"L4 - Spesifik Basket: Shooting, Dribbling, Defense\"\"\"
    atlet         = models.ForeignKey(AtletBasket, on_delete=models.CASCADE, related_name='audit_l4')
    atlet_name    = models.CharField(max_length=150, blank=True)
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    posisi        = models.CharField(max_length=5, choices=POSISI_CHOICES, blank=True)

    # Pilar 1: Shooting
    free_throw_pct  = models.FloatField(null=True, blank=True, verbose_name='Free Throw %')
    midrange_pct    = models.FloatField(null=True, blank=True, verbose_name='Mid-Range %')
    three_point_pct = models.FloatField(null=True, blank=True, verbose_name='3-Point %')
    score_shooting  = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 2: Ball Handling / Dribbling
    dribble_speed_dominant = models.FloatField(null=True, blank=True, verbose_name='Dribble Speed Dom (detik)')
    dribble_speed_weak     = models.FloatField(null=True, blank=True, verbose_name='Dribble Speed Weak (detik)')
    weak_hand_ratio        = models.FloatField(null=True, blank=True)
    score_dribbling        = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 3: Defense
    lateral_speed_detik = models.FloatField(null=True, blank=True, verbose_name='Lateral Slide Speed (detik)')
    contest_rate_pct    = models.FloatField(null=True, blank=True, verbose_name='Shot Contest Rate %')
    score_defense       = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 4: IQ / Decision Making (subjektif coach)
    court_vision_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    decision_speed     = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    score_iq           = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Pilar 5: Conditioning (Yo-Yo)
    yoyo_level        = models.IntegerField(null=True, blank=True)
    yoyo_jarak_m      = models.FloatField(null=True, blank=True)
    vo2max_estimasi   = models.FloatField(null=True, blank=True)
    score_conditioning = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    total_skor      = models.FloatField(default=0)
    predikat        = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    layak_kompetisi = models.BooleanField(default=False)
    catatan         = models.TextField(blank=True)
    timestamp       = models.DateTimeField(default=timezone.now)
    created_by      = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Basket L4 Specific'
        db_table = 'hpcs_basket_l4'

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet
        if self.dribble_speed_dominant and self.dribble_speed_weak and self.dribble_speed_dominant > 0:
            self.weak_hand_ratio = round(self.dribble_speed_dominant / self.dribble_speed_weak * 100, 1)
        if self.yoyo_jarak_m:
            self.vo2max_estimasi = round((self.yoyo_jarak_m * 0.0084) + 36.4, 1)
        self.score_iq = _avg(self.court_vision_score, self.decision_speed)
        self.total_skor = _avg(self.score_shooting, self.score_dribbling, self.score_defense, self.score_iq, self.score_conditioning)
        self.predikat = _predikat(self.total_skor)
        self.layak_kompetisi = self.total_skor >= 8.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f'L4 Basket {self.atlet_name} | {self.predikat} | {self.total_skor}'
""")
print("OK: models.py")

# 4. Buat folder templates
os.makedirs("basketball/templates/basketball", exist_ok=True)
print("OK: folder templates")

print("\nSemua file dasar berhasil dibuat!")
print("Langkah berikutnya:")
print("1. Daftarkan 'basketball' di settings.py")
print("2. Jalankan makemigrations")
print("3. Buat views.py")