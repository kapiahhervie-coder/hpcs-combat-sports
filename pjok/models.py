"""
App: pjok
Modul penilaian PJOK / Physical Education — terpisah dari app combat (HPCS Combat Sports).

Struktur mengikuti Capaian Pembelajaran (CP) PJOK Kurikulum Merdeka
(Kepmendikbud 033/H/KR/2022), dengan 4 elemen resmi:
  1. Keterampilan Gerak   -> PenilaianTeknik
  2. Pengetahuan Gerak    -> (opsional, bisa ditambah PenilaianPengetahuan)
  3. Pemanfaatan Gerak    -> PenilaianFisik (L1-L4, diadaptasi dari TKJI)
  4. Pengembangan Karakter -> PenilaianKarakter

Filosofi: nilai teknik/skill (Elemen 1) dihubungkan dengan komponen fisik dasar
(Elemen 3 / L1-L4) untuk membantu guru menemukan akar masalah perkembangan siswa,
bukan sekadar memberi angka tanpa konteks.
"""

from django.contrib.auth.models import User
from django.db import models

from .diagnostik import hitung_skor_l1, hitung_skor_l2, hitung_skor_l3, hitung_skor_l4


FASE_CHOICES = [
    ('A', 'Fase A (Kelas 1-2 SD)'),
    ('B', 'Fase B (Kelas 3-4 SD)'),
    ('C', 'Fase C (Kelas 5-6 SD)'),
    ('D', 'Fase D (Kelas 7-9 SMP)'),
    ('E', 'Fase E (Kelas 10 SMA)'),
    ('F', 'Fase F (Kelas 11-12 SMA)'),
]

JENJANG_PER_FASE = {
    'A': 'SD', 'B': 'SD', 'C': 'SD',
    'D': 'SMP',
    'E': 'SMA', 'F': 'SMA',
}

# 4 tingkat pencapaian sesuai Rubrik Penilaian PJOK Kurikulum Merdeka
TINGKAT_CHOICES = [
    (1, 'Perlu Bimbingan'),
    (2, 'Cukup'),
    (3, 'Baik'),
    (4, 'Sangat Baik'),
]
TINGKAT_KE_SKOR = {1: 25, 2: 50, 3: 75, 4: 100}


class GuruProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama_lengkap = models.CharField(max_length=100)
    sekolah = models.CharField(max_length=100)
    fase = models.CharField(max_length=1, choices=FASE_CHOICES)
    nip = models.CharField(max_length=30, blank=True)
    tanggal_bergabung = models.DateTimeField(auto_now_add=True)

    @property
    def jenjang(self):
        """Diturunkan otomatis dari fase — tidak perlu diinput manual."""
        return JENJANG_PER_FASE.get(self.fase, '')

    def __str__(self):
        return f"{self.nama_lengkap} - {self.sekolah} (Fase {self.fase})"


class Siswa(models.Model):
    L_P = [('L', 'Laki-laki'), ('P', 'Perempuan')]

    guru = models.ForeignKey(GuruProfile, on_delete=models.CASCADE, related_name='siswa')
    fase = models.CharField(max_length=1, choices=FASE_CHOICES, null=True, blank=True)
    nama = models.CharField(max_length=100)
    kelas = models.CharField(max_length=20)
    jenis_kelamin = models.CharField(max_length=1, choices=L_P)
    tanggal_lahir = models.DateField()

    def __str__(self):
        return f"{self.nama} ({self.kelas})"


# ---------------------------------------------------------------------------
# Elemen 1: Keterampilan Gerak — materi mengikuti ATP resmi per fase
# ---------------------------------------------------------------------------

class KategoriAktivitas(models.Model):
    """5 kategori resmi CP PJOK — data referensi, sama untuk semua fase."""
    KATEGORI_CHOICES = [
        ('permainan_olahraga', 'Permainan dan Olahraga'),
        ('senam', 'Aktivitas Senam'),
        ('gerak_berirama', 'Aktivitas Gerak Berirama'),
        ('air', 'Aktivitas Permainan dan Olahraga Air'),
        ('kebugaran', 'Aktivitas Kebugaran Jasmani'),
    ]
    kode = models.CharField(max_length=30, choices=KATEGORI_CHOICES, unique=True)

    def __str__(self):
        return self.get_kode_display()


class MateriFase(models.Model):
    """Materi spesifik per fase, diisi guru sesuai ATP sekolahnya masing-masing."""
    fase = models.CharField(max_length=1, choices=FASE_CHOICES)
    kategori = models.ForeignKey(KategoriAktivitas, on_delete=models.CASCADE, related_name='materi')
    nama_materi = models.CharField(max_length=100)  # mis. "Sepak Bola - Teknik Dribbling"
    deskripsi_cp = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.fase}] {self.nama_materi}"


class PenilaianTeknik(models.Model):
    """Elemen Keterampilan Gerak."""
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='penilaian_teknik')
    materi = models.ForeignKey(MateriFase, on_delete=models.CASCADE, related_name='penilaian_teknik')
    tingkat = models.IntegerField(choices=TINGKAT_CHOICES, null=True, blank=True)
    skor = models.FloatField(editable=False, null=True, blank=True)
    catatan = models.TextField(blank=True)
    tanggal = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.tingkat:
            self.skor = TINGKAT_KE_SKOR.get(self.tingkat)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.siswa.nama} - {self.materi.nama_materi}: {self.skor}"


