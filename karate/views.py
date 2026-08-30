"""
HPCS — Karate Views
Terpisah penuh dari Boxing/Muay Thai/Taekwondo. Model L2-L4 shared, L1 & halaman
terpisah (custom neural mobility scheme untuk Karate).
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.contrib import messages

from combat.models import (
    Atlet,
    StrengthAuditL2,
    PowerAuditL3,
    SpeedAgilityAuditL4,
)
from karate.models import CorrectionAuditL1KRT


def get_atlet_karate(user):
    qs = Atlet.objects.filter(cabang='krt')
    if user.is_superuser or user.is_staff:
        return qs
    return qs.filter(pelatih=user)


# ══════════════════════════════════════════════════════════════════════
# L1 — CORRECTION (Karate) — SOP Revisi 2, 6 pilar, skor otomatis 0-10
# ══════════════════════════════════════════════════════════════════════
#
# Ambang berikut HARUS identik dengan tabel norma di
# karate/l1_correction.html (JS) agar preview & hasil simpan konsisten.
# SOP Karate ini FLAT (tidak dipecah per kategori usia/gender), beda
# dengan Boxing yang punya tabel per usia.
#
# Perubahan Revisi 2 vs Revisi 1:
#  - Ankle: ambang berubah + ada syarat asimetri L-R (>1.5cm -> Kurang)
#  - Hip Rotation: IR & ER punya ambang TERPISAH (bukan dijumlahkan lagi)
#  - Thoracic: ambang sama, tapi asimetri >10° membatasi skor maksimal
#    di batas atas "Cukup" (tidak bisa dapat "Baik" walau sudut besar)

RUBRIK_L1_KRT = {
    # SOP Tabel 1: Ankle Mobility (WBLT, cm) — <7 kurang / 7-10 cukup / >=10 baik
    'ankle':        [(10, 9.5), (8.5, 7.5), (7, 5.5)],
    # SOP Tabel 2: Seated Thoracic Rotation (°) — <35 kurang / 35-44 cukup / >=45 baik
    'thoracic':     [(45, 9.5), (40, 7.5), (35, 5.5)],
    # SOP Tabel 3a: Hip Internal Rotation (°) — <30 kurang / 30-35 cukup / >=35 baik
    'hip_ir':       [(35, 9.5), (32.5, 7.5), (30, 5.5)],
    # SOP Tabel 3b: Hip External Rotation (°) — <40 kurang / 40-45 cukup / >=45 baik
    'hip_er':       [(45, 9.5), (42.5, 7.5), (40, 5.5)],
    # SOP Tabel 4: ASLR (°) — <70 kurang / 70-85 cukup / >85-90+ baik
    'aslr':         [(85, 9.5), (77.5, 7.5), (70, 5.5)],
}

# Selisih Kanan vs Kiri di atas ambang ini -> SOP: otomatis dikategorikan
# "Kurang" (Ankle & Hip Rotation) atau dibatasi maksimal "Cukup" (Thoracic).
BATAS_ASIMETRI_ANKLE_KRT   = 1.5   # cm
BATAS_ASIMETRI_THORACIC_KRT = 10   # derajat
BATAS_ASIMETRI_HIP_ROTATION_KRT = 10  # derajat (berlaku terpisah utk IR & ER)


def _skor_dari_ambang_krt(nilai, ambang):
    """ambang = daftar (batas, skor) terurut MENURUN. Kalau nilai >= salah
    satu batas, pakai skor pertama yang cocok. Kalau di bawah batas
    terendah, hitung proporsional (skor = 1 + 3*(nilai/batas_bawah),
    dibatasi maksimal 4.0 — tetap masuk band 'Kurang')."""
    if nilai is None:
        return None
    for batas, skor in ambang:
        if nilai >= batas:
            return skor
    batas_bawah = ambang[-1][0]
    if not batas_bawah or batas_bawah <= 0:
        return 1.0
    return round(min(1 + 3 * (nilai / batas_bawah), 4.0), 1)


def hitung_skor_ankle_krt(kanan, kiri):
    """SOP Revisi 2: skor dari sisi terlemah, DITAMBAH syarat asimetri
    L-R > 1.5cm -> otomatis masuk band Kurang (skor dibatasi maks 4.0)."""
    nilai = [v for v in (kanan, kiri) if v is not None]
    if not nilai:
        return 0
    skor = _skor_dari_ambang_krt(min(nilai), RUBRIK_L1_KRT['ankle']) or 0
    if kanan is not None and kiri is not None:
        if abs(kanan - kiri) > BATAS_ASIMETRI_ANKLE_KRT:
            skor = min(skor, 4.0)
    return skor


def hitung_skor_thoracic_krt(kanan, kiri):
    """SOP Revisi 2: skor dari sisi terlemah. Asimetri >10° membatasi
    skor maksimal di batas atas 'Cukup' (7.0) -- tidak otomatis Kurang,
    tapi tidak bisa mencapai 'Baik' walau sudut individual besar."""
    nilai = [v for v in (kanan, kiri) if v is not None]
    if not nilai:
        return 0
    skor = _skor_dari_ambang_krt(min(nilai), RUBRIK_L1_KRT['thoracic']) or 0
    if kanan is not None and kiri is not None:
        if abs(kanan - kiri) > BATAS_ASIMETRI_THORACIC_KRT and skor > 7.0:
            skor = 7.0
    return skor


def hitung_skor_hip_rotation_krt(int_kanan, int_kiri, eks_kanan, eks_kiri):
    """SOP Revisi 2: Internal Rotation (IR) & External Rotation (ER)
    dinilai dengan ambang TERPISAH (bukan dijumlahkan). Skor gabungan =
    skor TERENDAH antara IR dan ER (komponen paling lemah menentukan).
    Asimetri Kanan vs Kiri > 10° pada IR ATAU ER -> otomatis Kurang."""
    nilai_ir = [v for v in (int_kanan, int_kiri) if v is not None]
    nilai_er = [v for v in (eks_kanan, eks_kiri) if v is not None]

    skor_ir = _skor_dari_ambang_krt(min(nilai_ir), RUBRIK_L1_KRT['hip_ir']) if nilai_ir else None
    skor_er = _skor_dari_ambang_krt(min(nilai_er), RUBRIK_L1_KRT['hip_er']) if nilai_er else None

    komponen = [s for s in (skor_ir, skor_er) if s is not None]
    if not komponen:
        return 0
    skor = min(komponen)

    asimetri = False
    if int_kanan is not None and int_kiri is not None and abs(int_kanan - int_kiri) > BATAS_ASIMETRI_HIP_ROTATION_KRT:
        asimetri = True
    if eks_kanan is not None and eks_kiri is not None and abs(eks_kanan - eks_kiri) > BATAS_ASIMETRI_HIP_ROTATION_KRT:
        asimetri = True
    if asimetri:
        skor = min(skor, 4.0)
    return skor


def hitung_skor_aslr_krt(kanan, kiri):
    nilai = [v for v in (kanan, kiri) if v is not None]
    if not nilai:
        return 0
    return _skor_dari_ambang_krt(min(nilai), RUBRIK_L1_KRT['aslr']) or 0


# Lumbar Extension & Lateral Pelvic Stability sifatnya MURNI KUALITATIF
# (observasi pelatih dari dropdown, sama pola dengan combat.CorrectionAuditL1
# di Boxing) — server hanya memvalidasi & mengunci rentang skor (0-10),
# tidak menghitung ulang dari data mentah numerik.
def hitung_skor_kualitatif_krt(nilai_pilihan):
    if nilai_pilihan is None:
        return 0
    try:
        v = float(nilai_pilihan)
    except (TypeError, ValueError):
        return 0
    return round(max(0.0, min(10.0, v)), 1)


class L1CorrectionKRTView(LoginRequiredMixin, View):
    template_name = 'karate/l1_correction.html'

    def get(self, request):
        atlet_qs   = get_atlet_karate(request.user)
        history    = CorrectionAuditL1KRT.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        atlet_list = atlet_qs.order_by('nama_atlet')
        return render(request, self.template_name, {
            'history':    history,
            'atlet_list': atlet_list,
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='krt') if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                if val in (None, ''):
                    return None
                val = str(val).strip().replace(',', '.')  # dukung input format ID (koma desimal)
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None

            kategori_usia = request.POST.get('kategori_usia', 'ELITE')
            gender        = request.POST.get('gender', 'Putra')

            ankle_kanan = to_float('ankle_dorsifleksi_kanan_cm')
            ankle_kiri  = to_float('ankle_dorsifleksi_kiri_cm')

            thoracic_kanan = to_float('thoracic_rotasi_kanan')
            thoracic_kiri  = to_float('thoracic_rotasi_kiri')

            hip_int_kanan = to_float('hip_rotasi_internal_kanan')
            hip_int_kiri  = to_float('hip_rotasi_internal_kiri')
            hip_eks_kanan = to_float('hip_rotasi_eksternal_kanan')
            hip_eks_kiri  = to_float('hip_rotasi_eksternal_kiri')

            aslr_kanan = to_float('asl_raise_kanan_derajat')
            aslr_kiri  = to_float('asl_raise_kiri_derajat')

            # Pilar kualitatif (SOP): pelatih pilih kondisi di dropdown, JS
            # mengirim skornya langsung lewat field skor_lumbar_extension /
            # skor_lateral_pelvic.
            skor_lumbar_input = to_float('skor_lumbar_extension')
            skor_pelvic_input = to_float('skor_lateral_pelvic')

            # NOTE: semua score_* SENGAJA dihitung ulang di server dari data
            # mentah / pilihan dropdown, TIDAK diambil mentah-mentah tanpa
            # validasi — sama pola dengan combat.CorrectionAuditL1 (Boxing).
            audit = CorrectionAuditL1KRT(
                atlet         = atlet,
                atlet_name    = atlet.nama_atlet if atlet else request.POST.get('atlet_name', ''),
                kategori_usia = kategori_usia,
                gender        = gender,
                kelas_berat   = to_float('kelas_berat'),

                ankle_dorsifleksi_kanan_cm = ankle_kanan,
                ankle_dorsifleksi_kiri_cm  = ankle_kiri,
                score_ankle = hitung_skor_ankle_krt(ankle_kanan, ankle_kiri),

                thoracic_rotasi_kanan = thoracic_kanan,
                thoracic_rotasi_kiri  = thoracic_kiri,
                score_thoracic_rotation = hitung_skor_thoracic_krt(thoracic_kanan, thoracic_kiri),

                hip_rotasi_internal_kanan  = hip_int_kanan,
                hip_rotasi_internal_kiri   = hip_int_kiri,
                hip_rotasi_eksternal_kanan = hip_eks_kanan,
                hip_rotasi_eksternal_kiri  = hip_eks_kiri,
                score_hip_rotation = hitung_skor_hip_rotation_krt(hip_int_kanan, hip_int_kiri, hip_eks_kanan, hip_eks_kiri),

                asl_raise_kanan_derajat = aslr_kanan,
                asl_raise_kiri_derajat  = aslr_kiri,
                score_aslr = hitung_skor_aslr_krt(aslr_kanan, aslr_kiri),

                score_lumbar_extension = hitung_skor_kualitatif_krt(skor_lumbar_input),
                score_lateral_pelvic   = hitung_skor_kualitatif_krt(skor_pelvic_input),

                ai_confidence_score = to_float('ai_confidence_score'),
            )
            audit.save()

            if audit.layak_naik:
                messages.success(request, f'✅ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). LAYAK naik ke L2!')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). Belum layak ke L2.')

        except Exception as e:
            messages.error(request, f'Error menyimpan data: {e}')

        return redirect('karate:l1_correction')


@login_required
def hapus_l1_krt(request, pk):
    audit = get_object_or_404(CorrectionAuditL1KRT, pk=pk, atlet__in=get_atlet_karate(request.user))
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L1 {nama} berhasil dihapus.')
    return redirect('karate:l1_correction')


@login_required
def detail_l1_krt(request, pk):
    audit = get_object_or_404(CorrectionAuditL1KRT, pk=pk, atlet__in=get_atlet_karate(request.user))
    return JsonResponse({
        'atlet_name': audit.atlet_name, 'kategori_usia': audit.kategori_usia,
        'gender': audit.gender, 'kelas_berat': audit.kelas_berat,
        'score_ankle': audit.score_ankle,
        'score_thoracic_rotation': audit.score_thoracic_rotation,
        'score_hip_rotation': audit.score_hip_rotation,
        'score_aslr': audit.score_aslr,
        'score_lumbar_extension': audit.score_lumbar_extension,
        'score_lateral_pelvic': audit.score_lateral_pelvic,
        'total_skor': audit.total_skor, 'predikat': audit.predikat,
        'layak_naik': audit.layak_naik, 'item_terlemah': audit.item_terlemah,
        'rekomendasi': audit.rekomendasi_auto,
    })


# ══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════

class DashboardKarateView(LoginRequiredMixin, View):
    template_name = 'karate/dashboard_karate.html'

    def get(self, request):
        atlet_id     = request.GET.get('atlet_id')
        daftar_atlet = get_atlet_karate(request.user).order_by('nama_atlet')
        atlet = daftar_atlet.filter(id=atlet_id).first() if atlet_id else daftar_atlet.first()

        score_labels, score_data = [], []
        if atlet:
            riwayat = CorrectionAuditL1KRT.objects.filter(atlet=atlet).order_by('timestamp')[:8]
            for r in riwayat:
                score_labels.append(r.timestamp.strftime('%d/%m'))
                score_data.append(float(r.total_skor))

        if not score_data:
            score_labels = ['-']
            score_data   = [0]

        l1_last = CorrectionAuditL1KRT.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None
        l2_last = StrengthAuditL2.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None
        l3_last = PowerAuditL3.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None
        l4_last = SpeedAgilityAuditL4.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None

        scores_ada    = [s for s in [
            l1_last.total_skor if l1_last else 0,
            l2_last.total_skor if l2_last else 0,
            l3_last.total_skor if l3_last else 0,
            l4_last.total_skor if l4_last else 0,
        ] if s > 0]
        training_load = round((sum(scores_ada) / len(scores_ada)) * 10, 1) if scores_ada else 0

        context = {
            'atlet':         atlet,
            'daftar_atlet':  daftar_atlet,
            'total_atlet':   daftar_atlet.count(),
            'score_labels':  json.dumps(score_labels),
            'score_data':    json.dumps(score_data),
            'training_load': training_load,
            'l1': l1_last, 'l2': l2_last, 'l3': l3_last, 'l4': l4_last,
        }
        return render(request, self.template_name, context)


# ══════════════════════════════════════════════════════════════════════
# DAFTAR ATLET
# ══════════════════════════════════════════════════════════════════════

class DaftarAtletKarateView(LoginRequiredMixin, View):
    template_name = 'karate/daftar_atlet.html'

    def get(self, request):
        daftar_atlet = get_atlet_karate(request.user).order_by('nama_atlet')
        return render(request, self.template_name, {
            'daftar_atlet': daftar_atlet,
            'total_atlet':  daftar_atlet.count(),
        })


# ══════════════════════════════════════════════════════════════════════
# L2 — STRENGTH (Karate)
# ══════════════════════════════════════════════════════════════════════

class L2StrengthKRTView(LoginRequiredMixin, View):
    template_name = 'karate/l2_strength.html'

    def get(self, request):
        atlet_qs      = get_atlet_karate(request.user)
        atlet_id      = request.GET.get('atlet_id')
        selected_atlet = atlet_qs.filter(pk=atlet_id).first() if atlet_id else None
        history       = StrengthAuditL2.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history':        history,
            'selected_atlet': selected_atlet,
            'atlet_list':     atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='krt') if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                return float(val) if val else None

            def to_int(key):
                val = request.POST.get(key)
                return int(val) if val else None

            audit = StrengthAuditL2(
                atlet=atlet,
                atlet_name=atlet.nama_atlet if atlet else request.POST.get('atlet_name', ''),
                kategori_usia=request.POST.get('kategori_usia', 'Elite'),
                gender=request.POST.get('gender', 'Putra'),
                kelas_berat=to_float('kelas_berat'),
                lower_5rm_beban=to_float('lower_5rm_beban'),
                score_lower=float(request.POST.get('score_lower', 0)),
                push_5rm_beban=to_float('push_5rm_beban'),
                score_push=float(request.POST.get('score_push', 0)),
                pull_reps=to_int('pull_reps'),
                score_pull=float(request.POST.get('score_pull', 0)),
                core_durasi_detik=to_int('core_durasi_detik'),
                score_core=float(request.POST.get('score_core', 0)),
                iso_durasi_detik=to_int('iso_durasi_detik'),
                iso_tremor_onset_detik=to_int('iso_tremor_onset_detik'),
                score_isometric=float(request.POST.get('score_isometric', 0)),
                ai_confidence_score=to_float('ai_confidence_score'),
            )
            audit.save()

            if audit.layak_naik:
                messages.success(request, f'✅ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). LAYAK naik ke L3!')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — Skor {audit.total_skor}. Belum layak ke L3.')

        except Exception as e:
            messages.error(request, f'Error menyimpan data: {e}')

        return redirect('karate:l2_strength')


@login_required
def hapus_l2_krt(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk, atlet__in=get_atlet_karate(request.user))
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L2 {nama} berhasil dihapus.')
    return redirect('karate:l2_strength')


@login_required
def detail_l2_krt(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk, atlet__in=get_atlet_karate(request.user))
    return JsonResponse({
        'atlet_name': audit.atlet_name, 'kategori_usia': audit.kategori_usia,
        'gender': audit.gender, 'kelas_berat': audit.kelas_berat,
        'score_lower': audit.score_lower, 'score_push': audit.score_push,
        'score_pull': audit.score_pull, 'score_core': audit.score_core,
        'score_isometric': audit.score_isometric, 'iso_tremor_rasio': audit.iso_tremor_rasio,
        'total_skor': audit.total_skor, 'predikat': audit.predikat,
        'layak_naik': audit.layak_naik, 'cns_status': audit.cns_status,
        'rekomendasi': audit.rekomendasi_auto,
    })


# ══════════════════════════════════════════════════════════════════════
# L3 — POWER (Karate)
# ══════════════════════════════════════════════════════════════════════

class L3PowerKRTView(LoginRequiredMixin, View):
    template_name = 'karate/l3_power.html'

    def get(self, request):
        atlet_qs      = get_atlet_karate(request.user)
        atlet_id      = request.GET.get('atlet_id')
        selected_atlet = atlet_qs.filter(pk=atlet_id).first() if atlet_id else None
        history       = PowerAuditL3.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history':        history,
            'selected_atlet': selected_atlet,
            'atlet_list':     atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='krt') if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                return float(val) if val else None

            audit = PowerAuditL3(
                atlet=atlet,
                atlet_name=request.POST.get('atlet_name', ''),
                kategori_usia=request.POST.get('kategori_usia', 'ELITE'),
                gender=request.POST.get('gender', 'Putra'),
                kelas_berat=to_float('kelas_berat'),
                score_jump=float(request.POST.get('score_jump', 0)),
                score_sprint=float(request.POST.get('score_sprint', 0)),
                score_throw=float(request.POST.get('score_throw', 0)),
                score_rsi=float(request.POST.get('score_rsi', 0)),
                score_agility=float(request.POST.get('score_agility', 0)),
                rsi_jump_height=to_float('rsi_jump_height'),
                rsi_contact_time=to_float('rsi_contact_time'),
                ai_confidence_score=to_float('ai_confidence_score'),
                catatan=request.POST.get('catatan', ''),
            )
            audit.save()

            if audit.layak_naik:
                messages.success(request, f'🏆 {audit.atlet_name} — Skor {audit.total_skor}. LAYAK KOMPETISI!')
            elif audit.layak_bertahan:
                messages.info(request, f'ℹ️ {audit.atlet_name} — Layak bertahan di L3.')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — {audit.alasan_tidak_layak}')

        except Exception as e:
            messages.error(request, f'Error menyimpan data: {e}')

        return redirect('karate:l3_power')


@login_required
def hapus_l3_krt(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk, atlet__in=get_atlet_karate(request.user))
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L3 {nama} berhasil dihapus.')
    return redirect('karate:l3_power')


@login_required
def detail_l3_krt(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk, atlet__in=get_atlet_karate(request.user))
    return JsonResponse({
        'atlet_name': audit.atlet_name, 'kategori_usia': audit.kategori_usia,
        'gender': audit.gender, 'kelas_berat': audit.kelas_berat,
        'score_jump': audit.score_jump, 'score_sprint': audit.score_sprint,
        'score_throw': audit.score_throw, 'score_rsi': audit.score_rsi,
        'score_agility': audit.score_agility, 'rsi_value': audit.rsi_value,
        'total_skor': audit.total_skor, 'predikat': audit.predikat,
        'layak_naik': audit.layak_naik, 'layak_bertahan': audit.layak_bertahan,
        'rekomendasi': audit.rekomendasi_auto,
    })


# ══════════════════════════════════════════════════════════════════════
# L4 — SPEED & AGILITY (Karate)
# ══════════════════════════════════════════════════════════════════════

# Tabel konversi level-shuttle ke jarak (meter), protokol standar Yo-Yo IR1.
# HARUS identik dengan YOYO_JARAK di l4_speed_agility.html (JS) dan dengan
# YOYO_JARAK_TABLE di boxing/views.py (norma sama untuk semua cabor combat).
YOYO_JARAK_TABLE = {
    5:  {1: 40, 2: 80, 3: 120, 4: 160},
    7:  {1: 200, 2: 240, 3: 280, 4: 320, 5: 360, 6: 400, 7: 440, 8: 480},
    9:  {1: 520, 2: 560, 3: 600, 4: 640, 5: 680, 6: 720, 7: 760, 8: 800},
    11: {1: 840, 2: 880, 3: 920, 4: 960, 5: 1000, 6: 1040, 7: 1080, 8: 1120},
    13: {1: 1160, 2: 1200, 3: 1240, 4: 1280, 5: 1320, 6: 1360, 7: 1400, 8: 1440},
    15: {1: 1480, 2: 1520, 3: 1560, 4: 1600, 5: 1640, 6: 1680, 7: 1720, 8: 1760},
    17: {1: 1800, 2: 1840, 3: 1880, 4: 1920, 5: 1960, 6: 2000, 7: 2040, 8: 2080},
    19: {1: 2120, 2: 2160, 3: 2200, 4: 2240, 5: 2280, 6: 2320, 7: 2360, 8: 2400},
    21: {1: 2440, 2: 2480, 3: 2520},
}

# Rubrik kategori+gender NSCA/ACSM L4 — HARUS identik dengan RUBRIK_L4 di
# l4_speed_agility.html (JS) dan boxing/views.py agar preview & hasil
# simpan konsisten. Sama untuk semua cabor combat (SOP L4 HPCS).
RUBRIK_L4 = {
    'YOUTH': {
        'Putra': {'hex': [(12.00, 9.5), (14.00, 7.5), (16.00, 5.5), (18.00, 3.5)],
                   'punch': [(59, 9.5), (51, 7.5), (43, 5.5), (35, 3.5)],
                   'yoyo': [(920, 9.5), (680, 7.5), (440, 5.5), (240, 3.5)]},
        'Putri': {'hex': [(13.50, 9.5), (15.50, 7.5), (17.50, 5.5), (19.50, 3.5)],
                   'punch': [(53, 9.5), (46, 7.5), (38, 5.5), (30, 3.5)],
                   'yoyo': [(760, 9.5), (560, 7.5), (360, 5.5), (160, 3.5)]},
    },
    'JUNIOR': {
        'Putra': {'hex': [(10.50, 9.5), (12.00, 7.5), (13.50, 5.5), (15.00, 3.5)],
                   'punch': [(75, 9.5), (65, 7.5), (55, 5.5), (45, 3.5)],
                   'yoyo': [(1640, 9.5), (1240, 7.5), (880, 5.5), (560, 3.5)]},
        'Putri': {'hex': [(11.60, 9.5), (13.20, 7.5), (14.80, 5.5), (16.50, 3.5)],
                   'punch': [(66, 9.5), (58, 7.5), (49, 5.5), (40, 3.5)],
                   'yoyo': [(1320, 9.5), (1000, 7.5), (680, 5.5), (400, 3.5)]},
    },
    'SENIOR': {
        'Putra': {'hex': [(8.80, 9.5), (10.00, 7.5), (11.50, 5.5), (13.00, 3.5)],
                   'punch': [(90, 9.5), (79, 7.5), (67, 5.5), (55, 3.5)],
                   'yoyo': [(2080, 9.5), (1640, 7.5), (1200, 5.5), (800, 3.5)]},
        'Putri': {'hex': [(9.80, 9.5), (11.20, 7.5), (12.80, 5.5), (14.50, 3.5)],
                   'punch': [(79, 9.5), (69, 7.5), (59, 5.5), (48, 3.5)],
                   'yoyo': [(1640, 9.5), (1280, 7.5), (920, 5.5), (600, 3.5)]},
    },
}
RUBRIK_L4['ELITE'] = RUBRIK_L4['SENIOR']


def _tabel_l4(kategori_usia, gender):
    kat = (kategori_usia or 'ELITE').upper()
    tabel_kat = RUBRIK_L4.get(kat, RUBRIK_L4['SENIOR'])
    return tabel_kat.get(gender, tabel_kat['Putra'])


def hitung_skor_hex(hex1, hex2, hex3, kategori_usia='ELITE', gender='Putra'):
    """Rata-rata 3 putaran hexagon jump -> skor 0-10 (semakin cepat semakin baik).
    Cermin dari calcHex() di JS, kategori/gender-aware seperti RUBRIK_L4."""
    nilai = [v for v in (hex1, hex2, hex3) if v is not None and v > 0]
    if not nilai:
        return 0, None
    avg = round(sum(nilai) / len(nilai), 2)
    ambang = _tabel_l4(kategori_usia, gender)['hex']
    skor = 1.5  # Novice
    for batas, s in ambang:
        if avg <= batas:
            skor = s
            break
    return skor, avg


def hitung_skor_punch(punch_freq, postur_ok=True, kategori_usia='ELITE', gender='Putra'):
    """Jumlah pukulan/10 detik -> skor 0-10, dikurangi 1 jika postur tidak benar.
    Cermin dari autoScorePunch() di JS, kategori/gender-aware."""
    if not punch_freq:
        return 0
    ambang = _tabel_l4(kategori_usia, gender)['punch']
    skor = 1.5  # Novice
    for batas, s in ambang:
        if punch_freq >= batas:
            skor = s
            break
    if not postur_ok:
        skor = max(0, skor - 1)
    return skor


def hitung_skor_yoyo(level, shuttle, jarak_manual, kategori_usia='ELITE', gender='Putra'):
    """Level & shuttle (atau jarak manual) -> jarak (m) -> skor 0-10.
    Cermin dari calcYoYo() di JS, kategori/gender-aware."""
    jarak = jarak_manual
    if level and shuttle:
        jarak = YOYO_JARAK_TABLE.get(level, {}).get(shuttle)
        if jarak is None:
            jarak = level * shuttle * 20  # estimasi kasar, sama seperti fallback JS
    if not jarak or jarak <= 0:
        return 0, None
    ambang = _tabel_l4(kategori_usia, gender)['yoyo']
    skor = 1.5  # Novice
    for batas, s in ambang:
        if jarak >= batas:
            skor = s
            break
    return skor, jarak


class L4SpeedAgilityKRTView(LoginRequiredMixin, View):
    template_name = 'karate/l4_speed_agility.html'

    def get(self, request):
        atlet_qs      = get_atlet_karate(request.user)
        atlet_id      = request.GET.get('atlet_id')
        selected_atlet = atlet_qs.filter(pk=atlet_id).first() if atlet_id else None
        history       = SpeedAgilityAuditL4.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history':        history,
            'selected_atlet': selected_atlet,
            'atlet_list':     atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='krt') if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                try: return float(val) if val else None
                except: return None

            def to_int(key):
                val = request.POST.get(key)
                try: return int(val) if val else None
                except: return None

            kategori_usia = request.POST.get('kategori_usia', 'ELITE')
            gender = request.POST.get('gender', 'Putra')

            hex1 = to_float('hex_waktu_putaran1')
            hex2 = to_float('hex_waktu_putaran2')
            hex3 = to_float('hex_waktu_putaran3')
            score_hex, hex_avg = hitung_skor_hex(hex1, hex2, hex3, kategori_usia, gender)

            punch_freq = to_int('punch_freq_10s')
            punch_postur_ok = request.POST.get('punch_postur_ok') == 'true'
            score_punch = hitung_skor_punch(punch_freq, punch_postur_ok, kategori_usia, gender)

            yoyo_level = to_int('yoyo_level_tercapai')
            yoyo_shuttle = to_int('yoyo_shuttle_tercapai')
            yoyo_jarak_input = to_float('yoyo_total_jarak_m')
            score_yoyo, jarak_final = hitung_skor_yoyo(
                yoyo_level, yoyo_shuttle, yoyo_jarak_input, kategori_usia, gender
            )

            # NOTE: score_hex, score_punch, score_yoyo SENGAJA dihitung ulang di sini
            # dan TIDAK diambil dari request.POST — sama seperti pola di boxing/views.py.
            # Nilai final yang tersimpan selalu hasil kalkulasi server, bukan input
            # pelatih/JS, agar tidak ada skor salah/kosong kalau JS di browser gagal jalan.
            audit = SpeedAgilityAuditL4(
                atlet=atlet,
                atlet_name=request.POST.get('atlet_name', ''),
                kategori_usia=kategori_usia,
                gender=gender,
                kelas_berat=to_float('kelas_berat'),
                hex_waktu_putaran1=hex1,
                hex_waktu_putaran2=hex2,
                hex_waktu_putaran3=hex3,
                score_hex=score_hex,
                punch_freq_10s=punch_freq,
                punch_postur_ok=punch_postur_ok,
                punch_reaction_time_ms=to_float('punch_reaction_time_ms'),
                score_punch=score_punch,
                yoyo_level_tercapai=yoyo_level,
                yoyo_shuttle_tercapai=yoyo_shuttle,
                yoyo_total_jarak_m=jarak_final if jarak_final else yoyo_jarak_input,
                score_yoyo=score_yoyo,
                kondisi_uji=request.POST.get('kondisi_uji', 'FRESH'),
                catatan=request.POST.get('catatan', ''),
            )
            audit.save()

            if audit.layak_kompetisi:
                messages.success(request, f'✅ {audit.atlet_name} — LAYAK KOMPETISI!')
            elif audit.layak_bertahan:
                messages.info(request, f'ℹ️ {audit.atlet_name} — Layak bertahan di L4.')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — {audit.alasan_tidak_layak}')

        except Exception as e:
            messages.error(request, f'Error menyimpan data: {e}')

        return redirect('karate:l4_speed_agility')


@login_required
def hapus_l4_krt(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk, atlet__in=get_atlet_karate(request.user))
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L4 {nama} berhasil dihapus.')
    return redirect('karate:l4_speed_agility')


@login_required
def detail_l4_krt(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk, atlet__in=get_atlet_karate(request.user))
    return JsonResponse({
        'atlet_name': audit.atlet_name, 'kategori_usia': audit.kategori_usia,
        'gender': audit.gender, 'kelas_berat': audit.kelas_berat,
        'hex_waktu_rata': audit.hex_waktu_rata, 'score_hex': audit.score_hex,
        'punch_freq_10s': audit.punch_freq_10s, 'score_punch': audit.score_punch,
        'yoyo_total_jarak_m': audit.yoyo_total_jarak_m,
        'yoyo_vo2max': audit.yoyo_vo2max_estimasi,
        'score_yoyo': audit.score_yoyo, 'total_skor': audit.total_skor,
        'predikat': audit.predikat, 'rekomendasi': audit.rekomendasi_auto,
    })


# ══════════════════════════════════════════════════════════════════════
# REPORT CARD (Karate)
# ══════════════════════════════════════════════════════════════════════

class ReportCardKRTView(LoginRequiredMixin, View):
    template_name = 'karate/report_card.html'

    def get(self, request, atlet_id):
        from django.utils import timezone
        atlet_qs = get_atlet_karate(request.user)
        atlet = get_object_or_404(atlet_qs, pk=atlet_id, cabang='krt')

        l1 = CorrectionAuditL1KRT.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l2 = StrengthAuditL2.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l3 = PowerAuditL3.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l4 = SpeedAgilityAuditL4.objects.filter(atlet=atlet).order_by('-timestamp').first()

        s1 = round(l1.total_skor * 10, 1) if l1 else 0
        s2 = round(l2.total_skor * 10, 1) if l2 else 0
        s3 = round(l3.total_skor * 10, 1) if l3 else 0
        s4 = round(l4.total_skor * 10, 1) if l4 else 0
        overall = round((s1+s2+s3+s4) / max(sum([1 for x in [s1,s2,s3,s4] if x > 0]), 1), 1)

        # Skala 0-100 (overall = total_skor 0-10 * 10), ambang disamakan
        # proporsional dengan _hitung_predikat 0-10 di combat/models.py
        # (>=9->ELITE, >=7->READY, >=5->DEVELOPING, else NOVICE).
        if overall >= 90:
            overall_predikat = 'ELITE'
        elif overall >= 70:
            overall_predikat = 'READY'
        elif overall >= 50:
            overall_predikat = 'DEVELOPING'
        else:
            overall_predikat = 'NOVICE'

        context = {
            'atlet': atlet, 'l1': l1, 'l2': l2, 'l3': l3, 'l4': l4,
            'readiness': overall,
            'overall_predikat': overall_predikat,
            'radar_data_json': json.dumps([s1, s2, s3, s4, s2, overall]),
            'trend_data_json': json.dumps({
                'power':       [s3*0.6, s3*0.7, s3*0.8, s3*0.85, s3*0.9, s3],
                'readiness':   [overall*0.6, overall*0.7, overall*0.75, overall*0.8, overall*0.9, overall],
                'athleticism': [s4*0.5, s4*0.6, s4*0.7, s4*0.8, s4*0.9, s4],
            }),
            'months_labels_json': json.dumps(['JAN','FEB','MAR','APR','MAY','JUN']),
            'tanggal_cetak': timezone.now(),
        }
        return render(request, self.template_name, context)