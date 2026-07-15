from django.urls import path
from . import views

app_name = 'muaythai'

urlpatterns = [
    path('dashboard/', views.DashboardMuayThaiView.as_view(), name='dashboard'),
    path('daftar-atlet/', views.DaftarAtletMuayThaiView.as_view(), name='daftar_atlet'),

    # Audit L1-L4 khusus Muay Thai
    path('l1-correction/', views.L1CorrectionMTView.as_view(), name='l1_correction'),
    path('l1-correction/hapus/<int:pk>/', views.hapus_l1_mt, name='hapus_l1_audit'),
    path('l1-correction/detail/<int:pk>/', views.detail_l1_mt, name='detail_l1_audit'),

    path('l2-strength/', views.L2StrengthMTView.as_view(), name='l2_strength'),
    path('l2-strength/hapus/<int:pk>/', views.hapus_l2_mt, name='hapus_l2_audit'),
    path('l2-strength/detail/<int:pk>/', views.detail_l2_mt, name='detail_l2_audit'),

    path('l3-power/', views.L3PowerMTView.as_view(), name='l3_power'),
    path('l3-power/hapus/<int:pk>/', views.hapus_l3_mt, name='hapus_l3_audit'),
    path('l3-power/detail/<int:pk>/', views.detail_l3_mt, name='detail_l3_audit'),

    path('l4-speed-agility/', views.L4SpeedAgilityMTView.as_view(), name='l4_speed_agility'),
    path('l4-speed-agility/hapus/<int:pk>/', views.hapus_l4_mt, name='hapus_l4_audit'),
    path('l4-speed-agility/detail/<int:pk>/', views.detail_l4_mt, name='detail_l4_audit'),

    path('report-card/<int:atlet_id>/', views.ReportCardMTView.as_view(), name='report_card'),
]
