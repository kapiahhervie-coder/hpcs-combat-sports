content = open("combat/views.py", "r", encoding="utf-8").read()

old = """        return render(request, self.template_name, {
            'pending_list':   pending_list,
            'approved_list':  approved_list,
            'rejected_list':  rejected_list,
            'total_pending':  pending_list.count(),
            'total_approved': approved_list.count(),
            'total_rejected': rejected_list.count(),
            'total_semua':    ProfilPelatih.objects.count(),
        })"""

new = """        semua_atlet = Atlet.objects.all().order_by('nama_atlet')
        atlet_bebas = Atlet.objects.filter(pelatih__isnull=True).order_by('nama_atlet')
        return render(request, self.template_name, {
            'pending_list':   pending_list,
            'approved_list':  approved_list,
            'rejected_list':  rejected_list,
            'total_pending':  pending_list.count(),
            'total_approved': approved_list.count(),
            'total_rejected': rejected_list.count(),
            'total_semua':    ProfilPelatih.objects.count(),
            'semua_atlet':    semua_atlet,
            'atlet_bebas':    atlet_bebas,
        })"""

if old in content:
    content = content.replace(old, new)
    open("combat/views.py", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
