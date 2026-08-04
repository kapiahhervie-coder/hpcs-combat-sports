# App `pjok` — Modul Penilaian PJOK / Physical Education

App ini **terpisah** dari `combat` (HPCS Combat Sports): user berbeda (guru vs pelatih),
model berbeda, dashboard berbeda. Sama-sama hidup di project Django yang sama,
sama-sama pakai satu database fisik (bukan multi-db routing) — jadi setupnya ringkas.

## Cara pasang ke project HPCS yang sudah ada

1. Copy folder `pjok/` ini ke root project Django kamu (sejajar dengan folder `combat/`).

2. Tambahkan ke `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'combat',
       'pjok',
   ]
   ```

3. Tambahkan ke `urls.py` project:
   ```python
   urlpatterns = [
       ...
       path('pjok/', include('pjok.urls')),
   ]
   ```

4. Jalankan migrasi (satu database yang sama, perintah biasa — tidak perlu `--database=`):
   ```powershell
   python manage.py makemigrations pjok
   python manage.py migrate
   ```
   Migrasi `0002_seed_kategori_aktivitas.py` sudah disiapkan untuk otomatis mengisi
   5 kategori aktivitas resmi CP PJOK begitu `migrate` dijalankan.

5. Buat superuser (kalau belum ada) untuk akses admin dan input `MateriFase` &
   `InstrumenTKJI` sesuai ATP sekolahmu:
   ```powershell
   python manage.py createsuperuser
   ```

## Yang masih perlu dilengkapi (belum ada di paket ini)

- **Template `base.html`** — templates di sini pakai `{% extends "base.html" %}`;
  sesuaikan dengan base template project HPCS kamu yang sudah ada (navbar, styling, dll).
- **Perhitungan skor L1-L4 otomatis** — helper hitung sudah ada di `diagnostik.py`
  (`hitung_skor_l1` s.d. `hitung_skor_l4`), tapi belum di-hook ke `save()` model
  `PenilaianFisik`. Perlu ditambahkan `signals.py` atau override `save()` supaya
  `skor_l1`-`skor_l4` terisi otomatis saat guru input data mentah.
- **Data referensi `InstrumenTKJI`** — tabel norma resmi per fase & jenis kelamin
  (durasi gantung, jarak lari, dst) perlu diisi manual lewat admin atau fixture,
  karena angka pastinya perlu dicek ulang dari buku panduan TKJI resmi.
- **Autentikasi/registrasi guru** — belum ada view registrasi; asumsinya akun guru
  dibuat lewat admin dulu (approval), sama seperti pola combat sports.
- **Proteksi CSS/JS & desain dashboard** — template masih minimal, belum ada styling.

## Struktur file

```
pjok/
├── models.py       # GuruProfile, Siswa, MateriFase, PenilaianTeknik/Fisik/Karakter
├── views.py        # dashboard_redirect, buat_profile, dashboard_fase, detail_siswa
├── urls.py
├── admin.py
├── forms.py
├── diagnostik.py   # logika akar masalah + helper hitung skor L1-L4
├── apps.py
├── migrations/
│   ├── __init__.py
│   └── 0002_seed_kategori_aktivitas.py   # 0001_initial dibuat otomatis oleh makemigrations
└── templates/pjok/
    ├── buat_profile.html
    ├── dashboard.html
    └── detail_siswa.html
```
