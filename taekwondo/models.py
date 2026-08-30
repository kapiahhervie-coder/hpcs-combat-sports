"""
taekwondo/models.py — VERSI REBUILD SESUAI SOP "Revisi Final 2026"

PERUBAHAN dari versi sebelumnya (8 pilar hybrid -> 9 bagian resmi SOP):
1. Hip Rotation gabungan (internal+eksternal dijumlah jadi 1 skor) DIPECAH
   jadi 2 pilar terpisah: Hip Internal Rotation & Hip External Rotation,
   sesuai Tes 4B SOP yang menilai IR dan ER secara terpisah.
2. Single-Leg Balance yang tadinya rata-rata mata terbuka+tertutup diganti
   jadi SLST mata tertutup SAJA, dipisah per kaki (kanan/kiri), sesuai
   Tes 2 SOP.
3. Ditambahkan Y-Balance Test (YBT-LQ) — jangkauan ANT/PM/PL per kaki +
   panjang tungkai, dengan skor berbasis asimetri Anterior kanan-kiri
   (Tes 3 SOP). BELUM ADA di versi sebelumnya.
4. Thoracic Rotation diganti nama jadi Seated Trunk Rotation (field sama
   secara struktur, threshold beda — lihat Tes 4A SOP).
5. DITAMBAHKAN 3 pilar baru yang sebelumnya tidak ada sama sekali:
   Lumbar Extension Clearing Test (Tes 5, safety-gate/pain-override),
   Fixed Plumb Line Posture (Tes 6, observasional), Hi-Lo Breathing
   Observation (Tes 7, observasional).
6. DIHAPUS total (tidak ada dasar SOP-nya): Hip Hinge Pattern, Core
   Anti-Rotation, Dynamic Balance Recovery.
7. total_skor = rata-rata 8 pilar bernilai numerik (ankle, balance,
   ybalance, trunk_rotation, hip_ir, hip_er, postur, napas). Lumbar
   Extension SENGAJA DIKELUARKAN dari rata-rata karena sifatnya safety
   clearing gate (nyeri = rujuk, bukan skor rendah biasa) — lihat
   status_keputusan di bawah untuk override keselamatan.
8. Threshold predikat (8.3/5.8/4.2) TETAP SAMA seperti sebelumnya, dan
   TETAP dipakai supaya kompatibel dengan dashboard/report card lintas
   cabor yang membaca l1.total_skor & l1.predikat secara generik.
9. DITAMBAHKAN status_keputusan (HIJAU/KUNING/MERAH) sesuai kerangka
   keputusan SOP bagian 4 — MERAH (nyeri lumbar) memaksa layak_naik=False
   apa pun nilai total_skor-nya.

⚠️ CATATAN PEMETAAN KATEGORI USIA: SOP ini pakai 3 kategori usia
(Anak 6-11 / Remaja 12-17 / Dewasa 18-35), sedangkan field kategori_usia
di app ini pakai KATEGORI_USIA_CHOICES yang sama dengan L2/L3/L4
(kemungkinan YOUTH/JUNIOR/SENIOR/ELITE — field TIDAK diubah supaya tidak
mengganggu L2/L3/L4). Pemetaan yang dipakai di RUBRIK_L1 (taekwondo/views.py):
YOUTH -> ANAK, JUNIOR -> REMAJA, SENIOR & ELITE -> DEWASA. ASUMSI ini
perlu dikonfirmasi ulang oleh Coach Fanny — ganti di _band_usia_l1() pada
views.py kalau pemetaannya beda.

Timpa seluruh isi taekwondo/models.py dengan file ini, lalu jalankan
makemigrations & migrate (field berubah total, migration WAJIB).
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from combat.models import Atlet, KATEGORI_USIA_CHOICES, GENDER_CHOICES, PREDIKAT_CHOICES

LUMBAR_STATUS_CHOICES = [
    ('NYERI', 'Nyeri (safety override — skor 0, rujuk)'),
    ('TERBATAS', 'Tidak nyeri, tapi kaku/terbatas/ada kompensasi bahu'),
    ('MULUS', 'Bebas nyeri, gerakan mulus, panggul tetap menempel'),
]

POSTUR_STATUS_CHOICES = [
    ('DEVIASI_JELAS', 'Deviasi jelas'),
    ('DEVIASI_RINGAN', 'Deviasi ringan'),
    ('TANPA_DEVIASI', 'Tanpa deviasi jelas'),
]

NAPAS_STATUS_CHOICES = [
    ('DADA_DOMINAN', 'Gerak dada atas tampak dominan'),
    ('CAMPURAN', 'Pola campuran'),
    ('ABDOMINAL_DOMINAN', 'Ekspansi abdominal/lateral lower-rib tampak dominan'),
]

STATUS_KEPUTUSAN_CHOICES = [
    ('HIJAU', 'Hijau — Lanjut program'),
    ('KUNING', 'Kuning — Korektif & retest'),
    ('MERAH', 'Merah — Dihentikan & dirujuk'),
]


class CorrectionAuditL1TKD(models.Model):
    """
    L1 Correction — Taekwondo, mengikuti SOP & Rubrik HPCS Level 1
    Taekwondo (Revisi Final 2026): screening performa lapangan, BUKAN
    instrumen diagnosis medis.

    Skor per item (skor_*) DIHITUNG OTOMATIS oleh server dari data mentah
    hasil ukur (derajat/detik/cm) atau pilihan observasional, memakai
    RUBRIK_L1 & fungsi hitung_skor_l1_*() di taekwondo/views.py. Coach
    hanya input data mentah / observasi, bukan skor.
    """
    # -- Identitas --------------------------------------------------
    atlet         = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='audit_l1_tkd', verbose_name='Atlet')
    atlet_name    = models.CharField(max_length=150, blank=True, verbose_name='Nama Atlet (form)')
    kategori_usia = models.CharField(max_length=20, choices=KATEGORI_USIA_CHOICES, default='ELITE')
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Putra')
    kelas_berat   = models.FloatField(null=True, blank=True, verbose_name='Berat Badan (kg)')

    # -- A. Ankle Mobility — Weight-Bearing Lunge Test (WBLT) -----------
    wblt_kanan_cm = models.FloatField(null=True, blank=True, verbose_name='WBLT Kanan (cm)')
    wblt_kiri_cm  = models.FloatField(null=True, blank=True, verbose_name='WBLT Kiri (cm)')
    skor_ankle    = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- B. Static Balance — Single-Leg Stance Test, Mata Tertutup -------
    slst_kanan_detik = models.FloatField(null=True, blank=True, verbose_name='SLST Kaki Kanan Tumpu (detik, terbaik dari 2 trial)')
    slst_kiri_detik  = models.FloatField(null=True, blank=True, verbose_name='SLST Kaki Kiri Tumpu (detik, terbaik dari 2 trial)')
    skor_balance     = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- C. Dynamic Balance — Y-Balance Test (YBT-LQ) --------------------
    panjang_tungkai_kanan_cm = models.FloatField(null=True, blank=True, verbose_name='Panjang Tungkai Kanan (ASIS-maleolus, cm)')
    panjang_tungkai_kiri_cm  = models.FloatField(null=True, blank=True, verbose_name='Panjang Tungkai Kiri (ASIS-maleolus, cm)')
    ybt_ant_kanan_cm = models.FloatField(null=True, blank=True, verbose_name='YBT Anterior — Tumpu Kanan (cm)')
    ybt_ant_kiri_cm  = models.FloatField(null=True, blank=True, verbose_name='YBT Anterior — Tumpu Kiri (cm)')
    ybt_pm_kanan_cm  = models.FloatField(null=True, blank=True, verbose_name='YBT Posteromedial — Tumpu Kanan (cm)')
    ybt_pm_kiri_cm   = models.FloatField(null=True, blank=True, verbose_name='YBT Posteromedial — Tumpu Kiri (cm)')
    ybt_pl_kanan_cm  = models.FloatField(null=True, blank=True, verbose_name='YBT Posterolateral — Tumpu Kanan (cm)')
    ybt_pl_kiri_cm   = models.FloatField(null=True, blank=True, verbose_name='YBT Posterolateral — Tumpu Kiri (cm)')
    skor_ybalance    = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- D. Seated Trunk Rotation ------------------------------------
    trunk_rotasi_kanan_derajat = models.FloatField(null=True, blank=True, verbose_name='Trunk Rotation Kanan (derajat)')
    trunk_rotasi_kiri_derajat  = models.FloatField(null=True, blank=True, verbose_name='Trunk Rotation Kiri (derajat)')
    skor_trunk_rotation        = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- E. Seated Hip Internal Rotation ------------------------------
    hip_ir_kanan_derajat = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kanan (derajat)')
    hip_ir_kiri_derajat  = models.FloatField(null=True, blank=True, verbose_name='Hip Internal Rotation Kiri (derajat)')
    skor_hip_ir          = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- F. Seated Hip External Rotation ------------------------------
    hip_er_kanan_derajat = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kanan (derajat)')
    hip_er_kiri_derajat  = models.FloatField(null=True, blank=True, verbose_name='Hip External Rotation Kiri (derajat)')
    skor_hip_er          = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- G. Lumbar Extension Clearing Test (Modified Cobra) ---------------
    # Safety gate: NYERI wajib skor 0 & memaksa status_keputusan=MERAH,
    # tidak ikut dirata-rata ke total_skor (lihat property skor_neural_list).
    lumbar_status = models.CharField(max_length=20, choices=LUMBAR_STATUS_CHOICES, default='MULUS')
    skor_lumbar   = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- H. Fixed Plumb Line Posture Screening ----------------------------
    postur_status = models.CharField(max_length=20, choices=POSTUR_STATUS_CHOICES, default='TANPA_DEVIASI')
    skor_postur   = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- I. Hi-Lo Breathing Observation -----------------------------------
    napas_status = models.CharField(max_length=20, choices=NAPAS_STATUS_CHOICES, default='ABDOMINAL_DOMINAN')
    skor_napas   = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # -- AI --------------------------------------------------------
    ai_confidence_score = models.FloatField(null=True, blank=True)

    # -- Hasil --------------------------------------------------------
    total_skor         = models.FloatField(default=0, verbose_name='Total Skor (0-10, rata-rata 8 pilar numerik)')
    predikat           = models.CharField(max_length=20, choices=PREDIKAT_CHOICES, default='NOVICE')
    status_keputusan   = models.CharField(max_length=10, choices=STATUS_KEPUTUSAN_CHOICES, default='HIJAU', verbose_name='Kategori Keputusan HPCS (Hijau/Kuning/Merah)')
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
        """8 pilar bernilai numerik yang masuk rata-rata total_skor. Lumbar
        Extension SENGAJA tidak dimasukkan — lihat status_keputusan."""
        return [
            self.skor_ankle, self.skor_balance, self.skor_ybalance,
            self.skor_trunk_rotation, self.skor_hip_ir, self.skor_hip_er,
            self.skor_postur, self.skor_napas,
        ]

    def save(self, *args, **kwargs):
        if self.atlet_id and not self.atlet_name:
            self.atlet_name = self.atlet.nama_atlet

        # NOTE: skor_* SUDAH dihitung otomatis di view sebelum instance ini
        # dibuat (dari data mentah + RUBRIK_L1), jadi di sini tinggal
        # dirata-rata 8 pilar numerik (bukan 9 — Lumbar Extension dikeluarkan
        # karena sifatnya safety-gate, bukan skala performa biasa).
        self.total_skor = round(sum(self.skor_neural_list) / 8, 1)

        if self.total_skor >= 8.3:
            self.predikat = 'ELITE'
        elif self.total_skor >= 5.8:
            self.predikat = 'READY'
        elif self.total_skor >= 4.2:
            self.predikat = 'DEVELOPING'
        else:
            self.predikat = 'NOVICE'

        # Kerangka keputusan HPCS (bagian 4 SOP): Merah kalau nyeri lumbar
        # (safety override, wajib rujuk) — mengalahkan total_skor berapa pun.
        # Kuning kalau ada pilar "Kurang" (skor <5.5) atau deviasi postural
        # jelas tanpa nyeri. Hijau kalau semua bersih.
        if self.lumbar_status == 'NYERI':
            self.status_keputusan = 'MERAH'
        elif any(s < 5.5 for s in self.skor_neural_list) or self.postur_status == 'DEVIASI_JELAS':
            self.status_keputusan = 'KUNING'
        else:
            self.status_keputusan = 'HIJAU'

        if self.status_keputusan == 'MERAH':
            self.layak_naik = False
            self.alasan_tidak_layak = (
                "Lumbar Extension Clearing Test: NYERI (safety override, skor 0). "
                "Atlet WAJIB dirujuk ke tenaga kesehatan berwenang sebelum tes/latihan lanjutan. "
                "Bukan diagnosis — hanya skrining performa lapangan."
            )
        elif self.predikat in ('ELITE', 'READY'):
            self.layak_naik = True
            self.alasan_tidak_layak = ''
        else:
            self.layak_naik = False
            self.alasan_tidak_layak = (
                f"Skor {self.total_skor}/10 ({self.status_keputusan}). "
                f"Item terlemah: {self.item_terlemah}. "
                f"Wajib program korektif mobility/stability sebelum lanjut."
            )

        super().save(*args, **kwargs)

    @property
    def item_terlemah(self):
        labels = {
            'Ankle Mobility (WBLT)': self.skor_ankle,
            'Static Balance (SLST)': self.skor_balance,
            'Dynamic Balance (Y-Balance)': self.skor_ybalance,
            'Seated Trunk Rotation': self.skor_trunk_rotation,
            'Hip Internal Rotation': self.skor_hip_ir,
            'Hip External Rotation': self.skor_hip_er,
            'Fixed Plumb Line Posture': self.skor_postur,
            'Hi-Lo Breathing': self.skor_napas,
        }
        return min(labels, key=labels.get)

    @property
    def ybt_composite_kanan(self):
        """Composite Score (%) = (ANT+PM+PL) / (3 x panjang tungkai) x 100 — kaki kanan sebagai tumpu."""
        panjang = self.panjang_tungkai_kanan_cm
        if not panjang or panjang <= 0:
            return None
        vals = [self.ybt_ant_kanan_cm, self.ybt_pm_kanan_cm, self.ybt_pl_kanan_cm]
        if any(v is None for v in vals):
            return None
        return round(sum(vals) / (3 * panjang) * 100, 1)

    @property
    def ybt_composite_kiri(self):
        panjang = self.panjang_tungkai_kiri_cm
        if not panjang or panjang <= 0:
            return None
        vals = [self.ybt_ant_kiri_cm, self.ybt_pm_kiri_cm, self.ybt_pl_kiri_cm]
        if any(v is None for v in vals):
            return None
        return round(sum(vals) / (3 * panjang) * 100, 1)

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
        if self.status_keputusan == 'MERAH':
            return "🔴 STOP — Lumbar Extension nyeri (safety override). Rujuk ke tenaga kesehatan berwenang sebelum melanjutkan tes/latihan apa pun."
        if self.predikat == 'ELITE':
            return "🟢 Semua pilar screening baik. Lanjut ke L2 Strength Assessment."
        elif self.predikat == 'READY':
            return f"🟢 Layak ke L2. Tetap latih '{nama}' 2-3x/minggu untuk konsolidasi."
        elif self.predikat == 'DEVELOPING':
            return f"🟡 Tahan ke L2. Fokus 4-6 minggu program korektif pada '{nama}', lalu retest."
        return f"🟡 Kontrol mobility/stability masih rendah, prioritaskan '{nama}'. Wajib program korektif 8 minggu sebelum retest."