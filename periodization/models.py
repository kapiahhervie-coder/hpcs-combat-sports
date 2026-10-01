"""
periodization/models.py
Pilar 3 HPCS -- Engine Periodisasi Otomatis (Makro, Meso, Mikro).

Referensi konsep:
- Makrosiklus (1-4 tahun): roadmap jangka panjang menuju event kompetisi
  (Kejurda/Kejurnas/PON), menampilkan kurva Volume vs Intensitas, plus
  kalender kompetisi (KompetisiTarget) sepanjang roadmap-nya.
- Mesosiklus (4-6 minggu): fase spesifik (GPP/SPP/Pre-Comp/Comp) dengan
  porsi fokus L1-L4 tersendiri, objektif fisik per fase, dan target
  performa spesifik (TargetPerforma) yang mau dicapai di fase itu.
- Mikrosiklus (7 hari): kontainer mingguan, isinya SesiLatihan per hari
  (1-7) dengan pilar fokus mengikuti prinsip hard-easy alternation
  (selang-seling berat-ringan ala program elite/Olimpiade), dan tiap
  sesi bisa dirinci sampai LatihanItem (exercise/set/rep/istirahat).
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

LEVEL_KOMPETISI_CHOICES = [
    ('domestik',      'Domestik'),
    ('internasional', 'Internasional'),
    ('kualifikasi',   'Kualifikasi'),
]

STATUS_TARGET_KOMPETISI_CHOICES = [
    ('TARGET_UTAMA',        'Target Utama'),
    ('OPSIONAL',             'Opsional'),
    ('PERTIMBANGAN_PELATIH', 'Berdasarkan Pertimbangan Pelatih'),
]

PILAR_CHOICES = [
    ('L1',     'L1 - Correction / Mobility'),
    ('L2',     'L2 - Strength'),
    ('L3',     'L3 - Power'),
    ('L4',     'L4 - Speed & Agility'),
    ('CUSTOM', 'Target Kustom Pelatih'),
]

PILAR_FOKUS_HARIAN_CHOICES = [
    ('L1',        'L1 - Correction / Mobility'),
    ('L2',        'L2 - Strength'),
    ('L3',        'L3 - Power'),
    ('L4',        'L4 - Speed & Agility'),
    ('TEKNIK',    'Teknik / Skill'),
    ('RECOVERY',  'Recovery / Regenerasi'),
    ('REST',      'Istirahat Penuh'),
    ('KOMPETISI', 'Kompetisi / Try-Out'),
]

KATEGORI_LATIHAN_CHOICES = [
    ('PEMANASAN',   'Pemanasan'),
    ('INTI',        'Latihan Inti'),
    ('PENDINGINAN', 'Pendinginan'),
]

WAKTU_SESI_CHOICES = [
    ('PAGI',  'Pagi'),
    ('SIANG', 'Siang'),
    ('SORE',  'Sore'),
    ('MALAM', 'Malam'),
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


class KompetisiTarget(models.Model):
    """
    Kalender kompetisi di sepanjang 1 MacroProgram -- bukan cuma 1
    event target di akhir, tapi bisa banyak kompetisi try-out/
    kualifikasi/kejuaraan di tengah jalan menuju event puncak.
    """
    macro_program   = models.ForeignKey(MacroProgram, on_delete=models.CASCADE, related_name='kompetisi_list')
    nama_kompetisi  = models.CharField(max_length=150, help_text="mis. 'Kejurda Sumut 2027'")
    tanggal_mulai   = models.DateField()
    tanggal_selesai = models.DateField(blank=True, null=True, help_text="Kosongkan kalau kompetisi cuma 1 hari")
    level           = models.CharField(max_length=20, choices=LEVEL_KOMPETISI_CHOICES, default='domestik')
    status          = models.CharField(max_length=25, choices=STATUS_TARGET_KOMPETISI_CHOICES, default='OPSIONAL')
    catatan         = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Target Kompetisi'
        verbose_name_plural = 'Kalender Kompetisi'
        ordering            = ['tanggal_mulai']

    def __str__(self):
        return f"{self.nama_kompetisi} ({self.tanggal_mulai})"


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

    # Objektif fisik per fase -- deskripsi tujuan, melengkapi porsi %
    # fokus_l1-l4 di atas yang sifatnya angka. Sengaja fokus fisik saja
    # dulu (bukan teknik/taktik/psikologis).
    objektif_fisik    = models.TextField(blank=True, help_text="mis. 'Bangun basis kekuatan umum & daya tahan aerobik'")
    objektif_teknik   = models.TextField(blank=True, help_text="Objektif teknik/skill fase ini")
    objektif_taktik   = models.TextField(blank=True, help_text="Objektif taktik fase ini")
    objektif_mental   = models.TextField(blank=True, help_text="Objektif mental/psikologis fase ini")

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


class TargetPerforma(models.Model):
    """
    Target performa fisik spesifik yang mau dicapai di 1 fase (mis.
    'Sprint 20m: 3.1 detik'). Bisa nempel ke pilar L1-L4 standar HPCS,
    atau custom -- pelatih bikin test/nama target sendiri di luar
    battery standar.
    """
    meso_cycle    = models.ForeignKey(MesoCycle, on_delete=models.CASCADE, related_name='target_performa')
    pilar         = models.CharField(max_length=10, choices=PILAR_CHOICES, default='CUSTOM')
    nama_test     = models.CharField(max_length=150, help_text="mis. '20m Sprint', 'Vertical Jump', atau nama test custom pelatih")
    nilai_target  = models.FloatField(help_text="Nilai target yang mau dicapai")
    satuan        = models.CharField(max_length=20, help_text="mis. 'detik', 'cm', 'kg', 'reps'")
    catatan       = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Target Performa'
        verbose_name_plural = 'Target Performa per Fase'
        ordering            = ['meso_cycle', 'pilar', 'nama_test']

    def __str__(self):
        return f"{self.nama_test}: {self.nilai_target} {self.satuan} ({self.meso_cycle})"


class MicroCycle(models.Model):
    """
    Kontainer 1 minggu latihan di dalam 1 MesoCycle. Isi latihan
    harian ada di SesiLatihan (per hari, 1-7) dan LatihanItem
    (exercise/set/rep di dalam 1 sesi).
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


