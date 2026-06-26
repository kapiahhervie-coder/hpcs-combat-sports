from combat.models import Atlet
print("Total atlet:", Atlet.objects.count())
print("Sudah punya pelatih:", Atlet.objects.filter(pelatih__isnull=False).count())
print("Belum punya pelatih:", Atlet.objects.filter(pelatih__isnull=True).count())
for a in Atlet.objects.all():
    print(f"  - {a.nama_atlet} | pelatih: {a.pelatih or 'belum ada'}")
