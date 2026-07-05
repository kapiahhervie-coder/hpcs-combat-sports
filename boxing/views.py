"""
HPCS Boxing — Views
App mandiri untuk cabang Boxing. Model & permission tetap dipakai bersama
dari app 'combat' (data layer terpusat), sesuai pola yang sudah dipakai
di app 'muaythai'.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
import json

from boxing.models import (
    Atlet,
    CorrectionAuditL1,
    StrengthAuditL2,
    PowerAuditL3,
    SpeedAgilityAuditL4,
)
from combat.permissions import get_atlet_queryset  # ini boleh tetap dari combat, karena memang fungsi bersama


def get_atlet_boxing(user):
    """
    Sama seperti get_atlet_muaythai() di app muaythai — memastikan
    semua view/audit di app 'boxing' HANYA melihat atlet cabang Boxing.
    """
    return get_atlet_queryset(user).filter(cabang='boxing')


# ══════════════════════════════════════════════════════════════════════
# DASHBOARD BOXING
# ══════════════════════════════════════════════════════════════════════

class DashboardBoxingView(LoginRequiredMixin, View):
    template_name = 'boxing/dashboard_boxing.html'

    def get(self, request):
        atlet_id = request.GET.get('atlet_id')
        daftar_atlet = get_atlet_boxing(request.user).order_by('nama_atlet')

        if atlet_id:
            atlet = daftar_atlet.filter(id=atlet_id).first()
        else:
            atlet = daftar_atlet.first()

        score_labels = []
        score_data = []

        if atlet:
            riwayat = CorrectionAuditL1.objects.filter(
                atlet=atlet
            ).order_by('timestamp')[:8]

            for r in riwayat:
                score_labels.append(r.timestamp.strftime('%d/%m'))
                score_data.append(float(r.total_skor))

        if not score_data:
            score_labels = ['—']
            score_data = [0]

        context = {
            'atlet': atlet,
            'daftar_atlet': daftar_atlet,
            'score_labels': json.dumps(score_labels),
            'score_data': json.dumps(score_data),
            'training_load': 0,
        }
        return render(request, self.template_name, context)


# ══════════════════════════════════════════════════════════════════════
# L1 — CORRECTION (Boxing)
# ══════════════════════════════════════════════════════════════════════

class L1CorrectionView(LoginRequiredMixin, View):
    template_name = 'boxing/l1_correction.html'

    def get(self, request):
        atlet_qs = get_atlet_boxing(request.user)
        history = CorrectionAuditL1.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        atlet_list = atlet_qs.order_by('nama_atlet')
        return render(request, self.template_name, {
            'history': history,
            'atlet_list': atlet_list,
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet = get_object_or_404(Atlet, pk=atlet_id, cabang='boxing') if atlet_id else None

            audit = CorrectionAuditL1(
                atlet=atlet,
                atlet_name=atlet.nama_atlet if atlet else request.POST.get('atlet_name', ''),
                kategori_usia=request.POST.get('kategori_usia', 'ELITE'),
                gender=request.POST.get('gender', 'Putra'),
                kelas_berat=request.POST.get('kelas_berat') or None,
                score_rotation=round((float(request.POST.get('score_rotation', 0) or 0) + float(request.POST.get('score_rotation_r', 0) or 0)) / 2, 2),
                score_extension=float(request.POST.get('score_extension', 0) or 0),
                score_stability=round((float(request.POST.get('score_stability', 0) or 0) + float(request.POST.get('score_stability_r', 0) or 0)) / 2, 2),
                score_posture=float(request.POST.get('score_posture', 0) or 0),
                score_breathing=float(request.POST.get('score_breathing', 0) or 0),
                ai_confidence_score=request.POST.get('ai_confidence_score') or None,
            )
            audit.save()

            if audit.layak_naik:
                messages.success(request, f"✅ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). LAYAK naik ke L2!")
            else:
                messages.warning(request, f"⚠️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). Belum layak ke L2.")

        except Exception as e:
            print(f"‼️ ERROR L1 SAVE: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error menyimpan data: {e}")

        return redirect('boxing:l1_correction')


def hapus_l1_audit(request, pk):
    audit = get_object_or_404(CorrectionAuditL1, pk=pk, atlet__cabang='boxing')
    nama = audit.atlet_name
    audit.delete()
    messages.success(request, f"Data L1 {nama} berhasil dihapus.")
    return redirect('boxing:l1_correction')


def detail_l1_audit(request, pk):
    audit = get_object_or_404(CorrectionAuditL1, pk=pk, atlet__cabang='boxing')
    return JsonResponse({
        'atlet_name': audit.atlet_name,
        'kategori_usia': audit.kategori_usia,
        'gender': audit.gender,
        'kelas_berat': audit.kelas_berat,
        'score_rotation': audit.score_rotation,
        'score_extension': audit.score_extension,
        'score_stability': audit.score_stability,
        'score_posture': audit.score_posture,
        'score_breathing': audit.score_breathing,
        'total_skor': audit.total_skor,
        'predikat': audit.predikat,
        'layak_naik': audit.layak_naik,
    })


# ══════════════════════════════════════════════════════════════════════
# L2 — STRENGTH (Boxing)
# ══════════════════════════════════════════════════════════════════════

class L2StrengthView(LoginRequiredMixin, View):
    template_name = 'boxing/l2_strenght.html'

    def get(self, request):
        atlet_qs = get_atlet_boxing(request.user)
        history = StrengthAuditL2.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        atlet_list = atlet_qs.order_by('nama_atlet')
        return render(request, self.template_name, {
            'history': history,
            'atlet_list': atlet_list,
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet = get_object_or_404(Atlet, pk=atlet_id, cabang='boxing') if atlet_id else None

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
                ai_rep_count_lower=to_int('ai_rep_count_lower'),
                ai_rep_count_push=to_int('ai_rep_count_push'),
                ai_rep_count_pull=to_int('ai_rep_count_pull'),
                ai_confidence_score=to_float('ai_confidence_score'),
            )
            audit.save()

            if audit.layak_naik:
                messages.success(request, f"✅ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}) | LAYAK naik ke L3!")
            else:
                messages.warning(request, f"⚠️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). Belum layak ke L3.")

        except Exception as e:
            print(f"‼️ ERROR L2 SAVE: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error menyimpan data: {e}")

        return redirect('boxing:l2_strength')


def hapus_l2_audit(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk, atlet__cabang='boxing')
    nama = audit.atlet_name
    audit.delete()
    messages.success(request, f"Data L2 {nama} berhasil dihapus.")
    return redirect('boxing:l2_strength')


def detail_l2_audit(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk, atlet__cabang='boxing')
    return JsonResponse({
        'atlet_name': audit.atlet_name,
        'kategori_usia': audit.kategori_usia,
        'gender': audit.gender,
        'kelas_berat': audit.kelas_berat,
        'score_lower': audit.score_lower,
        'score_push': audit.score_push,
        'score_pull': audit.score_pull,
        'score_core': audit.score_core,
        'score_isometric': audit.score_isometric,
        'iso_tremor_rasio': audit.iso_tremor_rasio,
        'total_skor': audit.total_skor,
        'predikat': audit.predikat,
        'layak_naik': audit.layak_naik,
        'cns_status': audit.cns_status,
        'rekomendasi': audit.rekomendasi_auto,
    })


# ══════════════════════════════════════════════════════════════════════
# L3 — POWER (Boxing)
# ══════════════════════════════════════════════════════════════════════

class L3PowerView(LoginRequiredMixin, View):
    template_name = 'boxing/l3_power.html'

    def get(self, request):
        atlet_qs = get_atlet_boxing(request.user)
        history = PowerAuditL3.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        atlet_list = atlet_qs.order_by('nama_atlet')
        return render(request, self.template_name, {
            'history': history,
            'atlet_list': atlet_list,
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet = get_object_or_404(Atlet, pk=atlet_id, cabang='boxing') if atlet_id else None

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
                messages.success(request, f"🏆 {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). LAYAK KOMPETISI!")
            elif audit.layak_bertahan:
                messages.info(request, f"ℹ️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). Layak bertahan di L3.")
            else:
                messages.warning(request, f"⚠️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). {audit.alasan_tidak_layak}")

        except Exception as e:
            print(f"‼️ ERROR L3 SAVE: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error menyimpan data: {e}")

        return redirect('boxing:l3_power')


def hapus_l3_audit(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk, atlet__cabang='boxing')
    nama = audit.atlet_name
    audit.delete()
    messages.success(request, f"Data L3 {nama} berhasil dihapus.")
    return redirect('boxing:l3_power')


def detail_l3_audit(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk, atlet__cabang='boxing')
    return JsonResponse({
        'atlet_name': audit.atlet_name,
        'kategori_usia': audit.kategori_usia,
        'gender': audit.gender,
        'kelas_berat': audit.kelas_berat,
        'score_jump': audit.score_jump,
        'score_sprint': audit.score_sprint,
        'score_throw': audit.score_throw,
        'score_rsi': audit.score_rsi,
        'score_agility': audit.score_agility,
        'rsi_value': audit.rsi_value,
        'total_skor': audit.total_skor,
        'predikat': audit.predikat,
        'layak_naik': audit.layak_naik,
        'layak_bertahan': audit.layak_bertahan,
        'rekomendasi': audit.rekomendasi_auto,
    })


# ══════════════════════════════════════════════════════════════════════
# L4 — SPEED, AGILITY & METABOLIC ENDURANCE (Boxing)
# ══════════════════════════════════════════════════════════════════════

# Tabel konversi level-shuttle ke jarak (meter), protokol standar Yo-Yo IR1.
# HARUS identik dengan YOYO_JARAK di l4_speed_agility.html (JS) agar hasil konsisten.
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


def hitung_skor_hex(hex1, hex2, hex3):
    """Rata-rata 3 putaran hexagon jump -> skor 0-10. Cermin dari calcHex() di JS."""
    nilai = [v for v in (hex1, hex2, hex3) if v is not None and v > 0]
    if not nilai:
        return 0, None
    avg = round(sum(nilai) / len(nilai), 2)
    if avg < 10:    skor = 10
    elif avg < 10.5: skor = 9
    elif avg < 11:   skor = 8
    elif avg < 11.5: skor = 7
    elif avg < 12:   skor = 6
    elif avg < 13:   skor = 5
    elif avg < 14:   skor = 4
    else:            skor = 3
    return skor, avg


def hitung_skor_punch(punch_freq, postur_ok):
    """Jumlah pukulan/10 detik -> skor 0-10, dikurangi 1 jika postur tidak benar.
    Cermin dari autoScorePunch() di JS."""
    if not punch_freq:
        return 0
    p = punch_freq
    if p >= 25:   skor = 10
    elif p >= 22: skor = 9
    elif p >= 20: skor = 8
    elif p >= 18: skor = 7
    elif p >= 16: skor = 6
    elif p >= 14: skor = 5
    elif p >= 12: skor = 4
    else:         skor = 3
    if not postur_ok:
        skor = max(0, skor - 1)
    return skor


def hitung_skor_yoyo(level, shuttle, jarak_manual):
    """Level & shuttle (atau jarak manual) -> estimasi VO2 Max -> skor 0-10.
    Cermin dari calcYoYo()/calcVO2Max() di JS."""
    jarak = jarak_manual
    if level and shuttle:
        jarak = YOYO_JARAK_TABLE.get(level, {}).get(shuttle)
        if jarak is None:
            jarak = level * shuttle * 20  # estimasi kasar, sama seperti fallback JS
    if not jarak or jarak <= 0:
        return 0, None
    vo2 = round((jarak * 0.0084) + 36.4, 1)
    if vo2 >= 60:   skor = 10
    elif vo2 >= 57: skor = 9
    elif vo2 >= 55: skor = 8
    elif vo2 >= 52: skor = 7
    elif vo2 >= 50: skor = 6
    elif vo2 >= 47: skor = 5
    elif vo2 >= 44: skor = 4
    else:           skor = 3
    return skor, vo2


class L4SpeedAgilityView(LoginRequiredMixin, View):
    template_name = 'boxing/l4_speed_agility.html'

    def get(self, request):
        atlet_qs = get_atlet_boxing(request.user)
        history = SpeedAgilityAuditL4.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        atlet_list = atlet_qs.order_by('nama_atlet')
        return render(request, self.template_name, {
            'history': history,
            'atlet_list': atlet_list,
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet = get_object_or_404(Atlet, pk=atlet_id, cabang='boxing') if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                try:
                    return float(val) if val else None
                except (ValueError, TypeError):
                    return None

            def to_int(key):
                val = request.POST.get(key)
                try:
                    return int(val) if val else None
                except (ValueError, TypeError):
                    return None

            hex1 = to_float('hex_waktu_putaran1')
            hex2 = to_float('hex_waktu_putaran2')
            hex3 = to_float('hex_waktu_putaran3')
            score_hex, hex_avg = hitung_skor_hex(hex1, hex2, hex3)

            punch_freq = to_int('punch_freq_10s')
            punch_postur_ok = request.POST.get('punch_postur_ok') == 'true'
            score_punch = hitung_skor_punch(punch_freq, punch_postur_ok)

            yoyo_level = to_int('yoyo_level_tercapai')
            yoyo_shuttle = to_int('yoyo_shuttle_tercapai')
            yoyo_jarak_input = to_float('yoyo_total_jarak_m')
            score_yoyo, vo2_estimasi = hitung_skor_yoyo(yoyo_level, yoyo_shuttle, yoyo_jarak_input)

            # NOTE: score_hex, score_punch, score_yoyo SENGAJA dihitung ulang di sini
            # dan TIDAK diambil dari request.POST. Field skor di form hanya untuk
            # ditampilkan (readonly) — nilai final yang tersimpan selalu hasil
            # kalkulasi server, bukan input pelatih. Ini mencegah skor salah/kosong
            # kalau JS di browser gagal jalan.
            audit = SpeedAgilityAuditL4(
                atlet=atlet,
                atlet_name=request.POST.get('atlet_name', ''),
                kategori_usia=request.POST.get('kategori_usia', 'ELITE'),
                gender=request.POST.get('gender', 'Putra'),
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
                yoyo_total_jarak_m=yoyo_jarak_input if yoyo_jarak_input else (
                    YOYO_JARAK_TABLE.get(yoyo_level, {}).get(yoyo_shuttle) if yoyo_level and yoyo_shuttle else None
                ),
                score_yoyo=score_yoyo,
                kondisi_uji=request.POST.get('kondisi_uji', 'FRESH'),
                catatan=request.POST.get('catatan', ''),
            )
            audit.save()

            if audit.layak_kompetisi:
                messages.success(request, f"✅ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). LAYAK KOMPETISI!")
            elif audit.layak_bertahan:
                messages.info(request, f"ℹ️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). Layak bertahan di L4.")
            else:
                messages.warning(request, f"⚠️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.predikat}). {audit.alasan_tidak_layak}")

        except Exception as e:
            print(f"‼️ ERROR L4 SAVE: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error menyimpan data: {e}")

        return redirect('boxing:l4_speed_agility')


def hapus_l4_audit(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk, atlet__cabang='boxing')
    nama = audit.atlet_name
    audit.delete()
    messages.success(request, f"Data L4 {nama} berhasil dihapus.")
    return redirect('boxing:l4_speed_agility')


def detail_l4_audit(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk, atlet__cabang='boxing')
    return JsonResponse({
        'atlet_name': audit.atlet_name,
        'kategori_usia': audit.kategori_usia,
        'gender': audit.gender,
        'kelas_berat': audit.kelas_berat,
        'hex_waktu_rata': audit.hex_waktu_rata,
        'score_hex': audit.score_hex,
        'punch_freq_10s': audit.punch_freq_10s,
        'punch_reaction_time': audit.punch_reaction_time_ms,
        'score_punch': audit.score_punch,
        'yoyo_total_jarak_m': audit.yoyo_total_jarak_m,
        'yoyo_vo2max': audit.yoyo_vo2max_estimasi,
        'score_yoyo': audit.score_yoyo,
        'total_skor': audit.total_skor,
        'predikat': audit.predikat,
        'rekomendasi': audit.rekomendasi_auto,
    })