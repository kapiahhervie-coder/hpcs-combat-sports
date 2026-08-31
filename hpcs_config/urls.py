from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('combat/', include('combat.urls')),
    path('combat/muaythai/', include('muaythai.urls', namespace='muaythai')),
    path('combat/boxing/', include('boxing.urls', namespace='boxing')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('',lambda request: redirect('combat:dashboard')),
    path('taekwondo/', include('taekwondo.urls')),
    path('karate/', include('karate.urls')),
    path('pjok/', include('pjok.urls')),
    path('periodization/', include('periodization.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
