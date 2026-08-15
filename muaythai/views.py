"""
HPCS — Muay Thai Views
Terpisah penuh dari Boxing. Model shared, URL & halaman terpisah.
Fase 2: L1-L4 pakai model yang sama, filter atlet MT.
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
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
from muaythai.models import CorrectionAuditL1MT


def get_atlet_muaythai(user):
    qs = Atlet.objects.filter(cabang='muaythai')
    if user.is_superuser or user.is_staff:
        return qs
    return qs.filter(pelatih=user)


# ══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════

class DashboardMuayThaiView(LoginRequiredMixin, View):
    template_name = 'muaythai/dashboard_muaythai.html'

    def get(self, request):
        atlet_id     = request.GET.get('atlet_id')
        daftar_atlet = get_atlet_muaythai(request.user).order_by('nama_atlet')
        atlet = daftar_atlet.filter(id=atlet_id).first() if atlet_id else daftar_atlet.first()

        score_labels, score_data = [], []
        if atlet:
            riwayat = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('timestamp')[:8]
            for r in riwayat:
                score_labels.append(r.timestamp.strftime('%d/%m'))
                score_data.append(float(r.total_skor))

        if not score_data:
            score_labels = ['-']
            score_data   = [0]

        l1_last = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None
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

class DaftarAtletMuayThaiView(LoginRequiredMixin, View):
    template_name = 'muaythai/daftar_atlet.html'

    def get(self, request):
        daftar_atlet = get_atlet_muaythai(request.user).order_by('nama_atlet')
        return render(request, self.template_name, {
            'daftar_atlet': daftar_atlet,
            'total_atlet':  daftar_atlet.count(),
        })


# ══════════════════════════════════════════════════════════════════════
# L1 — CORRECTION (Muay Thai)
# ══════════════════════════════════════════════════════════════════════

class L1CorrectionMTView(LoginRequiredMixin, View):
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
            messages.error(request, f'Error menyimpan data: {e}')

        return redirect('muaythai:l1_correction')


def hapus_l1_mt(request, pk):
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
        'score_rotation': audit.score_rotation, 'score_extension': audit.score_extension,
        'score_stability': audit.score_stability, 'score_posture': audit.score_posture,
        'score_breathing': audit.score_breathing, 'total_skor': audit.total_skor,
        'predikat': audit.predikat, 'layak_naik': audit.layak_naik,
    })


# ══════════════════════════════════════════════════════════════════════
# L2 — STRENGTH (Muay Thai)
# ══════════════════════════════════════════════════════════════════════

class L2StrengthMTView(LoginRequiredMixin, View):
    template_name = 'muaythai/l2_strength.html'

    def get(self, request):
        atlet_qs      = get_atlet_muaythai(request.user)
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
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='muaythai') if atlet_id else None

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

        return redirect('muaythai:l2_strength')


def hapus_l2_mt(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L2 {nama} berhasil dihapus.')
    return redirect('muaythai:l2_strength')


def detail_l2_mt(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk)
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
# L3 — POWER (Muay Thai)
# ══════════════════════════════════════════════════════════════════════

class L3PowerMTView(LoginRequiredMixin, View):
    template_name = 'muaythai/l3_power.html'

    def get(self, request):
        atlet_qs      = get_atlet_muaythai(request.user)
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
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='muaythai') if atlet_id else None

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

        return redirect('muaythai:l3_power')


def hapus_l3_mt(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L3 {nama} berhasil dihapus.')
    return redirect('muaythai:l3_power')


def detail_l3_mt(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk)
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
# L4 — SPEED & AGILITY (Muay Thai)
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


class L4SpeedAgilityMTView(LoginRequiredMixin, View):
    template_name = 'muaythai/l4_speed_agility.html'

    def get(self, request):
        atlet_qs      = get_atlet_muaythai(request.user)
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
            atlet    = get_object_or_404(Atlet, pk=atlet_id, cabang='muaythai') if atlet_id else None

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

        return redirect('muaythai:l4_speed_agility')


def hapus_l4_mt(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L4 {nama} berhasil dihapus.')
    return redirect('muaythai:l4_speed_agility')


def detail_l4_mt(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk)
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
# REPORT CARD (Muay Thai)
# ══════════════════════════════════════════════════════════════════════

class ReportCardMTView(LoginRequiredMixin, View):
    template_name = 'muaythai/report_card.html'

    def get(self, request, atlet_id):
        from django.utils import timezone
        atlet = get_object_or_404(Atlet, pk=atlet_id, cabang='muaythai')

        l1 = CorrectionAuditL1MT.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l2 = StrengthAuditL2.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l3 = PowerAuditL3.objects.filter(atlet=atlet).order_by('-timestamp').first()
        l4 = SpeedAgilityAuditL4.objects.filter(atlet=atlet).order_by('-timestamp').first()

        s1 = round(l1.total_skor * 10, 1) if l1 else 0
        s2 = round(l2.total_skor * 10, 1) if l2 else 0
        s3 = round(l3.total_skor * 10, 1) if l3 else 0
        s4 = round(l4.total_skor * 10, 1) if l4 else 0
        overall = round((s1+s2+s3+s4) / max(sum([1 for x in [s1,s2,s3,s4] if x > 0]), 1), 1)

        context = {
            'atlet': atlet, 'l1': l1, 'l2': l2, 'l3': l3, 'l4': l4,
            'readiness': overall,
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