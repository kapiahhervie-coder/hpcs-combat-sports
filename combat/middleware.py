from django.contrib import messages
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
                if profil and profil.status == 'rejected':
                    return redirect('combat:tunggu_approval')

        return self.get_response(request)


# nilai ProfilPelatih.cabang  ->  namespace URL cabornya
CABANG_NAMESPACE = {
    'boxing': 'boxing',
    'muaythai': 'muaythai',
    'tkd': 'taekwondo',
    'krt': 'karate',
    'sepakbola': 'sepakbola',
    'basketball': 'basketball',
}
CABOR_NAMESPACES = set(CABANG_NAMESPACE.values())


class CaborAccessMiddleware:
    """
    Pelatih (bukan superuser/staff) hanya boleh membuka halaman cabor yang
    dipilihnya. Mengetik URL cabor lain langsung dialihkan ke dashboard
    cabornya sendiri.

    - Cabang dikenal -> hanya namespace cabor itu yang boleh.
    - Punya profil, cabang belum punya dashboard atau kosong -> semua halaman
      cabor ditutup; diarahkan ke combat:dashboard yang menampilkan halaman
      "cabang belum tersedia".
    - Tidak dibatasi: superuser/staff, akun tanpa ProfilPelatih (mis. guru
      PJOK), dan halaman di luar namespace cabor (login, combat:*, pjok:*).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and not (user.is_superuser or user.is_staff):
            profil = getattr(user, 'profil_pelatih', None)
            if profil:
                own = CABANG_NAMESPACE.get(profil.cabang or '')
                try:
                    ns = (resolve(request.path_info).namespace or '').split(':')[0]
                except Resolver404:
                    ns = ''
                if ns in CABOR_NAMESPACES and ns != own:
                    messages.warning(request, 'Anda hanya dapat mengakses cabang olahraga yang Anda pilih.', fail_silently=True)
                    return redirect(f'{own}:dashboard' if own else 'combat:dashboard')
        return self.get_response(request)