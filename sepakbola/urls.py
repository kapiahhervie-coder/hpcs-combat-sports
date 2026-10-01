from django.urls import path
from . import views

app_name = 'sepakbola'

urlpatterns = [
    path('dashboard/', views.DashboardSepakbolaView.as_view(), name='dashboard'),
    path('daftar-atlet/', views.DaftarAtletSBView.as_view(), name='daftar_atlet'),
    path('l1-correction/', views.L1CorrectionSBView.as_view(), name='l1_correction'),
    path('l1-correction/hapus/<int:audit_id>/', views.L1DeleteSBView.as_view(), name='l1_delete'),
    path('l2-strength/', views.L2StrengthSBView.as_view(), name='l2_strength'),
    path('l2-strength/hapus/<int:audit_id>/', views.L2DeleteSBView.as_view(), name='l2_delete'),
    path('l3-power/', views.L3PowerSBView.as_view(), name='l3_power'),
    path('l3-power/hapus/<int:audit_id>/', views.L3DeleteSBView.as_view(), name='l3_delete'),
    path('l4-speed-agility/', views.L4SpeedAgilitySBView.as_view(), name='l4_speed_agility'),
    path('l4-speed-agility/hapus/<int:audit_id>/', views.L4DeleteSBView.as_view(), name='l4_delete'),
]





