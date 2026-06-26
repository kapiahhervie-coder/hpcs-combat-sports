content = open("combat/views.py", "r", encoding="utf-8").read()

old = """            if action == 'approve':
                profil.status = 'approved'; profil.save()
                messages.success(request, f'{nama} berhasil disetujui.')"""

new = """            if action == 'approve':
                profil.status = 'approved'; profil.save()
                messages.success(request, f'{nama} berhasil disetujui.')
                # Kirim email notifikasi
                try:
                    from django.core.mail import send_mail
                    email_tujuan = profil.email or profil.user.email
                    if email_tujuan:
                        send_mail(
                            subject='[HPCS] Akun Coach Anda Telah Disetujui',
                            message=f\"\"\"Halo {nama},

Selamat! Akun coach Anda di HPCS Combat Sports telah disetujui oleh administrator.

Detail akun:
- Username : {profil.user.username}
- Cabang   : {profil.get_cabang_display()}

Silakan login sekarang di:
http://127.0.0.1:8000/accounts/login/

Salam,
Tim HPCS Combat Sports\"\"\",
                            from_email=None,
                            recipient_list=[email_tujuan],
                            fail_silently=True,
                        )
                except Exception:
                    pass"""

if old in content:
    content = content.replace(old, new)
    open("combat/views.py", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
