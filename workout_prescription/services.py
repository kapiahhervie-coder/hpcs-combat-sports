"""
workout_prescription/services.py
Pilar 2 HPCS -- Rule Engine.

Fungsi di sini MURNI LOGIKA (gak ada model/migration baru), jadi aman
diubah/diperbaiki kapan saja tanpa perlu migrate ulang.

Kenapa baca `predikat`, BUKAN `total_skor` mentah:
1. Ambang batas "READY" beda-beda tiap cabang (mis. Karate >=7.0,
   Muay Thai/Taekwondo >=5.8) -- predikat sudah menormalkan semua itu.
2. Semua model L1 (Boxing/Muay Thai/Karate/Taekwondo) otomatis maksa
   predikat='NOVICE' kalau ada kondisi safety-gate (nyeri lumbar dkk),
   meskipun nama field gate-nya beda-beda per cabang (lumbar_nyeri vs
   status_keputusan vs skor manual 0). Jadi predikat sudah "mewarisi"
   override itu otomatis -- Rule Engine ini gak perlu tau detail SOP
   tiap cabang satu-satu.
"""


def get_audit_l1_terbaru(atlet):
    """
    Ambil objek audit L1 TERBARU milik 1 atlet, lintas cabang -- karena
    tiap cabang nyimpen L1 di model & related_name yang beda:
      - boxing   -> atlet.audit_l1     (combat.CorrectionAuditL1)
      - muaythai -> atlet.audit_l1_mt  (muaythai.CorrectionAuditL1MT)
      - krt      -> atlet.audit_l1_krt (karate.CorrectionAuditL1KRT)
      - tkd      -> atlet.audit_l1_tkd (taekwondo.CorrectionAuditL1TKD)

    Return None kalau atlet belum pernah diaudit L1 sama sekali, atau
    kalau cabang-nya belum dikenal Rule Engine ini (mis. judo/mma yang
    app-nya belum ada).
    """
    cabang_ke_related_name = {
        'boxing':   'audit_l1',
        'muaythai': 'audit_l1_mt',
        'krt':      'audit_l1_krt',
        'tkd':      'audit_l1_tkd',
    }
    related_name = cabang_ke_related_name.get(atlet.cabang)
    if not related_name:
        return None
    if not hasattr(atlet, related_name):
        return None
    return getattr(atlet, related_name).order_by('-timestamp').first()


def cek_akses_l3_l4(atlet):
    """
    Rule Engine utama: tentukan apakah 1 atlet boleh masuk menu L3
    (Power) & L4 (Speed/Agility), atau masih wajib dikunci ke menu
    koreksi L1 dulu.

    Return dict:
        boleh_l3_l4          : bool
        alasan                : str, buat ditampilkan ke pelatih
        predikat_l1           : str atau None
        wajib_koreksi_persen  : int, porsi menu L1 koreksi yang wajib
                                 dijadwalkan kalau belum boleh L3/L4
    """
    audit = get_audit_l1_terbaru(atlet)

    if audit is None:
        return {
            'boleh_l3_l4': False,
            'alasan': 'Belum ada data audit L1 sama sekali. Wajib asesmen L1 dulu sebelum program latihan apa pun.',
            'predikat_l1': None,
            'wajib_koreksi_persen': 100,
        }

    predikat = audit.predikat

    if predikat in ('READY', 'ELITE'):
        return {
            'boleh_l3_l4': True,
            'alasan': f"Audit L1 terbaru berpredikat {predikat}. Aman lanjut ke Power (L3) & Speed/Agility (L4).",
            'predikat_l1': predikat,
            'wajib_koreksi_persen': 0,
        }

    return {
        'boleh_l3_l4': False,
        'alasan': f"Audit L1 terbaru masih berpredikat {predikat} (belum Ready). L3/L4 terkunci sementara -- wajib 70% menu koreksi L1/mobility dulu.",
        'predikat_l1': predikat,
        'wajib_koreksi_persen': 70,
    }


def filter_exercise_bank_untuk_atlet(atlet, exercise_bank_queryset):
    """
    Terapkan hasil cek_akses_l3_l4() ke 1 queryset ExerciseBank --
    kalau atlet belum boleh L3/L4, exercise kategori L3/L4 otomatis
    disaring keluar dari daftar yang boleh dipilih pelatih.

    Dipakai nanti di views.py Tahap 3, waktu pelatih mau nyusun
    AutoPrescription buat 1 atlet.
    """
    hasil = cek_akses_l3_l4(atlet)
    if hasil['boleh_l3_l4']:
        return exercise_bank_queryset
    return exercise_bank_queryset.exclude(kategori__in=['L3', 'L4'])