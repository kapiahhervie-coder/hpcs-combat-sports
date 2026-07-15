"""
patch_admin_l4.py
Menambahkan class SpeedAgilityAuditL4Admin ke combat/admin.py,
supaya L4 muncul di Django Admin (sebelumnya belum terdaftar).
Aman dijalankan berkali-kali (idempotent).
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('combat', 'admin.py')

MARKER = """# ══════════════════════════════════════════════════════════════════════
# REKOMENDASI PROGRAM
# ══════════════════════════════════════════════════════════════════════"""

L4_ADMIN_CLASS = '''@admin.register(SpeedAgilityAuditL4)
class SpeedAgilityAuditL4Admin(admin.ModelAdmin):
    list_display  = [
        'get_atlet_nama', 'get_atlet_gender', 'get_atlet_bb',
        'score_hex', 'score_punch', 'score_yoyo',
        'get_total', 'get_predikat', 'get_layak', 'timestamp',
    ]
    list_filter   = ['predikat', 'layak_kompetisi', 'kondisi_uji']
    search_fields = ['atlet__nama_atlet', 'atlet_name']
    ordering      = ['-timestamp']
    readonly_fields = [
        'hex_waktu_rata', 'yoyo_vo2max_estimasi', 'total_skor', 'predikat',
        'layak_kompetisi', 'layak_bertahan', 'rekomendasi_auto', 'alasan_tidak_layak',
    ]

    fields = [
        'atlet',
        'hex_waktu_putaran1', 'hex_waktu_putaran2', 'hex_waktu_putaran3',
        'hex_waktu_rata', 'score_hex',
        'punch_freq_10s', 'punch_postur_ok', 'punch_reaction_time_ms', 'score_punch',
        'yoyo_level_tercapai', 'yoyo_shuttle_tercapai', 'yoyo_total_jarak_m',
        'yoyo_vo2max_estimasi', 'score_yoyo',
        'kondisi_uji', 'catatan',
        'total_skor', 'predikat', 'layak_kompetisi', 'layak_bertahan',
        'rekomendasi_auto', 'alasan_tidak_layak',
    ]

    def get_atlet_nama(self, obj):
        return obj.atlet.nama_atlet if obj.atlet else obj.atlet_name
    get_atlet_nama.short_description = 'Nama Atlet'

    def get_atlet_gender(self, obj):
        return obj.atlet.gender if obj.atlet else '\\u2014'
    get_atlet_gender.short_description = 'Gender'

    def get_atlet_bb(self, obj):
        return f"{obj.atlet.kelas_berat} kg" if obj.atlet else '\\u2014'
    get_atlet_bb.short_description = 'BB'

    def get_total(self, obj):
        c = '#34d399' if obj.total_skor >= 9 else ('#60a5fa' if obj.total_skor >= 7 else ('#fbbf24' if obj.total_skor >= 5 else '#f87171'))
        return format_html('<strong style="color:{};">{}</strong>', c, obj.total_skor)
    get_total.short_description = 'Total'

    def get_predikat(self, obj):
        return badge_predikat(obj.predikat)
    get_predikat.short_description = 'Predikat'

    def get_layak(self, obj):
        return badge_layak(obj.layak_kompetisi)
    get_layak.short_description = 'Layak Kompetisi?'

    def save_model(self, request, obj, form, change):
        if obj.atlet:
            obj.atlet_name    = obj.atlet.nama_atlet
            obj.gender        = obj.atlet.gender
            obj.kelas_berat   = obj.atlet.kelas_berat
            obj.kategori_usia = obj.atlet.kategori_umur
        super().save_model(request, obj, form, change)


''' + MARKER


def main():
    if not os.path.exists(FILEPATH):
        print(f"File tidak ditemukan: {FILEPATH}")
        return

    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    if "class SpeedAgilityAuditL4Admin" in content:
        print("Sudah ada -- SpeedAgilityAuditL4Admin sudah terdaftar sebelumnya. Tidak ada perubahan.")
        return

    count = content.count(MARKER)
    if count != 1:
        print(f"Peringatan: marker 'REKOMENDASI PROGRAM' ditemukan {count}x (perlu tepat 1x). Dibatalkan.")
        return

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = FILEPATH + f'.backup-{timestamp}'
    shutil.copy2(FILEPATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    content = content.replace(MARKER, L4_ADMIN_CLASS, 1)

    with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print("Berhasil menambahkan SpeedAgilityAuditL4Admin ke combat/admin.py")
    print("Jalankan 'python manage.py check' untuk verifikasi.")


if __name__ == '__main__':
    main()
