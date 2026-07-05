"""
fix_all_l1mt.py
Memastikan SEMUA pemakaian CorrectionAuditL1 (lama) di muaythai/views.py
sudah diganti ke CorrectionAuditL1MT (baru). Aman dijalankan berkali-kali:
- Kalau suatu blok sudah benar (OLD tidak ditemukan), akan dilewati.
- Kalau OLD ditemukan tepat 1x, akan diganti.
- Kalau OLD ditemukan >1x, akan diperingatkan tanpa diubah (perlu cek manual).
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('muaythai', 'views.py')

REPLACEMENTS = [
    (
        "Dashboard - riwayat",
        "riwayat = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('timestamp')[:8]",
        "riwayat = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('timestamp')[:8]",
    ),
    (
        "Dashboard - l1_last",
        "l1_last = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None",
        "l1_last = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None",
    ),
    (
        "L1CorrectionMTView.get - history",
        "history    = CorrectionAuditL1.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]",
        "history    = CorrectionAuditL1MT.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]",
    ),
    (
        "ReportCard - l1",
        "l1 = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first()",
        "l1 = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('-timestamp').first()",
    ),
    (
        "hapus_l1_mt",
        "def hapus_l1_mt(request, pk):\n    audit = get_object_or_404(CorrectionAuditL1, pk=pk)",
        "def hapus_l1_mt(request, pk):\n    audit = get_object_or_404(CorrectionAuditL1MT, pk=pk)",
    ),
    (
        "detail_l1_mt",
        "def detail_l1_mt(request, pk):\n    audit = get_object_or_404(CorrectionAuditL1, pk=pk)",
        "def detail_l1_mt(request, pk):\n    audit = get_object_or_404(CorrectionAuditL1MT, pk=pk)",
    ),
]

# Blok post() lama (constructor lama dengan field 5 pilar boxing) -> harus
# diganti total ke constructor baru 8-item. Ini dicek terpisah karena lebih panjang.
OLD_POST_CONSTRUCTOR = """            audit = CorrectionAuditL1(
                atlet               = atlet,
                atlet_name          = atlet.nama_atlet if atlet else request.POST.get('atlet_name', ''),
                kategori_usia       = request.POST.get('kategori_usia', 'ELITE'),
                gender              = request.POST.get('gender', 'Putra'),
                kelas_berat         = request.POST.get('kelas_berat') or None,
                score_rotation      = round((float(request.POST.get('score_rotation', 0) or 0) + float(request.POST.get('score_rotation_r', 0) or 0)) / 2, 2),
                score_extension     = float(request.POST.get('score_extension', 0) or 0),
                score_stability     = round((float(request.POST.get('score_stability', 0) or 0) + float(request.POST.get('score_stability_r', 0) or 0)) / 2, 2),
                score_posture       = float(request.POST.get('score_posture', 0) or 0),
                score_breathing     = float(request.POST.get('score_breathing', 0) or 0),
                ai_confidence_score = request.POST.get('ai_confidence_score') or None,
            )"""

NEW_POST_CONSTRUCTOR = """            def to_float(key):
                val = request.POST.get(key)
                try:
                    return float(val) if val else None
                except (ValueError, TypeError):
                    return None

            def to_int(key, default=1):
                val = request.POST.get(key)
                try:
                    return int(val) if val else default
                except (ValueError, TypeError):
                    return default

            audit = CorrectionAuditL1MT(
                atlet         = atlet,
                atlet_name    = atlet.nama_atlet if atlet else request.POST.get('atlet_name', ''),
                kategori_usia = request.POST.get('kategori_usia', 'ELITE'),
                gender        = request.POST.get('gender', 'Putra'),
                kelas_berat   = to_float('kelas_berat'),

                hip_rotasi_internal_kanan  = to_float('hip_rotasi_internal_kanan'),
                hip_rotasi_internal_kiri   = to_float('hip_rotasi_internal_kiri'),
                hip_rotasi_eksternal_kanan = to_float('hip_rotasi_eksternal_kanan'),
                hip_rotasi_eksternal_kiri  = to_float('hip_rotasi_eksternal_kiri'),
                skor_neural_hip_rotasi     = to_int('skor_neural_hip_rotasi'),

                balance_durasi_mata_terbuka  = to_float('balance_durasi_mata_terbuka'),
                balance_durasi_mata_tertutup = to_float('balance_durasi_mata_tertutup'),
                skor_neural_balance          = to_int('skor_neural_balance'),

                ankle_dorsifleksi_kanan_cm = to_float('ankle_dorsifleksi_kanan_cm'),
                ankle_dorsifleksi_kiri_cm  = to_float('ankle_dorsifleksi_kiri_cm'),
                skor_neural_ankle          = to_int('skor_neural_ankle'),

                thoracic_rotasi_kanan = to_float('thoracic_rotasi_kanan'),
                thoracic_rotasi_kiri  = to_float('thoracic_rotasi_kiri'),
                skor_neural_thoracic  = to_int('skor_neural_thoracic'),

                shoulder_fleksi_kanan = to_float('shoulder_fleksi_kanan'),
                shoulder_fleksi_kiri  = to_float('shoulder_fleksi_kiri'),
                skor_neural_shoulder  = to_int('skor_neural_shoulder'),

                hip_hinge_pass        = request.POST.get('hip_hinge_pass') == 'true',
                skor_neural_hip_hinge = to_int('skor_neural_hip_hinge'),

                core_hold_durasi_detik = to_float('core_hold_durasi_detik'),
                skor_neural_core       = to_int('skor_neural_core'),

                recovery_waktu_detik = to_float('recovery_waktu_detik'),
                skor_neural_recovery = to_int('skor_neural_recovery'),

                ai_confidence_score = to_float('ai_confidence_score'),
            )"""


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

    all_checks = REPLACEMENTS + [("post() constructor (8-item)", OLD_POST_CONSTRUCTOR, NEW_POST_CONSTRUCTOR)]

    for label, old, new in all_checks:
        count = content.count(old)
        if count == 0:
            skipped.append(label)
        elif count == 1:
            content = content.replace(old, new)
            applied.append(label)
        else:
            warned.append(f"{label} (ditemukan {count}x)")

    if content == original_content:
        print("Tidak ada perubahan diperlukan -- semua sudah benar (atau perlu cek manual, lihat peringatan).")
    else:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = FILEPATH + f'.backup-{timestamp}'
        shutil.copy2(FILEPATH, backup_path)
        print(f"Backup dibuat: {backup_path}\n")

        with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"File ditulis ulang: {FILEPATH}\n")

    print("=== RINGKASAN ===")
    if applied:
        print("Diterapkan:")
        for a in applied:
            print(f"  [OK] {a}")
    if skipped:
        print("Dilewati (sudah benar):")
        for s in skipped:
            print(f"  [-]  {s}")
    if warned:
        print("PERLU CEK MANUAL (jumlah kecocokan tidak 1):")
        for w in warned:
            print(f"  [!]  {w}")

    print("\nJalankan 'python manage.py check' untuk verifikasi.")


if __name__ == '__main__':
    main()
