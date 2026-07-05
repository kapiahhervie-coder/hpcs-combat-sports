from django.urls import path
from . import views

app_name = 'boxing'

urlpatterns = [
    path('', views.DashboardBoxingView.as_view(), name='dashboard'),

    path('l1-correction/', views.L1CorrectionView.as_view(), name='l1_correction'),
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
]
