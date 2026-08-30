from django.db import migrations


CABOR_AWAL = [
    {
        'kode': 'boxing', 'nama': 'Boxing', 'app_slug': 'boxing',
        'icon_class': 'fa-solid fa-hand-fist', 'warna_tema': '#e63946',
        'aktif': True, 'urutan_tampil': 1,
    },
    {
        'kode': 'muaythai', 'nama': 'Muay Thai', 'app_slug': 'muaythai',
        'icon_class': 'fa-solid fa-fire-flame-curved', 'warna_tema': '#f77f00',
        'aktif': True, 'urutan_tampil': 2,
    },
    {
        'kode': 'krt', 'nama': 'Karate', 'app_slug': 'karate',
        'icon_class': 'fa-solid fa-hand-back-fist', 'warna_tema': '#003049',
        'aktif': True, 'urutan_tampil': 3,
    },
    {
        'kode': 'tkd', 'nama': 'Taekwondo', 'app_slug': 'taekwondo',
        'icon_class': 'fa-solid fa-shoe-prints', 'warna_tema': '#0077b6',
        'aktif': True, 'urutan_tampil': 4,
    },
    # 2 cabor ini muncul di form Tambah Atlet tapi app-nya belum dibuat.
    # Ditaruh non-aktif dulu biar gak muncul di dropdown/menu manapun,
    # tapi kalau ternyata ada atlet lama yang ke-assign cabang='judo'/'mma',
    # atlet.cabor_obj tetap nemu datanya (gak return None).
    {
        'kode': 'judo', 'nama': 'Judo', 'app_slug': '',
        'icon_class': 'fa-solid fa-people-pulling', 'warna_tema': '#6a4c93',
        'aktif': False, 'urutan_tampil': 5,
    },
    {
        'kode': 'mma', 'nama': 'MMA', 'app_slug': '',
        'icon_class': 'fa-solid fa-hands', 'warna_tema': '#8d0801',
        'aktif': False, 'urutan_tampil': 6,
    },
]


def seed_cabor(apps, schema_editor):
    Cabor = apps.get_model('combat', 'Cabor')
    for data in CABOR_AWAL:
        Cabor.objects.get_or_create(kode=data['kode'], defaults=data)


def hapus_cabor(apps, schema_editor):
    Cabor = apps.get_model('combat', 'Cabor')
    kode_list = [c['kode'] for c in CABOR_AWAL]
    Cabor.objects.filter(kode__in=kode_list).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('combat', '0015_cabor'),
    ]

    operations = [
        migrations.RunPython(seed_cabor, hapus_cabor),
    ]
