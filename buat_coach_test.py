from django.contrib.auth.models import User
from combat.models import ProfilPelatih, Atlet

# Buat user coach baru (skip kalau sudah ada)
if not User.objects.filter(username="coach_test").exists():
    coach = User.objects.create_user(username="coach_test", password="coach12345", first_name="Budi")
    ProfilPelatih.objects.create(user=coach, cabang="boxing", status="approved")
    print("Coach baru dibuat:", coach.username)
else:
    coach = User.objects.get(username="coach_test")
    print("Coach sudah ada:", coach.username)

# Assign 1 atlet pertama ke coach ini
atlet = Atlet.objects.first()
if atlet:
    atlet.pelatih = coach
    atlet.save()
    print(f"{atlet.nama_atlet} sekarang dibina oleh {coach.username}")
else:
    print("Belum ada atlet sama sekali di database")

print()
print("=== VERIFIKASI ===")
print(f"Atlet binaan {coach.username}: {Atlet.objects.filter(pelatih=coach).count()}")
print(f"Total semua atlet: {Atlet.objects.count()}")
