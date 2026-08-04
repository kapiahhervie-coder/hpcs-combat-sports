from django.contrib import admin
from .models import CorrectionAuditL1KRT


@admin.register(CorrectionAuditL1KRT)
class CorrectionAuditL1KRTAdmin(admin.ModelAdmin):
    list_display  = ('atlet_name', 'kategori_usia', 'gender', 'total_skor', 'predikat', 'layak_naik', 'timestamp')
    list_filter   = ('kategori_usia', 'gender', 'predikat', 'layak_naik')
    search_fields = ('atlet_name',)
    ordering      = ('-timestamp',)
    readonly_fields = ('total_skor', 'predikat', 'layak_naik', 'alasan_tidak_layak')
