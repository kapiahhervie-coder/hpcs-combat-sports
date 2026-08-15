"""
combat/urls.py — PERBAIKAN

Hanya berisi view yang benar-benar ada di combat/views.py.
Semua path Taekwondo (dashboard, l2, l3, l4, report) SUDAH DIPINDAH
ke taekwondo/urls.py (app terpisah) — JANGAN didefinisikan lagi di sini,
karena `views` di file ini merujuk ke combat/views.py, bukan
taekwondo/views.py. Itulah penyebab AttributeError sebelumnya.

Kalau nanti ada boxing/urls.py, muaythai/urls.py, karate/urls.py
masing-masing sebagai app terpisah, jangan juga didefinisikan di sini —
cukup di-include lewat hpcs_config/urls.py (lihat catatan di bawah file
ini).
"""

from django.urls import path
from . import views

app_name = 'combat'

urlpatterns = [
    # Dashboard utama (combat, bukan per-cabor)
    path('', views.DashboardView.as_view(), name='dashboard'),
   

    # Athlete Intelligence Report (report card baru)
    path('athlete-report/<int:atlet_id>/', views.AthleteIntelligenceReportView.as_view(), name='athlete_report'),

    # Report Card (lama)
    path('report-card/<int:atlet_id>/', views.ReportCardView.as_view(), name='report_card'),

    # Report Center (rekap semua atlet lintas cabor)
    path('report-center/', views.ReportCenterView.as_view(), name='report_center'),

    # Registrasi & approval coach
    path('daftar-coach/', views.DaftarCoachView.as_view(), name='daftar_coach'),
    path('tunggu-approval/', views.TungguApprovalView.as_view(), name='tunggu_approval'),
    path('admin-coach/', views.AdminCoachView.as_view(), name='admin_coach'),
    path('assign-atlet-coach/', views.AssignAtletCoachView.as_view(), name='assign_atlet_coach'),

    # Tambah atlet (oleh coach)
    path('tambah-atlet/', views.TambahAtletView.as_view(), name='tambah_atlet'),
]