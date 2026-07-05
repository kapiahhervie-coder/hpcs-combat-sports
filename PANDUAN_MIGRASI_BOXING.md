# Panduan: Memisahkan `boxing` jadi App Django Mandiri

Pola ini **meniru persis** app `muaythai` yang sudah lebih dulu dipisah dari `combat`
(bukti: `urls.py` combat sudah punya redirect `dashboard_muaythai/ -> muaythai:dashboard`,
dan `l1_correction.html` yang kamu upload ternyata sudah pakai namespace `muaythai:`).

**Prinsip arsitektur:** model (`Atlet`, `CorrectionAuditL1`, dst), `permissions.py`, dan
`admin.py` **tetap tinggal di app `combat`** sebagai data layer terpusat. App `boxing`
(dan `muaythai`) hanya berisi urls + views + templates yang meng-*import* model dari
`combat.models` — persis seperti yang sudah kamu lakukan di `muaythai`.

## File yang saya buat (siap pakai)

```
boxing/
├── __init__.py
├── apps.py
├── urls.py                              (namespace 'boxing', 13 route)
├── views.py                              (dipindah dari combat, import model dari combat.models)
└── templates/boxing/
    ├── dashboard_boxing.html
    ├── l1_correction.html
    ├── l2_strenght.html
    ├── l3_power.html
    └── l4_speed_agility.html

combat_updated/
├── urls.py            → ganti isi combat/urls.py kamu dengan ini (boxing routes jadi redirect)
├── views.py            → ganti isi combat/views.py kamu dengan ini (kode boxing sudah dibuang)
└── tambah_atlet.html   → ganti isi combat/templates/combat/tambah_atlet.html (back-button diperbaiki)
```

## Langkah yang HARUS kamu lakukan manual

Saya tidak menerima `settings.py` dan `urls.py` project (root), jadi 2 langkah ini
tidak bisa saya eksekusi otomatis:

**1. Tambahkan `'boxing'` ke `INSTALLED_APPS`** di `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'combat',
    'boxing',      # ← tambahkan, taruh dekat 'combat'/'muaythai'
    'muaythai',    # (asumsi sudah ada)
    ...
]
```

**2. Daftarkan `boxing.urls`** di root `urls.py` project — cari baris `include('combat.urls'...)`
dan tambahkan baris serupa untuk boxing (mounting di prefix `boxing/`, sesuai pola hardcoded
JS `/boxing/l1-correction/hapus/...` yang sudah saya siapkan di template):
```python
urlpatterns = [
    ...
    path('combat/', include('combat.urls', namespace='combat')),
    path('boxing/', include('boxing.urls', namespace='boxing')),   # ← tambahkan
    path('muaythai/', include('muaythai.urls', namespace='muaythai')),  # (asumsi sudah ada)
    ...
]
```
> Kalau ternyata mounting `combat` kamu BUKAN di prefix `/combat/` (misal langsung di root `''`),
> kabari saya — saya perlu sesuaikan hardcoded fetch URL di `l1_correction.html` dan
> onclick URL di `l2_strenght.html` (baris yang isinya `/boxing/l1-correction/hapus/...`
> dan `/boxing/l2-strength/hapus/...`).

## Cara pasang file yang sudah jadi

```bash
# 1. Copy app boxing ke root project (sejajar dengan folder combat/)
cp -r boxing/ /path/ke/project/

# 2. Timpa file combat yang sudah diperbarui
cp combat_updated/urls.py           /path/ke/project/combat/urls.py
cp combat_updated/views.py          /path/ke/project/combat/views.py
cp combat_updated/tambah_atlet.html /path/ke/project/combat/templates/combat/tambah_atlet.html

# 3. Hapus template boxing lama dari combat (sudah dipindah ke boxing/templates/boxing/)
rm /path/ke/project/combat/templates/combat/dashboard_boxing.html
rm /path/ke/project/combat/templates/combat/l1_correction.html
rm /path/ke/project/combat/templates/combat/l2_strenght.html
rm /path/ke/project/combat/templates/combat/l3_power.html
rm /path/ke/project/combat/templates/combat/l4_speed_agility.html
```

## Checklist testing setelah dipasang

- [ ] `python manage.py check` tidak error (import `combat.models` dari `boxing/views.py` jalan)
- [ ] Login sebagai coach cabang boxing → dashboard combat/global tetap tampil normal
- [ ] Buka `/boxing/` → dashboard boxing tampil, dropdown pilih atlet jalan
- [ ] Isi form L1 Correction → submit → redirect balik ke `/boxing/l1-correction/` (bukan `/combat/...`)
- [ ] Tombol hapus di L1 (AJAX fetch) dan L2 (onclick) → berhasil hapus tanpa 404
- [ ] Tombol "Report Card" di dashboard boxing → tetap ke `combat:report_card` (shared, tidak error)
- [ ] Tambah Atlet dari dashboard boxing → tombol "Kembali"/"Batal" balik ke `/boxing/`, bukan 404
- [ ] URL lama `/combat/dashboard_boxing/`, `/combat/l1-correction/`, dst (kalau ada yang bookmark)
      → otomatis redirect ke `/boxing/...` (backward compat, sama seperti muaythai)
- [ ] **Data lama tidak perlu migrasi** — `Atlet.cabang='boxing'` dan semua audit L1-L4
      tetap di tabel yang sama (`combat_atlet`, `hpcs_power_audit_l3`, dst), tidak ada
      perubahan skema database sama sekali. Ini murni pemisahan kode presentasi/routing.

## Catatan tambahan

- `tambah_atlet.html` sebenarnya form **generik** (ada dropdown pilih cabang apapun),
  jadi saya sengaja biarkan tetap di `combat` sebagai fitur bersama — hanya tombol
  kembalinya yang saya arahkan ke `boxing:dashboard` sesuai konteks upload kamu.
  Kalau nanti coach Muay Thai/Karate juga pakai form ini, pertimbangkan pakai
  `request.META.get('HTTP_REFERER')` atau parameter `?next=` supaya tombol kembali
  dinamis per cabang.
- `ReportCardView`, `ReportCenterView`, `AthleteIntelligenceReportView` sengaja saya
  biarkan di `combat` karena tidak di-filter per cabang (menerima `atlet_id` apa saja) —
  ini fitur lintas-cabang yang wajar dipakai bersama.
