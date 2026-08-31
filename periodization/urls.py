from django.urls import path
from . import views

app_name = 'periodization'

urlpatterns = [
    path('', views.DaftarMacroProgramView.as_view(), name='daftar_program'),
    path('tambah/', views.TambahMacroProgramView.as_view(), name='tambah_program'),
    path('<int:program_id>/', views.DetailMacroProgramView.as_view(), name='detail_program'),
    path('<int:program_id>/generate-otomatis/', views.GenerateOtomatisView.as_view(), name='generate_otomatis'),
    path('<int:program_id>/kurva-data.json', views.KurvaVolumeIntensitasView.as_view(), name='kurva_data'),
]