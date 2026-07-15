"""
fix_atlet_list_mt.py
Memperbaiki bug: atlet_qs dihitung tapi tidak pernah dikirim sebagai
'atlet_list' ke context render() di L2StrengthMTView, L3PowerMTView,
L4SpeedAgilityMTView -- menyebabkan dropdown "Pilih Atlet" kosong.
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('muaythai', 'views.py')

REPLACEMENTS = [
    (
        "L2StrengthMTView",
        "        history       = StrengthAuditL2.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]\n        return render(request, self.template_name, {\n            'history':        history,\n            'selected_atlet': selected_atlet,\n        })",
        "        history       = StrengthAuditL2.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]\n        return render(request, self.template_name, {\n            'history':        history,\n            'selected_atlet': selected_atlet,\n            'atlet_list':     atlet_qs.order_by('nama_atlet'),\n        })",
    ),
    (
        "L3PowerMTView",
        "        history       = PowerAuditL3.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]\n        return render(request, self.template_name, {\n            'history':        history,\n            'selected_atlet': selected_atlet,\n        })",
        "        history       = PowerAuditL3.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]\n        return render(request, self.template_name, {\n            'history':        history,\n            'selected_atlet': selected_atlet,\n            'atlet_list':     atlet_qs.order_by('nama_atlet'),\n        })",
    ),
    (
        "L4SpeedAgilityMTView",
        "        history       = SpeedAgilityAuditL4.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]\n        return render(request, self.template_name, {\n            'history':        history,\n            'selected_atlet': selected_atlet,\n        })",
        "        history       = SpeedAgilityAuditL4.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]\n        return render(request, self.template_name, {\n            'history':        history,\n            'selected_atlet': selected_atlet,\n            'atlet_list':     atlet_qs.order_by('nama_atlet'),\n        })",
    ),
]


def main():
    if not os.path.exists(FILEPATH):
        print(f"File tidak ditemukan: {FILEPATH}")
        return

    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    original_content = content
    applied = []
    skipped = []
    warned = []

    for label, old, new in REPLACEMENTS:
        count = content.count(old)
        if count == 0:
            if content.count(new) >= 1:
                skipped.append(f"{label} (sudah benar)")
            else:
                warned.append(f"{label} (blok lama tidak ditemukan persis)")
        elif count == 1:
            content = content.replace(old, new)
            applied.append(label)
        else:
            warned.append(f"{label} (ditemukan {count}x, seharusnya 1x)")

    if content == original_content:
        print("Tidak ada perubahan dilakukan.")
    else:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = FILEPATH + f'.backup-{timestamp}'
        shutil.copy2(FILEPATH, backup_path)
        print(f"Backup dibuat: {backup_path}\n")

        with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"File ditulis ulang: {FILEPATH}\n")

    print("=== RINGKASAN ===")
    for a in applied:
        print(f"  [OK] {a}")
    for s in skipped:
        print(f"  [-]  {s}")
    for w in warned:
        print(f"  [!]  {w}")

    print("\nJalankan 'python manage.py check' untuk verifikasi.")


if __name__ == '__main__':
    main()
