from django.urls import resolve, Resolver404
from django.shortcuts import redirect

EXEMPT_URL_NAMES = {'login', 'logout', 'combat:daftar_coach', 'combat:tunggu_approval'}


class ApprovalRequiredMiddleware:
    """
    Mencegah pelatih yang belum di-approve admin mengakses halaman
    manapun selain login/logout/registrasi/halaman tunggu approval,
    walau sesi login-nya sudah valid.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and not (user.is_superuser or user.is_staff):
            try:
                match = resolve(request.path_info)
                url_name = f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name
            except Resolver404:
                url_name = None

            if url_name not in EXEMPT_URL_NAMES:
                profil = getattr(user, 'profil_pelatih', None)
                if profil and not profil.is_approved:
                    return redirect('combat:tunggu_approval')

        return self.get_response(request)
