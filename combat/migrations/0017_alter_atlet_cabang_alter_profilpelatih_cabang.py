# Generated manually to restore a migration lost before it was committed to Git.
# Recreated 2026-10-01 based on sepakbola.0001_initial's expected dependency name.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('combat', '0016_seed_cabor_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atlet',
            name='cabang',
            field=models.CharField(
                blank=True,
                choices=[
                    ('boxing', 'Boxing'),
                    ('muaythai', 'Muay Thai'),
                    ('tkd', 'Taekwondo'),
                    ('krt', 'Karate'),
                    ('sepakbola', 'Sepak Bola'),
                    ('basketball', 'Bola Basket'),
                    ('volleyball', 'Bola Voli'),
                    ('badminton', 'Bulutangkis'),
                ],
                max_length=20,
                verbose_name='Cabang Olahraga',
            ),
        ),
        migrations.AlterField(
            model_name='profilpelatih',
            name='cabang',
            field=models.CharField(
                blank=True,
                choices=[
                    ('boxing', 'Boxing'),
                    ('muaythai', 'Muay Thai'),
                    ('tkd', 'Taekwondo'),
                    ('krt', 'Karate'),
                    ('sepakbola', 'Sepak Bola'),
                    ('basketball', 'Bola Basket'),
                    ('volleyball', 'Bola Voli'),
                    ('badminton', 'Bulutangkis'),
                ],
                max_length=20,
            ),
        ),
    ]
