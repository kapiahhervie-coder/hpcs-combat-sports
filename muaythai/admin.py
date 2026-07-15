from django.contrib import admin
from .models import CorrectionAuditL1MT


@admin.register(CorrectionAuditL1MT)
class CorrectionAuditL1MTAdmin(admin.ModelAdmin):
    list_display = ['atlet_name', 'kategori_usia', 'gender', 'total_skor', 'predikat', 'layak_naik', 'timestamp']
    list_filter = ['predikat', 'layak_naik', 'kategori_usia']
    search_fields = ['atlet_name']
    ordering = ['-timestamp']
    readonly_fields = ['total_skor', 'predikat', 'layak_naik', 'alasan_tidak_layak']