"""
workout_prescription/models.py
Pilar 2 HPCS -- Preskripsi & Auto-Generated Program.

ExerciseBank   : katalog/bank gerakan latihan, dikategorikan L1-L4.
AutoPrescription: penugasan 1 gerakan ke 1 hari tertentu di dalam 1
                  MicroCycle (app periodization) -- ini yang jadi
                  "jadwal latihan harian" yang dilihat atlet/pelatih.

Catatan: Rule Engine (mis. "L3/L4 dikunci kalau skor L1 < 7.0") itu
LOGIKA, bukan struktur data -- akan ditulis di services.py Tahap 2,
bukan di models.py ini.
"""
from django.db import models
from datetime import timedelta
from combat.models import Cabor
from periodization.models import MicroCycle


KATEGORI_LATIHAN_CHOICES = [
    ('L1', 'L1 - Koreksi (Mobility/Stability)'),
    ('L2', 'L2 - Kekuatan (Strength)'),
    ('L3', 'L3 - Power (Plyometric/RFD)'),
    ('L4', 'L4 - Kecepatan & Reaktif (Speed/Agility)'),
]

HARI_CHOICES = [
    (1, 'Senin'), (2, 'Selasa'), (3, 'Rabu'), (4, 'Kamis'),
    (5, "Jum'at"), (6, 'Sabtu'), (7, 'Minggu'),
]


class ExerciseBank(models.Model):
    """Katalog gerakan latihan -- 1 baris = 1 jenis gerakan yang bisa dipakai berulang kali."""
    nama_latihan       = models.CharField(max_length=150)
    kategori           = models.CharField(max_length=2, choices=KATEGORI_LATIHAN_CHOICES)
    sub_kategori       = models.CharField(max_length=100, blank=True, help_text="mis. 'Ankle Mobility', 'Upper Body Strength'")
    deskripsi          = models.TextField(blank=True, help_text="Cara melakukan gerakan")
    video_url          = models.URLField(blank=True, help_text="Link video peragaan (YouTube, dll)")

    # Dosis default -- bisa di-override per-atlet di AutoPrescription
    default_set        = models.PositiveIntegerField(null=True, blank=True)
    default_reps       = models.CharField(max_length=30, blank=True, help_text="mis. '8-12', '30 detik', 'AMRAP'")
    default_rest_detik = models.PositiveIntegerField(null=True, blank=True)

    cabor              = models.ForeignKey(
        Cabor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='exercise_bank',
        help_text="Kosongkan kalau gerakan ini generik/berlaku semua cabor"
    )
    aktif              = models.BooleanField(default=True)
    dibuat_pada        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Bank Latihan'
        verbose_name_plural = 'Bank Latihan'
        ordering            = ['kategori', 'nama_latihan']

    def __str__(self):
        return f"[{self.kategori}] {self.nama_latihan}"


class AutoPrescription(models.Model):
    """
    Penugasan 1 gerakan dari ExerciseBank ke 1 hari tertentu di dalam
    1 MicroCycle (minggu latihan). Dosis di sini BOLEH beda dari
    default di ExerciseBank, karena dipersonalisasi per atlet.
    """
    micro_cycle          = models.ForeignKey(MicroCycle, on_delete=models.CASCADE, related_name='daftar_latihan')
    exercise             = models.ForeignKey(ExerciseBank, on_delete=models.PROTECT, related_name='penugasan')
    hari_ke              = models.PositiveSmallIntegerField(choices=HARI_CHOICES, help_text="Hari ke berapa dalam minggu ini")

    set_diberikan        = models.PositiveIntegerField(null=True, blank=True)
    reps_diberikan       = models.CharField(max_length=30, blank=True)
    rest_diberikan_detik = models.PositiveIntegerField(null=True, blank=True)

    catatan_pelatih      = models.TextField(blank=True)
    selesai              = models.BooleanField(default=False, help_text="Sudah dikerjakan atlet?")
    dibuat_pada          = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Preskripsi Latihan Harian'
        verbose_name_plural = 'Preskripsi Latihan Harian'
        ordering            = ['micro_cycle', 'hari_ke']

    def __str__(self):
        return f"{self.get_hari_ke_display()} - {self.exercise.nama_latihan} ({self.micro_cycle})"

    @property
    def tanggal(self):
        """Tanggal aktual hari ini, dihitung dari MicroCycle.tanggal_mulai + hari_ke."""
        return self.micro_cycle.tanggal_mulai + timedelta(days=self.hari_ke - 1)

    @property
    def set_final(self):
        """Dosis yang beneran dipakai: personalisasi kalau diisi, kalau kosong pakai default bank."""
        return self.set_diberikan or self.exercise.default_set

    @property
    def reps_final(self):
        return self.reps_diberikan or self.exercise.default_reps

    @property
    def rest_final_detik(self):
        return self.rest_diberikan_detik or self.exercise.default_rest_detik