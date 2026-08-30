"""
HPCS Boxing — Models

App 'boxing' TIDAK punya model sendiri. Semua data (Atlet, CorrectionAuditL1,
StrengthAuditL2, PowerAuditL3, SpeedAgilityAuditL4, RekomendasiProgram,
ProfilPelatih) dipakai bersama dari app 'combat' (data layer terpusat) —
sesuai pola yang sudah dipakai di app 'muaythai', 'karate', dan 'taekwondo'.

File ini sengaja dikosongkan dari 27/08/2026. Sebelumnya file ini berisi
duplikat penuh dari combat/models.py, yang menyebabkan Django gagal
migrate karena dua model berbeda menunjuk ke db_table yang sama
(hpcs_correction_audit_l1, hpcs_strength_audit_l2, dst).

Aman dihapus karena app 'boxing' TIDAK PERNAH punya migration sendiri
(dikonfirmasi lewat `python manage.py showmigrations boxing` -> "no
migrations") — semua data Boxing yang tersimpan selama ini sudah
otomatis memakai tabel combat.* yang sama (karena db_table-nya sama
persis), jadi tidak ada data yang hilang dari perubahan ini.

Kalau butuh model, import langsung dari combat.models, contoh:
    from combat.models import Atlet, CorrectionAuditL1, StrengthAuditL2
"""

from django.db import models  # noqa: F401  (dibiarkan supaya Django tetap treat file ini sebagai models module yang valid)