class SesiLatihan(models.Model):
    """
    Sesi latihan di dalam 1 MicroCycle. Satu hari (hari_ke 1-7) BISA
    punya lebih dari 1 sesi -- dibedakan lewat waktu_sesi (Pagi/Siang/
    Sore/Malam), bukan dipatok 1 sesi/hari. Realitanya kebutuhan ini
    tergantung posisi di periodisasi (mis. mendekati PON biasanya 2x
    sehari, persiapan Kejurda seringnya cukup 1x sore) -- jadi
    pelatih bebas nambah sesi sebanyak yang dia perlu per hari,
    bukan dihardcode berdasar jenis event.

    Pilar fokus per sesi sebaiknya mengikuti prinsip hard-easy
    alternation (hari berat & ringan selang-seling, ala program elite/
    Olimpiade) dan proporsi fokus_l1-l4_persen di MesoCycle induknya --
    tapi field ini tetap manual/fleksibel, pelatih yang menentukan sendiri.
    """
    micro_cycle   = models.ForeignKey(MicroCycle, on_delete=models.CASCADE, related_name='sesi_latihan')
    hari_ke       = models.PositiveSmallIntegerField(help_text="1=Senin ... 7=Minggu")
    waktu_sesi    = models.CharField(max_length=10, choices=WAKTU_SESI_CHOICES, default='SORE', help_text="Buat bedain kalau 1 hari ada lebih dari 1 sesi")
    nama_sesi     = models.CharField(max_length=150, help_text="mis. 'Strength AM', 'Speed & Agility'")
    pilar_fokus   = models.CharField(max_length=10, choices=PILAR_FOKUS_HARIAN_CHOICES, default='REST')
    durasi_menit  = models.PositiveIntegerField(default=0, help_text="Total durasi sesi (menit)")
    intensitas    = models.PositiveIntegerField(default=5, help_text="Skala 1-10")
    catatan       = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Sesi Latihan Harian'
        verbose_name_plural = 'Sesi Latihan Harian'
        ordering            = ['micro_cycle', 'hari_ke', 'waktu_sesi']

    def __str__(self):
        return f"Hari {self.hari_ke} ({self.get_waktu_sesi_display()}) - {self.nama_sesi} ({self.micro_cycle})"

    @property
    def tanggal(self):
        return self.micro_cycle.tanggal_mulai + timedelta(days=self.hari_ke - 1)


class LatihanItem(models.Model):
    """
    1 exercise di dalam 1 SesiLatihan -- level paling detail: set,
    rep, beban/intensitas, dan durasi istirahat antar set.

    Dikelompokkan per kategori (Pemanasan/Latihan Inti/Pendinginan)
    supaya tampilannya mirip format program latihan yang biasa dipakai
    pelatih di spreadsheet -- section per bagian, bukan daftar flat.
    """
    sesi_latihan            = models.ForeignKey(SesiLatihan, on_delete=models.CASCADE, related_name='latihan_items')
    urutan                  = models.PositiveIntegerField(default=1)
    kategori                = models.CharField(max_length=15, choices=KATEGORI_LATIHAN_CHOICES, default='INTI')
    nama_latihan            = models.CharField(max_length=150, help_text="mis. 'Barbell Back Squat'")
    jumlah_set              = models.PositiveIntegerField(default=1)
    jumlah_rep              = models.CharField(max_length=30, blank=True, help_text="mis. '8', '8-12', 'AMRAP'")
    waktu                   = models.CharField(max_length=30, blank=True, help_text="mis. '30 detik', '20+' -- buat latihan berbasis durasi/jarak, terpisah dari jumlah_rep")
    beban_intensitas        = models.CharField(max_length=50, blank=True, help_text="mis. '70% 1RM', 'RPE 7', '20kg'")
    durasi_istirahat_detik  = models.PositiveIntegerField(default=60, help_text="Istirahat antar set (detik)")
    link_video               = models.URLField(blank=True, help_text="Link video contoh gerakan (opsional)")
    catatan                  = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Item Latihan (Exercise)'
        verbose_name_plural = 'Item Latihan (Exercise)'
        ordering            = ['sesi_latihan', 'urutan']

    def __str__(self):
        return f"{self.nama_latihan} - {self.jumlah_set}x{self.jumlah_rep} ({self.sesi_latihan})"