from combat.models import ProfilPelatih
p = ProfilPelatih.objects.get(user__username='as coach')
print("Email profil:", repr(p.email))
print("Email user:", repr(p.user.email))
