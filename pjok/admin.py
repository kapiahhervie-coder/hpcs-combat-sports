from django.contrib import admin

from .models import (
    GuruProfile,
    InstrumenTKJI,
    KategoriAktivitas,
    MateriFase,
    PenilaianFisik,
    PenilaianKarakter,
    PenilaianTeknik,
    Siswa,
)


@admin.register(GuruProfile)
class GuruProfileAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'sekolah', 'fase', 'jenjang', 'tanggal_bergabung')
    list_filter = ('fase',)
    search_fields = ('nama_lengkap', 'sekolah', 'nip')


@admin.register(Siswa)
class SiswaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kelas', 'jenis_kelamin', 'guru')
    list_filter = ('guru__fase', 'kelas')
    search_fields = ('nama',)


@admin.register(KategoriAktivitas)
class KategoriAktivitasAdmin(admin.ModelAdmin):
    list_display = ('kode',)


@admin.register(MateriFase)
class MateriFaseAdmin(admin.ModelAdmin):
    list_display = ('nama_materi', 'fase', 'kategori')
    list_filter = ('fase', 'kategori')
    search_fields = ('nama_materi',)


@admin.register(PenilaianTeknik)
class PenilaianTeknikAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'materi', 'skor', 'tanggal')
    list_filter = ('materi__fase',)


@admin.register(InstrumenTKJI)
class InstrumenTKJIAdmin(admin.ModelAdmin):
    list_display = ('fase', 'jenis_kelamin', 'lari_jarak_pendek_m', 'lari_jarak_menengah_m')
    list_filter = ('fase',)


@admin.register(PenilaianFisik)
class PenilaianFisikAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'tanggal_tes', 'skor_l1', 'skor_l2', 'skor_l3', 'skor_l4')
    readonly_fields = ('skor_l1', 'skor_l2', 'skor_l3', 'skor_l4')


@admin.register(PenilaianKarakter)
class PenilaianKarakterAdmin(admin.ModelAdmin):
    list_display = ('siswa', 'aspek', 'skor', 'tanggal')
    list_filter = ('aspek',)
