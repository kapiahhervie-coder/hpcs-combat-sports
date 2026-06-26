from combat.models import Atlet
from django.db.models import Count

print("=== TOTAL ATLET PER CABANG ===")
hasil = Atlet.objects.values("cabang").annotate(jumlah=Count("id")).order_by("cabang")
for h in hasil:
    print(f"{h['cabang'] or '(kosong)'}: {h['jumlah']} atlet")

print()
print("=== TOTAL KESELURUHAN ===")
print(f"Total semua atlet: {Atlet.objects.count()}")
print(f"Boxing saja: {Atlet.objects.filter(cabang__iexact='boxing').count()}")
print(f"Muay Thai saja: {Atlet.objects.filter(cabang__iexact='muaythai').count()}")
