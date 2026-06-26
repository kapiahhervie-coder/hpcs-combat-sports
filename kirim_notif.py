from combat.models import ProfilPelatih
from django.core.mail import send_mail

p = ProfilPelatih.objects.get(user__username='as coach')
p.email = 'sakalahpcs@gmail.com'
p.user.email = 'sakalahpcs@gmail.com'
p.save()
p.user.save()

nama = p.user.get_full_name() or p.user.username
send_mail(
    subject='[HPCS] Akun Coach Anda Telah Disetujui',
    message=f"""Halo {nama},

Selamat! Akun coach Anda di HPCS Combat Sports telah disetujui.

Detail akun:
- Username : {p.user.username}
- Cabang   : {p.get_cabang_display()}

Login di: http://127.0.0.1:8000/accounts/login/

Salam,
Tim HPCS Combat Sports""",
    from_email=None,
    recipient_list=['sakalahpcs@gmail.com'],
    fail_silently=False,
)
print("Email terkirim!")
