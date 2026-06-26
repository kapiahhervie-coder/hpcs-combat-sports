from .models import Atlet


def get_atlet_queryset(user):
    """
    Mengembalikan queryset Atlet sesuai role user.
    - Superuser/Admin  -> semua atlet
    - Coach (approved) -> hanya atlet binaannya sendiri
    - User lain        -> queryset kosong (tidak ada akses)
    """
    if user.is_superuser or user.is_staff:
        return Atlet.objects.all()

    profil = getattr(user, 'profil_pelatih', None)
    if profil and profil.is_approved:
        return Atlet.objects.filter(pelatih=user)

    return Atlet.objects.none()


def is_admin(user):
    return user.is_superuser or user.is_staff


def is_approved_coach(user):
    profil = getattr(user, 'profil_pelatih', None)
    return bool(profil and profil.is_approved)


def can_access_atlet(user, atlet):
    if is_admin(user):
        return True
    if is_approved_coach(user):
        return atlet.pelatih_id == user.id
    return False
