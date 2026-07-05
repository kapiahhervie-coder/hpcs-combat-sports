"""
patch_muaythai_views.py
Menerapkan 3 perubahan di muaythai/views.py secara otomatis & presisi:
  1. Import CorrectionAuditL1MT dari muaythai.models
  2. Class L1CorrectionMTView -> pakai model & field baru (8 item)
  3. hapus_l1_mt & detail_l1_mt -> pakai model baru

Membuat backup otomatis sebelum menulis ulang file.
Jika salah satu blok "OLD" tidak ditemukan persis, script akan
berhenti dan memberi tahu tanpa mengubah apapun (aman).
"""
import os
import shutil
from datetime import datetime

FILEPATH = os.path.join('muaythai', 'views.py')

OLD_IMPORT = """from combat.models import (
    Atlet,
    CorrectionAuditL1,
    StrengthAuditL2,
    PowerAuditL3,
    SpeedAgilityAuditL4,
)"""

NEW_IMPORT = """from combat.models import (
    Atlet,
    StrengthAuditL2,
    PowerAuditL3,
    SpeedAgilityAuditL4,
)
from muaythai.models import CorrectionAuditL1MT"""


OLD_VIEW = """class L1CorrectionMTView(LoginRequiredMixin, View):
    template_name = 'muaythai/l1_correction.html'

    def get(self, request):
        atlet_qs   = get_atlet_muaythai(request.user)
        history    = CorrectionAuditL1.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        atlet_list = atlet_qs.order_by('nama_atlet')
        return render(request, self.template_name, {
            'history':    history,
            'atlet_list': atlet_list,
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='muaythai') if atlet_id else None

            audit = CorrectionAuditL1(
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
            )
            audit.save()

            if audit.layak_naik:
                messages.success(request, f'✅ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). LAYAK naik ke L2!')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). Belum layak ke L2.')

        except Exception as e:
            messages.error(request, f'Error menyimpan data: {e}')

        return redirect('muaythai:l1_correction')"""

NEW_VIEW = """class L1CorrectionMTView(LoginRequiredMixin, View):
    template_name = 'muaythai/l1_correction.html'

    def get(self, request):
        atlet_qs   = get_atlet_muaythai(request.user)
        history    = CorrectionAuditL1MT.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        atlet_list = atlet_qs.order_by('nama_atlet')
        return render(request, self.template_name, {
            'history':    history,
            'atlet_list': atlet_list,
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='muaythai') if atlet_id else None

            def to_float(key):
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
            )
            audit.save()

            if audit.layak_naik:
                messages.success(request, f'✅ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). LAYAK naik ke L2!')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). Belum layak ke L2.')

        except Exception as e:
            print(f"‼️ ERROR L1 MT SAVE: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error menyimpan data: {e}')

        return redirect('muaythai:l1_correction')"""


OLD_HAPUS_DETAIL = """def hapus_l1_mt(request, pk):
    audit = get_object_or_404(CorrectionAuditL1, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L1 {nama} berhasil dihapus.')
    return redirect('muaythai:l1_correction')


def detail_l1_mt(request, pk):
    audit = get_object_or_404(CorrectionAuditL1, pk=pk)
    return JsonResponse({
        'atlet_name': audit.atlet_name, 'kategori_usia': audit.kategori_usia,
        'gender': audit.gender, 'kelas_berat': audit.kelas_berat,
        'score_rotation': audit.score_rotation, 'score_extension': audit.score_extension,
        'score_stability': audit.score_stability, 'score_posture': audit.score_posture,
        'score_breathing': audit.score_breathing, 'total_skor': audit.total_skor,
        'predikat': audit.predikat, 'layak_naik': audit.layak_naik,
    })"""

NEW_HAPUS_DETAIL = """def hapus_l1_mt(request, pk):
    audit = get_object_or_404(CorrectionAuditL1MT, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L1 {nama} berhasil dihapus.')
    return redirect('muaythai:l1_correction')


def detail_l1_mt(request, pk):
    audit = get_object_or_404(CorrectionAuditL1MT, pk=pk)
    return JsonResponse({
        'atlet_name': audit.atlet_name, 'kategori_usia': audit.kategori_usia,
        'gender': audit.gender, 'kelas_berat': audit.kelas_berat,
        'total_skor': audit.total_skor, 'predikat': audit.predikat,
        'layak_naik': audit.layak_naik, 'item_terlemah': audit.item_terlemah,
        'rekomendasi': audit.rekomendasi_auto,
    })"""


REPLACEMENTS = [
    ("Import CorrectionAuditL1MT", OLD_IMPORT, NEW_IMPORT),
    ("Class L1CorrectionMTView", OLD_VIEW, NEW_VIEW),
    ("hapus_l1_mt & detail_l1_mt", OLD_HAPUS_DETAIL, NEW_HAPUS_DETAIL),
]


def main():
    if not os.path.exists(FILEPATH):
        print(f"File tidak ditemukan: {FILEPATH}")
        return

    with open(FILEPATH, encoding='utf-8') as f:
        content = f.read()

    # Cek dulu semua blok OLD ada sebelum mengubah apapun
    missing = []
    for label, old, new in REPLACEMENTS:
        count = content.count(old)
        if count == 0:
            missing.append(label)
        elif count > 1:
            print(f"PERINGATAN: blok '{label}' ditemukan {count}x (seharusnya 1x). Dibatalkan demi keamanan.")
            return

    if missing:
        print("Blok berikut TIDAK ditemukan persis di file (mungkin sudah pernah diedit sebagian):")
        for m in missing:
            print(f"  - {m}")
        print("\nTidak ada perubahan dilakukan. Cek manual bagian yang bermasalah.")
        return

    # Semua blok ditemukan tepat 1x -> aman untuk backup & ganti
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = FILEPATH + f'.backup-{timestamp}'
    shutil.copy2(FILEPATH, backup_path)
    print(f"Backup dibuat: {backup_path}\n")

    for label, old, new in REPLACEMENTS:
        content = content.replace(old, new)
        print(f"Berhasil menerapkan: {label}")

    with open(FILEPATH, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print(f"\nSelesai. File sudah ditulis ulang: {FILEPATH}")
    print("Jalankan 'python manage.py check' untuk verifikasi.")


if __name__ == '__main__':
    main()
