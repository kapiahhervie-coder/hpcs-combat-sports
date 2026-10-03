"""
HPCS Basketball â€” Views
High Performance Coaching System
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.contrib import messages

from .models import (
    AtletBasket, BasketL1Correction, BasketL2Strength,
    BasketL3Power, BasketL4Specific
)


def get_atlet_basket(user):
    qs = AtletBasket.objects.all()
    if user.is_superuser or user.is_staff:
        return qs
    return qs.filter(pelatih=user)


def to_float(val):
    if not val: return None
    try: return float(str(val).replace(',', '.').strip())
    except: return None


def to_int(val):
    if not val: return None
    try: return int(str(val).strip())
    except: return None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DASHBOARD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class DashboardBasketballView(LoginRequiredMixin, View):
    template_name = 'basketball/dashboard_basketball.html'

    def get(self, request):
        atlet_id     = request.GET.get('atlet_id')
        daftar_atlet = get_atlet_basket(request.user).order_by('nama_atlet')
        atlet = daftar_atlet.filter(id=atlet_id).first() if atlet_id else daftar_atlet.first()

        score_labels, score_data = ['-'], [0]
        l1 = l2 = l3 = l4 = None
        training_load = 0

        if atlet:
            riwayat = BasketL1Correction.objects.filter(atlet=atlet).order_by('timestamp')[:8]
            if riwayat:
                score_labels = [r.timestamp.strftime('%d/%m') for r in riwayat]
                score_data   = [float(r.total_skor) for r in riwayat]

            l1 = BasketL1Correction.objects.filter(atlet=atlet).order_by('-timestamp').first()
            l2 = BasketL2Strength.objects.filter(atlet=atlet).order_by('-timestamp').first()
            l3 = BasketL3Power.objects.filter(atlet=atlet).order_by('-timestamp').first()
            l4 = BasketL4Specific.objects.filter(atlet=atlet).order_by('-timestamp').first()

            scores = [x.total_skor for x in [l1, l2, l3, l4] if x]
            training_load = round((sum(scores) / len(scores)) * 10, 1) if scores else 0

        context = {
            'atlet': atlet,
            'daftar_atlet': daftar_atlet,
            'total_atlet': daftar_atlet.count(),
            'score_labels': json.dumps(score_labels),
            'score_data': json.dumps(score_data),
            'training_load': training_load,
            'l1': l1, 'l2': l2, 'l3': l3, 'l4': l4,
        }
        return render(request, self.template_name, context)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DAFTAR ATLET
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class DaftarAtletBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/daftar_atlet.html'

    def get(self, request):
        daftar = get_atlet_basket(request.user).order_by('nama_atlet')
        return render(request, 'basketball/daftar_atlet.html', {
            'daftar_atlet': daftar,
            'total_atlet': daftar.count(),
        })

    def post(self, request):
        try:
            profil = getattr(request.user, 'profil_pelatih', None)
            if profil and not profil.bisa_tambah_atlet():
                messages.error(request, f'Batas {profil.FREE_ATLET_LIMIT} atlet untuk akun Free sudah tercapai. Upgrade ke Pro untuk menambah atlet tanpa batas.')
                return redirect('basketball:daftar_atlet')
            atlet = AtletBasket(
                nama_atlet    = request.POST.get('nama_atlet', '').strip(),
                kategori_umur = request.POST.get('kategori_umur', 'ELITE'),
                gender        = request.POST.get('gender', 'Putra'),
                posisi        = request.POST.get('posisi', ''),
                kelas_berat   = to_float(request.POST.get('kelas_berat')) or 0,
                tinggi_badan  = to_float(request.POST.get('tinggi_badan')),
                wingspan      = to_float(request.POST.get('wingspan')),
                tanggal_lahir = request.POST.get('tanggal_lahir') or None,
                tahap_ltad    = request.POST.get('tahap_ltad', ''),
                pelatih       = request.user,
            )
            atlet.save()
            messages.success(request, f'Atlet {atlet.nama_atlet} berhasil ditambahkan!')
        except Exception as e:
            messages.error(request, f'Gagal: {e}')
        return redirect('basketball:daftar_atlet')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# L1 â€” CORRECTION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class L1CorrectionBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/l1_correction.html'

    def get(self, request):
        atlet_qs = get_atlet_basket(request.user)
        history  = BasketL1Correction.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history': history,
            'atlet_list': atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(AtletBasket, pk=atlet_id) if atlet_id else None

            audit = BasketL1Correction(
                atlet          = atlet,
                atlet_name     = atlet.nama_atlet if atlet else '',
                kategori_usia  = request.POST.get('kategori_usia', 'ELITE'),
                gender         = request.POST.get('gender', 'Putra'),
                posisi         = request.POST.get('posisi', ''),
                ankle_kiri_cm  = to_float(request.POST.get('ankle_kiri_cm')),
                ankle_kanan_cm = to_float(request.POST.get('ankle_kanan_cm')),
                score_ankle    = to_float(request.POST.get('score_ankle')) or 0,
                hip_fleksi_kiri  = to_float(request.POST.get('hip_fleksi_kiri')),
                hip_fleksi_kanan = to_float(request.POST.get('hip_fleksi_kanan')),
                score_hip      = to_float(request.POST.get('score_hip')) or 0,
                shoulder_fleksi = to_float(request.POST.get('shoulder_fleksi')),
                score_shoulder = to_float(request.POST.get('score_shoulder')) or 0,
                balance_kiri_detik  = to_float(request.POST.get('balance_kiri_detik')),
                balance_kanan_detik = to_float(request.POST.get('balance_kanan_detik')),
                score_stability = to_float(request.POST.get('score_stability')) or 0,
                score_posture   = to_float(request.POST.get('score_posture')) or 0,
                catatan        = request.POST.get('catatan', ''),
                created_by     = request.user.get_full_name() or request.user.username,
            )
            audit.save()
            if audit.layak_naik:
                messages.success(request, f'âœ… {audit.atlet_name} â€” {audit.total_skor} ({audit.predikat}). LAYAK ke L2!')
            else:
                messages.warning(request, f'âš ï¸ {audit.atlet_name} â€” {audit.total_skor} ({audit.predikat}). Belum layak ke L2.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('basketball:l1_correction')


def hapus_l1_basket(request, pk):
    audit = get_object_or_404(BasketL1Correction, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L1 {nama} dihapus.')
    return redirect('basketball:l1_correction')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# L2 â€” STRENGTH
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class L2StrengthBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/l2_strength.html'

    def get(self, request):
        atlet_qs = get_atlet_basket(request.user)
        history  = BasketL2Strength.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history': history,
            'atlet_list': atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(AtletBasket, pk=atlet_id) if atlet_id else None

            audit = BasketL2Strength(
                atlet       = atlet,
                atlet_name  = atlet.nama_atlet if atlet else '',
                kategori_usia = request.POST.get('kategori_usia', 'ELITE'),
                gender      = request.POST.get('gender', 'Putra'),
                posisi      = request.POST.get('posisi', ''),
                kelas_berat = to_float(request.POST.get('kelas_berat')),
                squat_1rm   = to_float(request.POST.get('squat_1rm')),
                score_lower = to_float(request.POST.get('score_lower')) or 0,
                bench_1rm   = to_float(request.POST.get('bench_1rm')),
                score_upper = to_float(request.POST.get('score_upper')) or 0,
                plank_detik = to_int(request.POST.get('plank_detik')),
                score_core  = to_float(request.POST.get('score_core')) or 0,
                single_leg_squat_kiri  = to_int(request.POST.get('single_leg_squat_kiri')),
                single_leg_squat_kanan = to_int(request.POST.get('single_leg_squat_kanan')),
                score_single_leg = to_float(request.POST.get('score_single_leg')) or 0,
                grip_kiri_kg  = to_float(request.POST.get('grip_kiri_kg')),
                grip_kanan_kg = to_float(request.POST.get('grip_kanan_kg')),
                score_grip  = to_float(request.POST.get('score_grip')) or 0,
                catatan     = request.POST.get('catatan', ''),
                created_by  = request.user.get_full_name() or request.user.username,
            )
            audit.save()
            if audit.layak_naik:
                messages.success(request, f'âœ… {audit.atlet_name} â€” {audit.total_skor} ({audit.predikat}). LAYAK ke L3!')
            else:
                messages.warning(request, f'âš ï¸ {audit.atlet_name} â€” {audit.total_skor}. Belum layak ke L3.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('basketball:l2_strength')


def hapus_l2_basket(request, pk):
    audit = get_object_or_404(BasketL2Strength, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L2 {nama} dihapus.')
    return redirect('basketball:l2_strength')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# L3 â€” POWER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class L3PowerBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/l3_power.html'

    def get(self, request):
        atlet_qs = get_atlet_basket(request.user)
        history  = BasketL3Power.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history': history,
            'atlet_list': atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(AtletBasket, pk=atlet_id) if atlet_id else None

            audit = BasketL3Power(
                atlet         = atlet,
                atlet_name    = atlet.nama_atlet if atlet else '',
                kategori_usia = request.POST.get('kategori_usia', 'ELITE'),
                gender        = request.POST.get('gender', 'Putra'),
                posisi        = request.POST.get('posisi', ''),
                vertical_jump_cm   = to_float(request.POST.get('vertical_jump_cm')),
                standing_reach_cm  = to_float(request.POST.get('standing_reach_cm')),
                max_reach_cm       = to_float(request.POST.get('max_reach_cm')),
                score_jump         = to_float(request.POST.get('score_jump')) or 0,
                sprint_30m_detik   = to_float(request.POST.get('sprint_30m_detik')),
                sprint_court_detik = to_float(request.POST.get('sprint_court_detik')),
                score_sprint       = to_float(request.POST.get('score_sprint')) or 0,
                lane_agility_detik = to_float(request.POST.get('lane_agility_detik')),
                score_agility      = to_float(request.POST.get('score_agility')) or 0,
                drop_jump_cm       = to_float(request.POST.get('drop_jump_cm')),
                rsi_value          = to_float(request.POST.get('rsi_value')),
                score_rsi          = to_float(request.POST.get('score_rsi')) or 0,
                cod_detik          = to_float(request.POST.get('cod_detik')),
                score_cod          = to_float(request.POST.get('score_cod')) or 0,
                catatan            = request.POST.get('catatan', ''),
                created_by         = request.user.get_full_name() or request.user.username,
            )
            audit.save()
            if audit.layak_naik:
                messages.success(request, f'ðŸ† {audit.atlet_name} â€” {audit.total_skor}. LAYAK KOMPETISI!')
            elif audit.layak_bertahan:
                messages.info(request, f'â„¹ï¸ {audit.atlet_name} â€” Layak bertahan di L3.')
            else:
                messages.warning(request, f'âš ï¸ {audit.atlet_name} â€” {audit.total_skor}. Perlu peningkatan.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('basketball:l3_power')


def hapus_l3_basket(request, pk):
    audit = get_object_or_404(BasketL3Power, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L3 {nama} dihapus.')
    return redirect('basketball:l3_power')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# L4 â€” SPESIFIK BASKET
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class L4SpecificBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/l4_specific.html'

    def get(self, request):
        atlet_qs = get_atlet_basket(request.user)
        history  = BasketL4Specific.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history': history,
            'atlet_list': atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(AtletBasket, pk=atlet_id) if atlet_id else None

            audit = BasketL4Specific(
                atlet         = atlet,
                atlet_name    = atlet.nama_atlet if atlet else '',
                kategori_usia = request.POST.get('kategori_usia', 'ELITE'),
                gender        = request.POST.get('gender', 'Putra'),
                posisi        = request.POST.get('posisi', ''),
                free_throw_pct  = to_float(request.POST.get('free_throw_pct')),
                midrange_pct    = to_float(request.POST.get('midrange_pct')),
                three_point_pct = to_float(request.POST.get('three_point_pct')),
                score_shooting  = to_float(request.POST.get('score_shooting')) or 0,
                dribble_speed_dominant = to_float(request.POST.get('dribble_speed_dominant')),
                dribble_speed_weak     = to_float(request.POST.get('dribble_speed_weak')),
                score_dribbling = to_float(request.POST.get('score_dribbling')) or 0,
                lateral_speed_detik = to_float(request.POST.get('lateral_speed_detik')),
                contest_rate_pct    = to_float(request.POST.get('contest_rate_pct')),
                score_defense   = to_float(request.POST.get('score_defense')) or 0,
                court_vision_score = to_float(request.POST.get('court_vision_score')) or 0,
                decision_speed     = to_float(request.POST.get('decision_speed')) or 0,
                yoyo_level      = to_int(request.POST.get('yoyo_level')),
                yoyo_jarak_m    = to_float(request.POST.get('yoyo_jarak_m')),
                score_conditioning = to_float(request.POST.get('score_conditioning')) or 0,
                catatan         = request.POST.get('catatan', ''),
                created_by      = request.user.get_full_name() or request.user.username,
            )
            audit.save()
            if audit.layak_kompetisi:
                messages.success(request, f'âœ… {audit.atlet_name} â€” LAYAK KOMPETISI!')
            else:
                messages.warning(request, f'âš ï¸ {audit.atlet_name} â€” {audit.total_skor}. Perlu peningkatan.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('basketball:l4_specific')


def hapus_l4_basket(request, pk):
    audit = get_object_or_404(BasketL4Specific, pk=pk)
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L4 {nama} dihapus.')
    return redirect('basketball:l4_specific')