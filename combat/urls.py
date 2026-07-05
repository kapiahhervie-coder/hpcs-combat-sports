from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'combat'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard_combat/', views.DashboardView.as_view(), name='dashboard_combat'),

    # Boxing — redirect ke app boxing yang baru (backward compat)
    path('dashboard_boxing/', lambda r: redirect('boxing:dashboard'), name='dashboard_boxing'),
    path('l1-correction/', lambda r: redirect('boxing:l1_correction'), name='l1_correction'),
    path('l1-correction/hapus/<int:pk>/', lambda r, pk: redirect('boxing:hapus_l1_audit', pk=pk), name='hapus_l1_audit'),
    path('l1-correction/detail/<int:pk>/', lambda r, pk: redirect('boxing:detail_l1_audit', pk=pk), name='detail_l1_audit'),
    path('l2-strength/', lambda r: redirect('boxing:l2_strength'), name='l2_strength'),
    path('l2-strength/hapus/<int:pk>/', lambda r, pk: redirect('boxing:hapus_l2_audit', pk=pk), name='hapus_l2_audit'),
    path('l2-strength/detail/<int:pk>/', lambda r, pk: redirect('boxing:detail_l2_audit', pk=pk), name='detail_l2_audit'),
    path('l3-power/', lambda r: redirect('boxing:l3_power'), name='l3_power'),
    path('l3-power/hapus/<int:pk>/', lambda r, pk: redirect('boxing:hapus_l3_audit', pk=pk), name='hapus_l3_audit'),
    path('l3-power/detail/<int:pk>/', lambda r, pk: redirect('boxing:detail_l3_audit', pk=pk), name='detail_l3_audit'),
    path('l4-speed-agility/', lambda r: redirect('boxing:l4_speed_agility'), name='l4_speed_agility'),
    path('l4-speed-agility/hapus/<int:pk>/', lambda r, pk: redirect('boxing:hapus_l4_audit', pk=pk), name='hapus_l4_audit'),
    path('l4-speed-agility/detail/<int:pk>/', lambda r, pk: redirect('boxing:detail_l4_audit', pk=pk), name='detail_l4_audit'),

    # Muay Thai — redirect ke app muaythai yang baru (backward compat)
    path('dashboard_muaythai/', lambda r: redirect('muaythai:dashboard'), name='dashboard_muaythai'),

    path('daftar-coach/', views.DaftarCoachView.as_view(), name='daftar_coach'),
    path('tunggu-approval/', views.TungguApprovalView.as_view(), name='tunggu_approval'),
    path('admin-coach/', views.AdminCoachView.as_view(), name='admin_coach'),
    path('admin-coach/assign/', views.AssignAtletCoachView.as_view(), name='assign_atlet_coach'),
    path('tambah-atlet/', views.TambahAtletView.as_view(), name='tambah_atlet'),

    path('report-card/<int:atlet_id>/', views.ReportCardView.as_view(), name='report_card'),
    path('report-center/', views.ReportCenterView.as_view(), name='report_center'),
]
