"""
patch_settings_production.py
Menyesuaikan hpcs_config/settings.py untuk siap deploy ke Render:
  1. DEBUG dibaca dari .env (default False untuk keamanan production)
  2. ALLOWED_HOSTS mencakup domain Render + localhost untuk dev
  3. Tambah whitenoise middleware (serve static files di production)
  4. Tambah STATIC_ROOT + STORAGES (untuk collectstatic + kompresi otomatis)
Aman dijalankan berkali-kali (idempotent).
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('hpcs_config', 'settings.py')

REPLACEMENTS = [
    (
        "DEBUG dari environment",
        "# SECURITY WARNING: don't run with debug turned on in production!\nDEBUG = True",
        "# SECURITY WARNING: don't run with debug turned on in production!\nDEBUG = config('DEBUG', default=False, cast=bool)",
    ),
    (
        "ALLOWED_HOSTS untuk Render",
        "ALLOWED_HOSTS = []",
        "ALLOWED_HOSTS = config(\n    'ALLOWED_HOSTS',\n    default='localhost,127.0.0.1,.onrender.com',\n).split(',')",
    ),
    (
        "Whitenoise middleware",
        "MIDDLEWARE = [\n    'django.middleware.security.SecurityMiddleware',\n    'django.contrib.sessions.middleware.SessionMiddleware',",
        "MIDDLEWARE = [\n    'django.middleware.security.SecurityMiddleware',\n    'whitenoise.middleware.WhiteNoiseMiddleware',\n    'django.contrib.sessions.middleware.SessionMiddleware',",
    ),
    (
        "STATIC_ROOT + STORAGES",
        "STATIC_URL = 'static/'",
        "STATIC_URL = 'static/'\nSTATIC_ROOT = BASE_DIR / 'staticfiles'\n\nSTORAGES = {\n    \"default\": {\n        \"BACKEND\": \"django.core.files.storage.FileSystemStorage\",\n    },\n    \"staticfiles\": {\n        \"BACKEND\": \"whitenoise.storage.CompressedManifestStaticFilesStorage\",\n    },\n}",
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