class PenilaianPengetahuan(models.Model):
    """Elemen Pengetahuan Gerak — pemahaman prosedur pola gerak dasar."""
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='penilaian_pengetahuan')
    tingkat = models.IntegerField(choices=TINGKAT_CHOICES)
    skor = models.FloatField(editable=False, null=True, blank=True)
    catatan = models.TextField(blank=True)
    tanggal = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.tingkat:
            self.skor = TINGKAT_KE_SKOR.get(self.tingkat)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.siswa.nama} - Pengetahuan Gerak: {self.skor}"


# ---------------------------------------------------------------------------
# Elemen 3: Pemanfaatan Gerak — diagnostik fisik L1-L4 (diadaptasi dari TKJI)
# ---------------------------------------------------------------------------

class InstrumenTKJI(models.Model):
    """Instrumen tes resmi per fase & jenis kelamin — data referensi (di-seed sekali)."""
    fase = models.CharField(max_length=1, choices=FASE_CHOICES)
    jenis_kelamin = models.CharField(max_length=1, choices=Siswa.L_P)

    lari_jarak_pendek_m = models.IntegerField(default=50)
    gantung_durasi_detik = models.IntegerField(help_text="Gantung siku tekuk / gantung angkat tubuh")
    sit_up_durasi_detik = models.IntegerField(default=60)
    lari_jarak_menengah_m = models.IntegerField(help_text="600 / 1000 / 1200 tergantung fase")

    class Meta:
        unique_together = ('fase', 'jenis_kelamin')

    def __str__(self):
        return f"TKJI Fase {self.fase} - {self.get_jenis_kelamin_display()}"


class PenilaianFisik(models.Model):
    """
    Elemen Pemanfaatan Gerak — L1-L4, mirip filosofi diagnostik combat sports.
    Skor per level dihitung otomatis dari data mentah lewat helper (lihat diagnostik.py).
    """
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='penilaian_fisik')
    tanggal_tes = models.DateField(auto_now_add=True)

    # L1 - Core & Mobility
    plank_hold_detik = models.FloatField(help_text="Durasi plank (detik)")
    sit_and_reach_cm = models.FloatField(help_text="Fleksibilitas (cm)")

    # L2 - Strength (berbasis TKJI: gantung siku tekuk + sit up)
    gantung_durasi_tercapai_detik = models.FloatField()
    sit_up_repetisi = models.IntegerField()

    # L3 - Power (berbasis TKJI: loncat tegak)
    vertical_jump_cm = models.FloatField()
    standing_broad_jump_cm = models.FloatField(blank=True, null=True)

    # L4 - Speed & Agility (berbasis TKJI: lari cepat + lari jarak menengah)
    lari_cepat_detik = models.FloatField(help_text="Waktu tempuh lari jarak pendek TKJI")
    lari_menengah_detik = models.FloatField(help_text="Waktu tempuh lari jarak menengah TKJI")

    # Skor turunan per level — dihitung otomatis, jangan diisi manual
    skor_l1 = models.FloatField(editable=False, null=True, blank=True)
    skor_l2 = models.FloatField(editable=False, null=True, blank=True)
    skor_l3 = models.FloatField(editable=False, null=True, blank=True)
    skor_l4 = models.FloatField(editable=False, null=True, blank=True)

    def __str__(self):
        return f"{self.siswa.nama} - Tes Fisik {self.tanggal_tes}"

    def save(self, *args, **kwargs):
        """
        Hitung skor_l1-l4 otomatis dari data mentah sebelum disimpan.
        Referensi norma saat ini pakai nilai default generik di diagnostik.py
        (belum tabel norma resmi TKJI per fase/usia — lihat README).
        """
        referensi = {}  # nanti bisa diisi dari InstrumenTKJI sesuai fase & jenis kelamin siswa

        self.skor_l1 = hitung_skor_l1(self.plank_hold_detik, self.sit_and_reach_cm, referensi)
        self.skor_l2 = hitung_skor_l2(self.gantung_durasi_tercapai_detik, self.sit_up_repetisi, referensi)
        self.skor_l3 = hitung_skor_l3(self.vertical_jump_cm, referensi)
        self.skor_l4 = hitung_skor_l4(self.lari_cepat_detik, self.lari_menengah_detik, referensi)

        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Elemen 4: Pengembangan Karakter
# ---------------------------------------------------------------------------

class PenilaianKarakter(models.Model):
    ASPEK_CHOICES = [
        ('sportivitas', 'Sportivitas'),
        ('kerjasama', 'Kerja Sama'),
        ('disiplin', 'Disiplin'),
        ('tanggung_jawab', 'Tanggung Jawab'),
        ('percaya_diri', 'Percaya Diri'),
    ]
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='penilaian_karakter')
    aspek = models.CharField(max_length=30, choices=ASPEK_CHOICES)
    tingkat = models.IntegerField(choices=TINGKAT_CHOICES, null=True, blank=True)
    skor = models.FloatField(editable=False, null=True, blank=True)
    catatan = models.TextField(blank=True)
    tanggal = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.tingkat:
            self.skor = TINGKAT_KE_SKOR.get(self.tingkat)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.siswa.nama} - {self.get_aspek_display()}: {self.skor}"


