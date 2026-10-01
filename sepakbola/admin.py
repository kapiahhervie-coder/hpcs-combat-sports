from django.contrib import admin
from .models import (
    CorrectionAuditL1SB, StrengthAuditL2SB,
    PowerAuditL3SB, SpeedAgilityAuditL4SB,
)

admin.site.register(CorrectionAuditL1SB)
admin.site.register(StrengthAuditL2SB)
admin.site.register(PowerAuditL3SB)
admin.site.register(SpeedAgilityAuditL4SB)
