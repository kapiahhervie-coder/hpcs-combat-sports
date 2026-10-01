from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

GROUPS = ["cabor_1", "cabor_2", "cabor_3", "cabor_4", "pjok"]

class Command(BaseCommand):
    help = "Buat groups untuk akses kalkulator fitnes"

    def handle(self, *args, **kwargs):
        for name in GROUPS:
            group, created = Group.objects.get_or_create(name=name)
            status = "dibuat" if created else "sudah ada"
            self.stdout.write(f"Group {name}: {status}")
