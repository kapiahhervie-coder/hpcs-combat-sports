from django.urls import path

from . import views

app_name = 'pjok'

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('buat-profile/', views.buat_profile, name='buat_profile'),
    path('dashboard/<str:fase>/', views.dashboard_fase, name='dashboard_fase'),
    path('tambah-siswa/', views.tambah_siswa, name='tambah_siswa'),
    path('import-siswa/template/', views.download_template_csv, name='download_template_csv'),
    path('import-siswa/<str:fase>/', views.import_siswa, name='import_siswa'),
    path('siswa/<int:siswa_id>/', views.detail_siswa, name='detail_siswa'),
    path('lembar-kosong/<str:fase>/', views.export_lembar_kosong, name='export_lembar_kosong'),

    # --- Mode Offline (Tes Fisik) ---
    path('offline/<str:fase>/sw.js', views.offline_sw, name='offline_sw'),
    path('offline/<str:fase>/', views.offline_tes_fisik, name='offline_tes_fisik'),
    path('api/sync-tes-fisik/', views.api_sync_tes_fisik, name='api_sync_tes_fisik'),

    # --- Offline Tes Fisik (PWA) ---
    path('offline/<str:fase>/', views.offline_tes_fisik, name='offline_tes_fisik'),
    path('offline/<str:fase>/sw.js', views.offline_sw, name='offline_sw'),
    path('api/sync-tes-fisik/', views.api_sync_tes_fisik, name='api_sync_tes_fisik'),
    path('siswa/<int:siswa_id>/edit/', views.edit_siswa, name='edit_siswa'),
    path('siswa/<int:siswa_id>/pindah-fase/', views.pindah_fase_siswa, name='pindah_fase_siswa'),
    path('absensi/<str:fase>/', views.daftar_absensi, name='daftar_absensi'),
    path('absensi/<str:fase>/ambil/', views.ambil_absensi, name='ambil_absensi'),
    path('absensi/<str:fase>/rekap/', views.rekap_absensi, name='rekap_absensi'),
    path('rencana/<str:fase>/', views.rencana_mingguan, name='rencana_mingguan'),
    path('rencana/<str:fase>/export-prosem/', views.export_prosem, name='export_prosem'),
    path('rencana/<str:fase>/export-prota/', views.export_prota, name='export_prota'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),

    # --- Modul Ajar ---
    path('modul-ajar/<str:fase>/', views.daftar_modul_ajar, name='daftar_modul_ajar'),
    path('modul-ajar/<str:fase>/tambah/', views.tambah_modul_ajar, name='tambah_modul_ajar'),
    path('modul-ajar/<str:fase>/<int:modul_id>/edit/', views.edit_modul_ajar, name='edit_modul_ajar'),
    path('modul-ajar/<str:fase>/<int:modul_id>/hapus/', views.hapus_modul_ajar, name='hapus_modul_ajar'),
    path('modul-ajar/<str:fase>/<int:modul_id>/export/', views.export_modul_ajar, name='export_modul_ajar'),
    path('siswa/<int:siswa_id>/tambah-fisik/', views.tambah_penilaian_fisik, name='tambah_penilaian_fisik'),
    path('siswa/<int:siswa_id>/tambah-teknik/', views.tambah_penilaian_teknik, name='tambah_penilaian_teknik'),
    path('siswa/<int:siswa_id>/tambah-karakter/', views.tambah_penilaian_karakter, name='tambah_penilaian_karakter'),
    path('siswa/<int:siswa_id>/tambah-pengetahuan/', views.tambah_penilaian_pengetahuan, name='tambah_penilaian_pengetahuan'),

    # --- Data Kesehatan Siswa ---
    path('siswa/<int:siswa_id>/kesehatan/', views.data_kesehatan, name='data_kesehatan'),
    path('siswa/<int:siswa_id>/kesehatan/tambah-cedera/', views.tambah_cedera, name='tambah_cedera'),
]