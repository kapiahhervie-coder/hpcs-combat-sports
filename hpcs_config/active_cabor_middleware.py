class ActiveCaborMiddleware:
    """
    Menyimpan cabang olahraga terakhir yang diakses ke session,
    supaya sidebar tetap menampilkan menu cabang yang benar walau
    sedang membuka halaman lintas-cabang seperti Periodisasi/Kalkulator.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        ns = getattr(request.resolver_match, 'namespace', None) if request.resolver_match else None
        if ns in ('boxing', 'sepakbola', 'muaythai', 'karate', 'taekwondo'):
            request.session['active_cabor'] = ns
        return None
