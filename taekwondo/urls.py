from django.urls import path
from . import views

app_name = 'taekwondo'

urlpatterns = [
    path('dashboard/', views.DashboardTaekwondoView.as_view(), name='dashboard'),
    path('daftar-atlet/', views.DaftarAtletTaekwondoView.as_view(), name='daftar_atlet'),

    # Audit L1-L4 khusus Taekwondo (L1 custom, L2-L4 shared dari combat)
    path('l1-correction/', views.L1CorrectionTKDView.as_view(), name='l1_correction'),
    path('l1-correction/hapus/<int:pk>/', views.hapus_l1_tkd, name='hapus_l1_audit'),
    path('l1-correction/detail/<int:pk>/', views.detail_l1_tkd, name='detail_l1_audit'),

    path('l2-strength/', views.L2StrengthTKDView.as_view(), name='l2_strength'),
    path('l2-strength/hapus/<int:pk>/', views.hapus_l2_tkd, name='hapus_l2_audit'),
    path('l2-strength/detail/<int:pk>/', views.detail_l2_tkd, name='detail_l2_audit'),

    path('l3-power/', views.L3PowerTKDView.as_view(), name='l3_power'),
    path('l3-power/hapus/<int:pk>/', views.hapus_l3_tkd, name='hapus_l3_audit'),
    path('l3-power/detail/<int:pk>/', views.detail_l3_tkd, name='detail_l3_audit'),

    path('l4-speed-agility/', views.L4SpeedAgilityTKDView.as_view(), name='l4_speed_agility'),
    path('l4-speed-agility/hapus/<int:pk>/', views.hapus_l4_tkd, name='hapus_l4_audit'),
    path('l4-speed-agility/detail/<int:pk>/', views.detail_l4_tkd, name='detail_l4_audit'),

    path('report-card/<int:atlet_id>/', views.ReportCardTKDView.as_view(), name='report_card'),
]
