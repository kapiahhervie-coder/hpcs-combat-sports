"""
periodization/models.py
Pilar 3 HPCS -- Engine Periodisasi Otomatis (Makro, Meso, Mikro).

Referensi konsep:
- Makrosiklus (1-4 tahun): roadmap jangka panjang menuju event kompetisi
  (Kejurda/Kejurnas/PON), menampilkan kurva Volume vs Intensitas.
- Mesosiklus (4-6 minggu): fase spesifik (GPP/SPP/Pre-Comp/Comp) dengan
  porsi fokus L1-L4 tersendiri.
- Mikrosiklus (7 hari): kontainer mingguan -- isi latihan harian
  detailnya nanti nempel dari app workout_prescription (tahap
  berikutnya), supaya periodization tetap fokus di 'kerangka jadwal',
  bukan 'isi latihan'.
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta
from combat.models import Atlet


EVENT_TARGET_CHOICES = [
    ('kejurda',   'Kejuaraan Daerah (Kejurda)'),
    ('kejurnas',  'Kejuaraan Nasional (Kejurnas)'),
    ('pon',       'PON'),
    ('sea_games', 'SEA Games'),
    ('lainnya',   'Lainnya'),
]

STATUS_PROGRAM_CHOICES = [
    ('DRAFT',      'Draft'),
    ('AKTIF',      'Aktif Berjalan'),
    ('SELESAI',    'Selesai'),
    ('DIBATALKAN', 'Dibatalkan'),
]

FASE_MESO_CHOICES = [
    ('GPP',      'General Physical Preparation'),
    ('SPP',      'Specific Physical Preparation'),
    ('PRE_COMP', 'Pre-Competition'),
    ('COMP',     'Competition'),
    ('TRANSISI', 'Transisi / Recovery'),
]


class MacroProgram(models.Model):
    """Roadmap jangka panjang (1-4 tahun) menuju 1 event target."""
    atlet          = models.ForeignKey(Atlet, on_delete=models.CASCADE, related_name='macro_programs')
    nama_program   = models.CharField(max_length=150, help_text="mis. 'Persiapan PON 2028'")
    event_target   = models.CharField(max_length=20, choices=EVENT_TARGET_CHOICES, default='lainnya')
    nama_event     = models.CharField(max_length=150, blank=True, help_text="Detail nama event, mis. 'PON XXII Aceh-Sumut'")
    tanggal_mulai  = models.DateField()
    tanggal_target = models.DateField(help_text="Tanggal event kompetisi yang dituju")
    status         = models.CharField(max_length=20, choices=STATUS_PROGRAM_CHOICES, default='DRAFT')
    catatan        = models.TextField(blank=True)
    dibuat_pada    = models.DateTimeField(auto_now_add=True)
    diupdate_pada  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Makrosiklus (Program Jangka Panjang)'
        verbose_name_plural = 'Makrosiklus (Program Jangka Panjang)'
        ordering            = ['-tanggal_mulai']

    def __str__(self):
        return f"{self.nama_program} ({self.atlet.nama_atlet})"

    @property
    def durasi_minggu(self):
        if self.tanggal_mulai and self.tanggal_target:
            return max((self.tanggal_target - self.tanggal_mulai).days // 7, 0)
        return 0

    @property
    def sisa_minggu(self):
        if self.tanggal_target:
            return max((self.tanggal_target - timezone.now().date()).days // 7, 0)
        return 0

    @property
    def progres_persen(self):
        """Persentase waktu yang sudah dilalui dari total durasi program."""
        total = self.durasi_minggu
        if total <= 0:
            return 0
        terlewati = max(total - self.sisa_minggu, 0)
        return min(round((terlewati / total) * 100), 100)


class MesoCycle(models.Model):
    """
    Fase 4-6 minggu di dalam 1 MacroProgram, dengan fokus & target
    volume/intensitas tersendiri per fase (GPP/SPP/Pre-Comp/Comp).
    """
    macro_program     = models.ForeignKey(MacroProgram, on_delete=models.CASCADE, related_name='meso_cycles')
    nama_fase         = models.CharField(max_length=20, choices=FASE_MESO_CHOICES)
    urutan            = models.PositiveIntegerField(default=1, help_text="Urutan fase ini dalam macro program, mis. 1, 2, 3")
    tanggal_mulai     = models.DateField()
    tanggal_selesai   = models.DateField()

    # Porsi fokus per parameter L1-L4 (persen, idealnya total ~100)
    fokus_l1_persen   = models.PositiveIntegerField(default=25, help_text="Porsi fokus Koreksi/Mobility (L1)")
    fokus_l2_persen   = models.PositiveIntegerField(default=25, help_text="Porsi fokus Strength (L2)")
    fokus_l3_persen   = models.PositiveIntegerField(default=25, help_text="Porsi fokus Power (L3)")
    fokus_l4_persen   = models.PositiveIntegerField(default=25, help_text="Porsi fokus Speed/Agility (L4)")

    # Buat kurva Volume vs Intensitas (skala 1-10, diisi pelatih)
    volume_target     = models.PositiveIntegerField(default=5, help_text="Skala 1-10")
    intensitas_target = models.PositiveIntegerField(default=5, help_text="Skala 1-10")

    catatan           = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Mesosiklus (Fase 4-6 Minggu)'
        verbose_name_plural = 'Mesosiklus (Fase 4-6 Minggu)'
        ordering            = ['macro_program', 'urutan']

    def __str__(self):
        return f"{self.get_nama_fase_display()} - {self.macro_program.nama_program}"

    @property
    def durasi_minggu(self):
        if self.tanggal_mulai and self.tanggal_selesai:
            # +1 karena tanggal_selesai itu INKLUSIF (hari terakhir fase
            # ini, bukan hari pertama fase berikutnya) -- tanpa +1,
            # pembagian bulat ke bawah bikin hasilnya kurang 1 minggu.
            return max(((self.tanggal_selesai - self.tanggal_mulai).days + 1) // 7, 0)
        return 0

    @property
    def total_fokus_persen(self):
        """Buat validasi/tampilan -- idealnya nilai ini = 100."""
        return self.fokus_l1_persen + self.fokus_l2_persen + self.fokus_l3_persen + self.fokus_l4_persen


class MicroCycle(models.Model):
    """
    Kontainer 1 minggu latihan di dalam 1 MesoCycle. Isi latihan
    harian detail (dosis, video, dst) dihubungkan nanti dari app
    workout_prescription lewat ForeignKey ke sini -- MicroCycle di
    sini sengaja tetap ringan, cuma kerangka jadwalnya.
    """
    meso_cycle    = models.ForeignKey(MesoCycle, on_delete=models.CASCADE, related_name='micro_cycles')
    minggu_ke     = models.PositiveIntegerField(help_text="Minggu ke berapa dalam mesocycle ini, mis. 1, 2, 3")
    tanggal_mulai = models.DateField(help_text="Tanggal Senin di minggu ini")
    catatan       = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Mikrosiklus (Minggu Latihan)'
        verbose_name_plural = 'Mikrosiklus (Minggu Latihan)'
        ordering            = ['meso_cycle', 'minggu_ke']
        unique_together     = ('meso_cycle', 'minggu_ke')

    def __str__(self):
        return f"Minggu {self.minggu_ke} - {self.meso_cycle}"

    @property
    def tanggal_selesai(self):
        return self.tanggal_mulai + timedelta(days=6)