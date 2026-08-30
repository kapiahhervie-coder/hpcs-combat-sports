from django.urls import path

from . import views

app_name = 'pjok'

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('buat-profile/', views.buat_profile, name='buat_profile'),
    path('dashboard/<str:fase>/', views.dashboard_fase, name='dashboard_fase'),
    path('tambah-siswa/', views.tambah_siswa, name='tambah_siswa'),
    path('siswa/<int:siswa_id>/', views.detail_siswa, name='detail_siswa'),
    path('siswa/<int:siswa_id>/edit/', views.edit_siswa, name='edit_siswa'),
    path('absensi/<str:fase>/', views.daftar_absensi, name='daftar_absensi'),
    path('absensi/<str:fase>/ambil/', views.ambil_absensi, name='ambil_absensi'),
    path('absensi/<str:fase>/rekap/', views.rekap_absensi, name='rekap_absensi'),
    path('rencana/<str:fase>/', views.rencana_mingguan, name='rencana_mingguan'),
    path('rencana/<str:fase>/export-prosem/', views.export_prosem, name='export_prosem'),
    path('rencana/<str:fase>/export-prota/', views.export_prota, name='export_prota'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),
    path('rencana/<str:fase>/export-prosem/', views.export_prosem, name='export_prosem'),
    path('rencana/<str:fase>/export-prota/', views.export_prota, name='export_prota'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),
    path('siswa/<int:siswa_id>/edit/', views.edit_siswa, name='edit_siswa'),
    path('absensi/<str:fase>/', views.daftar_absensi, name='daftar_absensi'),
    path('absensi/<str:fase>/ambil/', views.ambil_absensi, name='ambil_absensi'),
    path('absensi/<str:fase>/rekap/', views.rekap_absensi, name='rekap_absensi'),
    path('rencana/<str:fase>/', views.rencana_mingguan, name='rencana_mingguan'),
    path('rencana/<str:fase>/export-prosem/', views.export_prosem, name='export_prosem'),
    path('rencana/<str:fase>/export-prota/', views.export_prota, name='export_prota'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),
    path('rencana/<str:fase>/export-prosem/', views.export_prosem, name='export_prosem'),
    path('rencana/<str:fase>/export-prota/', views.export_prota, name='export_prota'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),
    path('tp/<str:fase>/', views.daftar_tp, name='daftar_tp'),
    path('siswa/<int:siswa_id>/tambah-fisik/', views.tambah_penilaian_fisik, name='tambah_penilaian_fisik'),
    path('siswa/<int:siswa_id>/tambah-teknik/', views.tambah_penilaian_teknik, name='tambah_penilaian_teknik'),
    path('siswa/<int:siswa_id>/tambah-karakter/', views.tambah_penilaian_karakter, name='tambah_penilaian_karakter'),
    path('siswa/<int:siswa_id>/tambah-pengetahuan/', views.tambah_penilaian_pengetahuan, name='tambah_penilaian_pengetahuan'),
]
