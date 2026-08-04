from django.db import migrations


def seed_kategori(apps, schema_editor):
    KategoriAktivitas = apps.get_model('pjok', 'KategoriAktivitas')
    kategori_list = [
        'permainan_olahraga',
        'senam',
        'gerak_berirama',
        'air',
        'kebugaran',
    ]
    for kode in kategori_list:
        KategoriAktivitas.objects.get_or_create(kode=kode)


def hapus_kategori(apps, schema_editor):
    KategoriAktivitas = apps.get_model('pjok', 'KategoriAktivitas')
    KategoriAktivitas.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pjok', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_kategori, hapus_kategori),
    ]
