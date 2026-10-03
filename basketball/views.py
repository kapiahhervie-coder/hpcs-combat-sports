"""
HPCS Basketball — Views
High Performance Coaching System
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views import View
from django.http import JsonResponse
from django.contrib import messages

from . import scoring
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


# ══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════
# DAFTAR ATLET
# ══════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════
# HELPER — filter kategori & atlet (pola sama dengan Boxing)
# ══════════════════════════════════════════════════════════════════════

KATEGORI_VALID = ('ELITE', 'YOUTH', 'JUNIOR', 'SENIOR')


def _kategori_filter(request):
    cat = (request.GET.get('category') or '').strip().upper()
    return cat if cat in KATEGORI_VALID else ''


def _atlet_dipilih(request, atlet_qs):
    """Atlet dari form POST. Wajib milik pelatih ini (anti-IDOR)."""
    atlet_id = to_int(request.POST.get('atlet_id'))
    if not atlet_id:
        return None
    return get_object_or_404(atlet_qs, pk=atlet_id)


def _context_list(request, model, extra=None):
    atlet_qs = get_atlet_basket(request.user)
    cat = _kategori_filter(request)
    history = model.objects.filter(atlet__in=atlet_qs).select_related('atlet', 'atlet__pelatih')
    atlet_list = atlet_qs.order_by('nama_atlet')
    if cat:
        history = history.filter(kategori_usia=cat)
        atlet_list = atlet_list.filter(kategori_umur=cat)
    atlet_id = request.GET.get('atlet_id')
    ctx = {
        'history': history.order_by('-timestamp')[:50],
        'atlet_list': atlet_list,
        'selected_category': cat.lower(),
        'atlet_id_terpilih': int(atlet_id) if atlet_id and atlet_id.isdigit() else None,
    }
    ctx.update(extra or {})
    return ctx


def _json_hapus(request, model, pk, label):
    audit = get_object_or_404(model, pk=pk, atlet__in=get_atlet_basket(request.user))
    nama = audit.atlet_name
    audit.delete()
    return JsonResponse({'status': 'success', 'message': f'Data {label} {nama} dihapus.'})


# ══════════════════════════════════════════════════════════════════════
# L1 — CORRECTION (skor dihitung SERVER dari data mentah; JS hanya preview)
# ══════════════════════════════════════════════════════════════════════

class L1CorrectionBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/l1_correction.html'

    def get(self, request):
        return render(request, self.template_name,
                      _context_list(request, BasketL1Correction, {'rubrik_l1': scoring.RUBRIK_L1}))

    def post(self, request):
        try:
            atlet = _atlet_dipilih(request, get_atlet_basket(request.user))
            if not atlet:
                messages.error(request, 'Pilih atlet terlebih dahulu.')
                return redirect('basketball:l1_correction')
            P = request.POST
            kategori, gender = atlet.kategori_umur, atlet.gender      # sumber: data master atlet
            bucket = scoring.tentukan_bucket(P.get('usia_kat_sop'), atlet, kategori)
            f = lambda k: to_float(P.get(k))
            skor = scoring.skor_l1(
                bucket, gender,
                ankle_kiri=f('ankle_kiri_cm'), ankle_kanan=f('ankle_kanan_cm'),
                hip_kiri=f('hip_fleksi_kiri'), hip_kanan=f('hip_fleksi_kanan'),
                shoulder=f('shoulder_fleksi'),
                balance_kiri=f('balance_kiri_detik'), balance_kanan=f('balance_kanan_detik'),
                posture=f('score_posture'),
            )
            audit = BasketL1Correction(
                atlet=atlet, atlet_name=atlet.nama_atlet,
                kategori_usia=kategori, gender=gender, posisi=atlet.posisi or P.get('posisi', ''),
                ankle_kiri_cm=f('ankle_kiri_cm'), ankle_kanan_cm=f('ankle_kanan_cm'),
                hip_fleksi_kiri=f('hip_fleksi_kiri'), hip_fleksi_kanan=f('hip_fleksi_kanan'),
                shoulder_fleksi=f('shoulder_fleksi'),
                balance_kiri_detik=f('balance_kiri_detik'), balance_kanan_detik=f('balance_kanan_detik'),
                catatan=P.get('catatan', ''),
                created_by=request.user.get_full_name() or request.user.username,
                **skor,
            )
            audit.save()
            if audit.layak_naik:
                messages.success(request, f'✅ {audit.atlet_name} — {audit.total_skor} ({audit.predikat}). LAYAK ke L2!')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — {audit.total_skor} ({audit.predikat}). Belum layak ke L2.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('basketball:l1_correction')


@login_required
@require_POST
def hapus_l1_basket(request, pk):
    return _json_hapus(request, BasketL1Correction, pk, 'L1')


# ══════════════════════════════════════════════════════════════════════
# L2 — STRENGTH
# ══════════════════════════════════════════════════════════════════════

class L2StrengthBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/l2_strength.html'

    def get(self, request):
        rubrik = {'tables': scoring.RUBRIK_L2, 'band': scoring.BAND_L2,
                  'youth': scoring.YOUTH_SKOR_L2, 'asym_single_leg': scoring.ASIMETRI_SINGLE_LEG}
        return render(request, self.template_name, _context_list(request, BasketL2Strength, {'rubrik_l2': rubrik}))

    def post(self, request):
        try:
            atlet = _atlet_dipilih(request, get_atlet_basket(request.user))
            if not atlet:
                messages.error(request, 'Pilih atlet terlebih dahulu.')
                return redirect('basketball:l2_strength')
            P = request.POST
            kategori, gender = atlet.kategori_umur, atlet.gender
            bb = to_float(P.get('kelas_berat')) or atlet.kelas_berat
            f = lambda k: to_float(P.get(k))
            skor = scoring.skor_l2(
                kategori, gender, bb=bb, squat_1rm=f('squat_1rm'), bench_1rm=f('bench_1rm'),
                plank=f('plank_detik'), sl_kiri=f('single_leg_squat_kiri'),
                sl_kanan=f('single_leg_squat_kanan'), broad_m=f('broad_jump_m'),
            )
            audit = BasketL2Strength(
                atlet=atlet, atlet_name=atlet.nama_atlet,
                kategori_usia=kategori, gender=gender, posisi=atlet.posisi or P.get('posisi', ''),
                kelas_berat=bb, squat_1rm=f('squat_1rm'), bench_1rm=f('bench_1rm'),
                plank_detik=to_int(P.get('plank_detik')),
                single_leg_squat_kiri=to_int(P.get('single_leg_squat_kiri')),
                single_leg_squat_kanan=to_int(P.get('single_leg_squat_kanan')),
                broad_jump_m=f('broad_jump_m'),
                catatan=P.get('catatan', ''),
                created_by=request.user.get_full_name() or request.user.username,
                **skor,
            )
            audit.save()
            if audit.layak_naik:
                messages.success(request, f'✅ {audit.atlet_name} — {audit.total_skor} ({audit.predikat}). LAYAK ke L3!')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — {audit.total_skor}. Belum layak ke L3.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('basketball:l2_strength')


@login_required
@require_POST
def hapus_l2_basket(request, pk):
    return _json_hapus(request, BasketL2Strength, pk, 'L2')


# ══════════════════════════════════════════════════════════════════════
# L3 — POWER (skor dihitung SERVER dari data mentah; JS hanya preview)
# ══════════════════════════════════════════════════════════════════════

class L3PowerBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/l3_power.html'

    def get(self, request):
        return render(request, self.template_name,
                      _context_list(request, BasketL3Power, {'rubrik_l3': scoring.payload_l3()}))

    def post(self, request):
        try:
            atlet = _atlet_dipilih(request, get_atlet_basket(request.user))
            if not atlet:
                messages.error(request, 'Pilih atlet terlebih dahulu.')
                return redirect('basketball:l3_power')
            P = request.POST
            kategori, gender = atlet.kategori_umur, atlet.gender      # sumber: data master atlet
            f = lambda k: to_float(P.get(k))
            skor = scoring.skor_l3(
                kategori, gender, vj=f('vertical_jump_cm'), sp30=f('sprint_30m_detik'),
                spct=f('sprint_court_detik'), lane=f('lane_agility_detik'),
                rsi=f('rsi_value'), cod=f('cod_detik'),
            )
            vj, reach = f('vertical_jump_cm'), f('standing_reach_cm')
            audit = BasketL3Power(
                atlet=atlet, atlet_name=atlet.nama_atlet,
                kategori_usia=kategori, gender=gender, posisi=atlet.posisi or P.get('posisi', ''),
                vertical_jump_cm=vj, standing_reach_cm=reach,
                max_reach_cm=(vj + reach) if vj and reach else None,
                sprint_30m_detik=f('sprint_30m_detik'), sprint_court_detik=f('sprint_court_detik'),
                lane_agility_detik=f('lane_agility_detik'),
                drop_jump_cm=f('drop_jump_cm'), rsi_value=f('rsi_value'),
                cod_detik=f('cod_detik'),
                catatan=P.get('catatan', ''),
                created_by=request.user.get_full_name() or request.user.username,
                **skor,
            )
            audit.save()
            if audit.layak_naik:
                messages.success(request, f'✅ {audit.atlet_name} — {audit.total_skor} ({audit.predikat}). LAYAK ke L4!')
            elif audit.layak_bertahan:
                messages.info(request, f'ℹ️ {audit.atlet_name} — {audit.total_skor}. Tahan di L3, perkuat pilar terlemah.')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — {audit.total_skor}. Kembali perkuat L2 (Strength).')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('basketball:l3_power')


@login_required
@require_POST
def hapus_l3_basket(request, pk):
    return _json_hapus(request, BasketL3Power, pk, 'L3')


# ══════════════════════════════════════════════════════════════════════
# L4 — SPESIFIK BASKET (skor dihitung SERVER dari data mentah; JS hanya preview)
# ══════════════════════════════════════════════════════════════════════

def _nilai_coach(val):
    """Penilaian coach 0–10: dibatasi ke rentang valid."""
    v = to_float(val)
    return 0 if v is None else max(0.0, min(10.0, v))


class L4SpecificBasketView(LoginRequiredMixin, View):
    template_name = 'basketball/l4_specific.html'

    def get(self, request):
        return render(request, self.template_name,
                      _context_list(request, BasketL4Specific, {'rubrik_l4': scoring.payload_l4()}))

    def post(self, request):
        try:
            atlet = _atlet_dipilih(request, get_atlet_basket(request.user))
            if not atlet:
                messages.error(request, 'Pilih atlet terlebih dahulu.')
                return redirect('basketball:l4_specific')
            P = request.POST
            kategori, gender = atlet.kategori_umur, atlet.gender
            f = lambda k: to_float(P.get(k))
            vision, decision = _nilai_coach(P.get('court_vision_score')), _nilai_coach(P.get('decision_speed'))
            skor = scoring.skor_l4(
                kategori, gender, ft=f('free_throw_pct'), mid=f('midrange_pct'), three=f('three_point_pct'),
                dom=f('dribble_speed_dominant'), weak=f('dribble_speed_weak'),
                lat=f('lateral_speed_detik'), cont=f('contest_rate_pct'), yoyo_m=f('yoyo_jarak_m'),
                vision=vision, decision=decision,
            )
            audit = BasketL4Specific(
                atlet=atlet, atlet_name=atlet.nama_atlet,
                kategori_usia=kategori, gender=gender, posisi=atlet.posisi or P.get('posisi', ''),
                free_throw_pct=f('free_throw_pct'), midrange_pct=f('midrange_pct'), three_point_pct=f('three_point_pct'),
                dribble_speed_dominant=f('dribble_speed_dominant'), dribble_speed_weak=f('dribble_speed_weak'),
                lateral_speed_detik=f('lateral_speed_detik'), contest_rate_pct=f('contest_rate_pct'),
                court_vision_score=vision, decision_speed=decision,
                yoyo_level=to_int(P.get('yoyo_level')), yoyo_jarak_m=f('yoyo_jarak_m'),
                catatan=P.get('catatan', ''),
                created_by=request.user.get_full_name() or request.user.username,
                **skor,
            )
            audit.save()
            if audit.layak_kompetisi:
                messages.success(request, f'🏆 {audit.atlet_name} — {audit.total_skor} ({audit.predikat}). LAYAK KOMPETISI!')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — {audit.total_skor}. Belum siap kompetisi, perbaiki pilar terlemah.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('basketball:l4_specific')


@login_required
@require_POST
def hapus_l4_basket(request, pk):
    return _json_hapus(request, BasketL4Specific, pk, 'L4')