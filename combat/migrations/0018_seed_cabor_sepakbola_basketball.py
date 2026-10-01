from django.db import migrations


CABOR_BARU = [
    {
        'kode': 'sepakbola', 'nama': 'Sepak Bola', 'app_slug': 'sepakbola',
        'icon_class': 'fa-solid fa-futbol', 'warna_tema': '#2a9d8f',
        'aktif': True, 'urutan_tampil': 7,
    },
    {
        'kode': 'basketball', 'nama': 'Basket', 'app_slug': 'basketball',
        'icon_class': 'fa-solid fa-basketball', 'warna_tema': '#ff9f1c',
        'aktif': True, 'urutan_tampil': 8,
    },
]


def seed_cabor_baru(apps, schema_editor):
    Cabor = apps.get_model('combat', 'Cabor')
    for data in CABOR_BARU:
        Cabor.objects.get_or_create(kode=data['kode'], defaults=data)


def hapus_cabor_baru(apps, schema_editor):
    Cabor = apps.get_model('combat', 'Cabor')
    kode_list = [c['kode'] for c in CABOR_BARU]
    Cabor.objects.filter(kode__in=kode_list).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('combat', '0017_alter_atlet_cabang_alter_profilpelatih_cabang'),
    ]

    operations = [
        migrations.RunPython(seed_cabor_baru, hapus_cabor_baru),
    ]
