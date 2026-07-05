import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('muaythai', 'views.py')

OLD = "    StrengthAuditL2,h\n"
NEW = "    StrengthAuditL2,\n"

with open(FILEPATH, encoding='utf-8') as f:
    content = f.read()

count = content.count(OLD)
if count != 1:
    print(f"Baris target ditemukan {count}x (perlu tepat 1x). Tidak ada perubahan dilakukan.")
else:
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = FILEPATH + f'.backup-{timestamp}'
    shutil.copy2(FILEPATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    content = content.replace(OLD, NEW)
    with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    print("Berhasil menghapus karakter 'h' nyasar.")
