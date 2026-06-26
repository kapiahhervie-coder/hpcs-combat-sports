from django.core.mail import send_mail
try:
    send_mail(
        subject='[HPCS] Test Email Notifikasi',
        message='Email test dari HPCS Combat Sports berhasil dikirim!',
        from_email=None,
        recipient_list=['sakalahpcs@gmail.com'],
        fail_silently=False,
    )
    print("Email berhasil dikirim!")
except Exception as e:
    print(f"Gagal: {e}")
