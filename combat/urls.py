from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'combat'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard_boxing/', views.DashboardBoxingView.as_view(), name='dashboard_boxing'),
    path('dashboard_combat/', views.DashboardView.as_view(), name='dashboard_combat'),

    # Muay Thai — redirect ke app muaythai yang baru (backward compat)
    path('dashboard_muaythai/', lambda r: redirect('muaythai:dashboard'), name='dashboard_muaythai'),

    path('daftar-coach/', views.DaftarCoachView.as_view(), name='daftar_coach'),
    path('tunggu-approval/', views.TungguApprovalView.as_view(), name='tunggu_approval'),
    path('admin-coach/', views.AdminCoachView.as_view(), name='admin_coach'),
    path('admin-coach/assign/', views.AssignAtletCoachView.as_view(), name='assign_atlet_coach'),
    path('tambah-atlet/', views.TambahAtletView.as_view(), name='tambah_atlet'),

    path('l1-correction/', views.L1CorrectionView.as_view(), name='l1_correction'),
    path('l1-correction/save/', views.L1CorrectionView.as_view(), name='save_l1_audit'),
    path('l1-correction/hapus/<int:pk>/', views.hapus_l1_audit, name='hapus_l1_audit'),
    path('l1-correction/detail/<int:pk>/', views.detail_l1_audit, name='detail_l1_audit'),

    path('l2-strength/', views.L2StrengthView.as_view(), name='l2_strength'),
    path('l2-strength/hapus/<int:pk>/', views.hapus_l2_audit, name='hapus_l2_audit'),
    path('l2-strength/detail/<int:pk>/', views.detail_l2_audit, name='detail_l2_audit'),

    path('l3-power/', views.L3PowerView.as_view(), name='l3_power'),
    path('l3-power/hapus/<int:pk>/', views.hapus_l3_audit, name='hapus_l3_audit'),
    path('l3-power/detail/<int:pk>/', views.detail_l3_audit, name='detail_l3_audit'),

    path('l4-speed-agility/', views.L4SpeedAgilityView.as_view(), name='l4_speed_agility'),
    path('l4-speed-agility/hapus/<int:pk>/', views.hapus_l4_audit, name='hapus_l4_audit'),
    path('l4-speed-agility/detail/<int:pk>/', views.detail_l4_audit, name='detail_l4_audit'),

    path('report-card/<int:atlet_id>/', views.ReportCardView.as_view(), name='report_card'),
    path('report-center/', views.ReportCenterView.as_view(), name='report_center'),
]
