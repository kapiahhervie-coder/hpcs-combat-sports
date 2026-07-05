"""
boxing/models.py
Model-model audit khusus Boxing.

Definisi asli & tabel database tetap dimiliki oleh app 'combat'
(lihat combat/models.py) -- file ini hanya menjembatani supaya
app 'boxing' punya titik akses model sendiri yang rapi, tanpa
memindahkan data atau memicu migrasi baru.
"""

from combat.models import (
    Atlet,
    CorrectionAuditL1,
    StrengthAuditL2,
    PowerAuditL3,
    SpeedAgilityAuditL4,
)

__all__ = [
    'Atlet',
    'CorrectionAuditL1',
    'StrengthAuditL2',
    'PowerAuditL3',
    'SpeedAgilityAuditL4',
]