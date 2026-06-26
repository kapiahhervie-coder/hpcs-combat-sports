from combat.models import Atlet
from django.contrib.auth.models import User

print("=== SEMUA ATLET & PELATIH ===")
for a in Atlet.objects.all().select_related('pelatih'):
    pelatih = a.pelatih.get_full_name() if a.pelatih else "BELUM ADA"
    print(f"  {a.nama_atlet} -> {pelatih} (id pelatih: {a.pelatih_id})")

print()
print("=== COACH & ATLET BINAAN ===")
for u in User.objects.filter(profil_pelatih__status='approved'):
    binaan = Atlet.objects.filter(pelatih=u)
    print(f"  {u.get_full_name()} (@{u.username}, id={u.id}): {[a.nama_atlet for a in binaan]}")