# ---------------------------------------------------------------------------
# Absensi — per sesi pertemuan, mencatat kehadiran semua siswa sekaligus
# ---------------------------------------------------------------------------

class SesiAbsensi(models.Model):
    """Satu kali pertemuan/sesi pelajaran untuk satu fase pada tanggal tertentu."""
    guru = models.ForeignKey(GuruProfile, on_delete=models.CASCADE, related_name='sesi_absensi')
    fase = models.CharField(max_length=1, choices=FASE_CHOICES)
    tanggal = models.DateField()
    catatan_sesi = models.CharField(max_length=200, blank=True, help_text="Contoh: Materi lari zig-zag")
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('guru', 'fase', 'tanggal')
        ordering = ['-tanggal']

    def __str__(self):
        return f"Absensi Fase {self.fase} - {self.tanggal}"


class Absensi(models.Model):
    STATUS_CHOICES = [
        ('H', 'Hadir'),
        ('I', 'Izin'),
        ('S', 'Sakit'),
        ('A', 'Alpa'),
    ]
    sesi = models.ForeignKey(SesiAbsensi, on_delete=models.CASCADE, related_name='daftar_absensi')
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name='absensi')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='H')
    keterangan = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('sesi', 'siswa')

    def __str__(self):
        return f"{self.siswa.nama} - {self.get_status_display()} ({self.sesi.tanggal})"

# ---------------------------------------------------------------------------
# Prota & Prosem — rencana materi mingguan, dipakai untuk generate dokumen
# ---------------------------------------------------------------------------

class RencanaMingguan(models.Model):
    SEMESTER_CHOICES = [
        ('ganjil', 'Ganjil'),
        ('genap', 'Genap'),
    ]
    guru = models.ForeignKey(GuruProfile, on_delete=models.CASCADE, related_name='rencana_mingguan')
    fase = models.CharField(max_length=1, choices=FASE_CHOICES)
    tahun_ajaran = models.CharField(max_length=9, help_text="Contoh: 2026/2027")
    semester = models.CharField(max_length=6, choices=SEMESTER_CHOICES)
    minggu_ke = models.PositiveSmallIntegerField()
    materi = models.ForeignKey(MateriFase, on_delete=models.SET_NULL, null=True, blank=True, related_name='rencana_mingguan')
    nama_materi_bebas = models.CharField(max_length=150, blank=True, help_text="Isi kalau materi belum ada di daftar Materi Fase")
    tp = models.ForeignKey('TujuanPembelajaran', on_delete=models.SET_NULL, null=True, blank=True, related_name='rencana_mingguan')
    alokasi_jp = models.PositiveSmallIntegerField(default=2, help_text="Jumlah jam pelajaran")
    keterangan = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('guru', 'fase', 'tahun_ajaran', 'semester', 'minggu_ke')
        ordering = ['tahun_ajaran', 'semester', 'minggu_ke']

    @property
    def nama_tampil(self):
        if self.materi:
            return self.materi.nama_materi
        return self.nama_materi_bebas or '(belum diisi)'

    def __str__(self):
        return f"Fase {self.fase} - {self.tahun_ajaran} {self.semester} - Minggu {self.minggu_ke}"

# ---------------------------------------------------------------------------
# TP, ATP, KKTP — Tujuan Pembelajaran per elemen CP, dasar Alur Tujuan Pembelajaran
# ---------------------------------------------------------------------------

class TujuanPembelajaran(models.Model):
    ELEMEN_CHOICES = [
        ('keterampilan_gerak', 'Keterampilan Gerak'),
        ('pengetahuan_gerak', 'Pengetahuan Gerak'),
        ('pemanfaatan_gerak', 'Pemanfaatan Gerak'),
        ('pengembangan_karakter', 'Pengembangan Karakter'),
    ]
    guru = models.ForeignKey(GuruProfile, on_delete=models.CASCADE, related_name='tujuan_pembelajaran')
    fase = models.CharField(max_length=1, choices=FASE_CHOICES)
    kode = models.CharField(max_length=20, help_text="Contoh: TP.1.1")
    elemen = models.CharField(max_length=30, choices=ELEMEN_CHOICES)
    deskripsi = models.TextField(help_text="Rumusan Tujuan Pembelajaran")
    kktp = models.TextField(blank=True, help_text="Kriteria Ketercapaian Tujuan Pembelajaran")

    class Meta:
        ordering = ['elemen', 'kode']
        unique_together = ('guru', 'fase', 'kode')

    def get_elemen_display_short(self):
        return dict(self.ELEMEN_CHOICES).get(self.elemen, self.elemen)

    def __str__(self):
        return f"{self.kode} - {self.deskripsi[:50]}"