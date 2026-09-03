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
    # TODO: uncomment 2 baris ini setelah KondisiKesehatan & CatatanCedera
    # selesai ditambahkan ke pjok/models.py
    # KondisiKesehatan,
    # CatatanCedera,
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


# ══════════════════════════════════════════════════════════════════
# BELUM AKTIF -- nunggu model KondisiKesehatan & CatatanCedera
# selesai ditambahkan ke pjok/models.py. Setelah itu, uncomment
# import di atas DAN 2 blok admin di bawah ini.
# ══════════════════════════════════════════════════════════════════

# @admin.register(KondisiKesehatan)
# class KondisiKesehatanAdmin(admin.ModelAdmin):
#     list_display = ('siswa', 'tingkat_risiko', 'perlu_perhatian', 'diperbarui_pada')
#     list_filter = ('tingkat_risiko',)
#     search_fields = ('siswa__nama',)
#
#     @admin.display(boolean=True, description='Perlu Perhatian')
#     def perlu_perhatian(self, obj):
#         return obj.perlu_perhatian


# @admin.register(CatatanCedera)
# class CatatanCederaAdmin(admin.ModelAdmin):
#     list_display = ('siswa', 'jenis_cedera', 'tanggal_kejadian', 'status')
#     list_filter = ('status',)
#     search_fields = ('siswa__nama', 'jenis_cedera')
