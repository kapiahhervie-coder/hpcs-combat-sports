"""
HPCS Boxing — Views
App mandiri untuk cabang Boxing. Model & permission tetap dipakai bersama
dari app 'combat' (data layer terpusat), sesuai pola yang sudah dipakai
di app 'muaythai'.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
import json

from combat.models import (
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
# DAFTAR ATLET BOXING (khusus lihat daftar, terpisah dari Tambah Atlet)
# ══════════════════════════════════════════════════════════════════════

class DaftarAtletBoxingView(LoginRequiredMixin, View):
    template_name = 'boxing/daftar_atlet.html'

    def get(self, request):
        daftar_atlet = get_atlet_boxing(request.user).order_by('nama_atlet')
        return render(request, self.template_name, {
            'daftar_atlet': daftar_atlet,
            'total_atlet':  daftar_atlet.count(),
        })


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

# ══════════════════════════════════════════════════════════════════════
# L1 — RUBRIK & KALKULASI SKOR OTOMATIS (Boxing)
# Data mentah -> skor 0-10, berdasarkan ambang batas per kategori usia.
# HARUS identik dengan RUBRIK_L1 di l1_correction.html (JS) agar preview
# & hasil simpan konsisten.
# ══════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════
# Ambang batas diambil dari SOP_Rubrik_Asesmen_HPCS_Level1_Revisi1.pdf
# HARUS identik dengan NORMA_ANKLE / NORMA_STABILITY / NORMA_ROTASI di
# l1_correction.html (JS) agar preview & hasil simpan konsisten.
#
# Catatan penyesuaian ke kategori usia aplikasi (JUNIOR/SENIOR/ELITE/YOUTH):
#   - JUNIOR  -> SOP "Remaja (12-17 thn)"
#   - SENIOR/ELITE -> SOP "Dewasa (18-35 thn)"
#   - YOUTH   -> sementara disamakan JUNIOR (belum ada tier SOP khusus)
# ══════════════════════════════════════════════════════════════════════
RUBRIK_L1 = {
    'JUNIOR': {
        # SOP Tabel C: kategori "Semua (12-35 thn)" -> <35° kurang / 35-45° cukup / >45° baik
        'rotation':  [(45, 9.5), (40, 7.5), (35, 5.5)],
        # SOP Tabel B (REVISI 1, tentatif "?"): Remaja <6 / 6-12 / >12 detik
        'balance':   [(12, 9.5), (9, 7.5), (6, 5.5)],
        # SOP Tabel A: Remaja (12-17 thn) Putra/Putri gabung <8 / 8-11 / >11 cm
        'ankle':     [(11, 9.5), (9.5, 7.5), (8, 5.5)],
    },
    'SENIOR': {  # dipakai juga untuk ELITE
        # SOP Tabel C: sama dengan Remaja, karena SOP menggabungkan 12-35 thn jadi satu ambang
        'rotation':  [(45, 9.5), (40, 7.5), (35, 5.5)],
        # SOP Tabel B (REVISI 1): Dewasa L/P digabung <8 / 8-15 / >15 detik
        'balance':   [(15, 9.5), (11.5, 7.5), (8, 5.5)],
        # SOP Tabel A: Dewasa Laki-laki <9 / 9-12 / >12 cm
        'ankle_l':   [(12, 9.5), (10.5, 7.5), (9, 5.5)],
        # SOP Tabel A: Dewasa Perempuan <8 / 8-11 / >11 cm
        'ankle_p':   [(11, 9.5), (9.5, 7.5), (8, 5.5)],
    },
}
RUBRIK_L1['ELITE'] = RUBRIK_L1['SENIOR']
RUBRIK_L1['YOUTH'] = RUBRIK_L1['JUNIOR']  # sementara pakai ambang Remaja, belum ada tier SOP Youth L1

# Penalti asimetri Rotation sesuai SOP Tabel C: selisih sudut Kiri vs Kanan
# > 10° -> skor akhir Rotation dikurangi 2 poin (identik dgn BATAS_ASIMETRI_ROTASI
# & PENALTI_ASIMETRI_ROTASI di JS).
BATAS_ASIMETRI_ROTASI = 10
PENALTI_ASIMETRI_ROTASI = 2


def _kat_l1(kategori_usia):
    """Normalisasi string kategori_usia -> key valid di RUBRIK_L1 (fallback SENIOR)."""
    kat = (kategori_usia or 'ELITE').upper()
    return kat if kat in RUBRIK_L1 else 'SENIOR'


def _tabel_l1(kategori_usia):
    return RUBRIK_L1[_kat_l1(kategori_usia)]


def _skor_dari_ambang(nilai, ambang_list, skor_novice=3.0):
    if nilai is None:
        return None
    for batas, skor in ambang_list:
        if nilai >= batas:
            return skor
    return skor_novice


def hitung_skor_rotation(rotasi_kiri, rotasi_kanan, kategori_usia='ELITE'):
    """Ambil sisi yang LEBIH LEMAH sebagai penentu skor, lalu terapkan
    penalti asimetri SOP (selisih L/R > 10° -> -2 poin, minimum 1.0)."""
    nilai = [v for v in (rotasi_kiri, rotasi_kanan) if v is not None]
    if not nilai:
        return 0
    ambang = _tabel_l1(kategori_usia)['rotation']
    skor = _skor_dari_ambang(min(nilai), ambang) or 0
    if rotasi_kiri is not None and rotasi_kanan is not None:
        if abs(rotasi_kiri - rotasi_kanan) > BATAS_ASIMETRI_ROTASI:
            skor = max(1.0, skor - PENALTI_ASIMETRI_ROTASI)
    return skor


def hitung_skor_stability(balance_kiri, balance_kanan, plank_hold_detik, kategori_usia='ELITE'):
    """Gabungan Single Leg Balance (sisi terlemah, bobot 70%) + Core Plank Hold (bobot 30%)."""
    nilai_balance = [v for v in (balance_kiri, balance_kanan) if v is not None]
    if not nilai_balance:
        return 0
    ambang = _tabel_l1(kategori_usia)['balance']
    skor_balance = _skor_dari_ambang(min(nilai_balance), ambang) or 3.0

    if plank_hold_detik is None:
        return skor_balance

    if plank_hold_detik >= 60:
        skor_plank = 9.5
    elif plank_hold_detik >= 45:
        skor_plank = 7.5
    elif plank_hold_detik >= 25:
        skor_plank = 5.5
    else:
        skor_plank = 3.0

    return round(skor_balance * 0.7 + skor_plank * 0.3, 1)


def hitung_skor_ankle(ankle_kiri, ankle_kanan, kategori_usia='ELITE', gender='Putra'):
    nilai = [v for v in (ankle_kiri, ankle_kanan) if v is not None]
    if not nilai:
        return 0
    kat = _kat_l1(kategori_usia)
    tabel = RUBRIK_L1[kat]
    if kat in ('SENIOR', 'ELITE'):
        # SOP Tabel A membedakan Dewasa Laki-laki vs Perempuan
        ambang = tabel['ankle_p'] if gender == 'Putri' else tabel['ankle_l']
    else:
        ambang = tabel['ankle']
    return _skor_dari_ambang(min(nilai), ambang) or 0


# ══════════════════════════════════════════════════════════════════════
# Extension (Modified Cobra), Posture (Plumb Line) & Breathing (Hi-Lo Test)
# sifatnya MURNI KUALITATIF sesuai SOP — pelatih memilih kondisi hasil
# observasi langsung dari dropdown (Baik=9 / Cukup=6 / Kurang=3), BUKAN
# dihitung dari angka pengukuran. Server hanya memvalidasi & mengunci
# rentang skornya (0-10), tidak menghitung ulang dari data mentah, karena
# memang tidak ada data mentah numerik untuk 3 pilar ini.
# ══════════════════════════════════════════════════════════════════════
def hitung_skor_kualitatif(nilai_pilihan):
    if nilai_pilihan is None:
        return 0
    try:
        v = float(nilai_pilihan)
    except (TypeError, ValueError):
        return 0
    return round(max(0.0, min(10.0, v)), 1)


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
            atlet = get_object_or_404(get_atlet_boxing(request.user), pk=atlet_id) if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                if val in (None, ''):
                    return None
                val = str(val).strip().replace(',', '.')  # dukung input format ID (koma desimal)
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None

            def to_int(key):
                val = request.POST.get(key)
                try:
                    return int(val) if val not in (None, '') else None
                except (ValueError, TypeError):
                    return None

            kategori_usia = request.POST.get('kategori_usia', 'ELITE')
            gender        = request.POST.get('gender', 'Putra')

            rotasi_kiri  = to_float('rotasi_kiri_derajat')
            rotasi_kanan = to_float('rotasi_kanan_derajat')

            balance_kiri  = to_float('balance_kiri_detik')
            balance_kanan = to_float('balance_kanan_detik')
            plank_hold    = to_float('plank_hold_detik')

            ankle_kiri  = to_float('ankle_kiri_cm')
            ankle_kanan = to_float('ankle_kanan_cm')

            # Pilar kualitatif (SOP): pelatih pilih kondisi di dropdown, JS
            # (calcExtension/calcPosture/calcBreathing) mengirim skornya
            # langsung lewat field skor_extension/skor_posture/skor_breathing.
            skor_extension_input = to_float('skor_extension')
            skor_posture_input   = to_float('skor_posture')
            skor_breathing_input = to_float('skor_breathing')

            # NOTE: semua score_* di bawah SENGAJA dihitung ulang di server
            # dari data mentah, TIDAK diambil dari request.POST — sama
            # seperti pola di L2/L3/L4. Nilai final yang tersimpan selalu
            # hasil kalkulasi server, bukan input pelatih/JS.
            #
            # PENTING: combat.CorrectionAuditL1 adalah model BERSAMA lintas
            # cabang (boxing/muaythai/karate/taekwondo) dan TIDAK menyimpan
            # data pengukuran mentah (rotasi_kiri_derajat, balance_*_detik,
            # ankle_*_cm, dst) — field itu HANYA dipakai di sisi form/JS
            # untuk menghitung skor, lalu dibuang. Yang disimpan cuma hasil
            # skor per pilar (score_rotation, score_ankle, dst).
            audit = CorrectionAuditL1(
                atlet=atlet,
                atlet_name=atlet.nama_atlet if atlet else request.POST.get('atlet_name', ''),
                kategori_usia=kategori_usia,
                gender=gender,
                kelas_berat=to_float('kelas_berat'),

                score_rotation=hitung_skor_rotation(rotasi_kiri, rotasi_kanan, kategori_usia),
                score_extension=hitung_skor_kualitatif(skor_extension_input),
                score_stability=hitung_skor_stability(balance_kiri, balance_kanan, plank_hold, kategori_usia),
                score_ankle=hitung_skor_ankle(ankle_kiri, ankle_kanan, kategori_usia, gender),
                score_posture=hitung_skor_kualitatif(skor_posture_input),
                score_breathing=hitung_skor_kualitatif(skor_breathing_input),

                ai_confidence_score=to_float('ai_confidence_score'),
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


@login_required
def hapus_l1_audit(request, pk):
    audit = get_object_or_404(CorrectionAuditL1, pk=pk, atlet__in=get_atlet_boxing(request.user))
    nama = audit.atlet_name
    audit.delete()
    messages.success(request, f"Data L1 {nama} berhasil dihapus.")
    return redirect('boxing:l1_correction')


@login_required
def detail_l1_audit(request, pk):
    audit = get_object_or_404(CorrectionAuditL1, pk=pk, atlet__in=get_atlet_boxing(request.user))
    return JsonResponse({
        'atlet_name': audit.atlet_name,
        'kategori_usia': audit.kategori_usia,
        'gender': audit.gender,
        'kelas_berat': audit.kelas_berat,
        'score_rotation': audit.score_rotation,
        'score_extension': audit.score_extension,
        'score_stability': audit.score_stability,
        'score_ankle': audit.score_ankle,
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
            atlet = get_object_or_404(get_atlet_boxing(request.user), pk=atlet_id) if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                if not val: return None
                try: return float(str(val).replace(',', '.').strip())
                except: return None

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
                score_lower=float(str(request.POST.get('score_lower', 0) or 0).replace(',', '.')),
                push_5rm_beban=to_float('push_5rm_beban'),
                score_push=float(str(request.POST.get('score_push', 0) or 0).replace(',', '.')),
                pull_reps=to_int('pull_reps'),
                score_pull=float(str(request.POST.get('score_pull', 0) or 0).replace(',', '.')),
                core_durasi_detik=to_int('core_durasi_detik'),
                score_core=float(str(request.POST.get('score_core', 0) or 0).replace(',', '.')),
                iso_durasi_detik=to_int('iso_durasi_detik'),
                iso_tremor_onset_detik=to_int('iso_tremor_onset_detik'),
                score_isometric=float(str(request.POST.get('score_isometric', 0) or 0).replace(',', '.')),
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


@login_required
def hapus_l2_audit(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk, atlet__in=get_atlet_boxing(request.user))
    nama = audit.atlet_name
    audit.delete()
    messages.success(request, f"Data L2 {nama} berhasil dihapus.")
    return redirect('boxing:l2_strength')


@login_required
def detail_l2_audit(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk, atlet__in=get_atlet_boxing(request.user))
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
            atlet = get_object_or_404(get_atlet_boxing(request.user), pk=atlet_id) if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                if not val: return None
                try: return float(str(val).replace(',', '.').strip())
                except: return None

            audit = PowerAuditL3(
                atlet=atlet,
                atlet_name=request.POST.get('atlet_name', ''),
                kategori_usia=request.POST.get('kategori_usia', 'ELITE'),
                gender=request.POST.get('gender', 'Putra'),
                kelas_berat=to_float('kelas_berat'),
                score_jump=float(str(request.POST.get('score_jump', 0) or 0).replace(',', '.')),
                score_sprint=float(str(request.POST.get('score_sprint', 0) or 0).replace(',', '.')),
                score_throw=float(str(request.POST.get('score_throw', 0) or 0).replace(',', '.')),
                score_rsi=float(str(request.POST.get('score_rsi', 0) or 0).replace(',', '.')),
                score_agility=float(str(request.POST.get('score_agility', 0) or 0).replace(',', '.')),
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


@login_required
def hapus_l3_audit(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk, atlet__in=get_atlet_boxing(request.user))
    nama = audit.atlet_name
    audit.delete()
    messages.success(request, f"Data L3 {nama} berhasil dihapus.")
    return redirect('boxing:l3_power')


@login_required
def detail_l3_audit(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk, atlet__in=get_atlet_boxing(request.user))
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
            atlet = get_object_or_404(get_atlet_boxing(request.user), pk=atlet_id) if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                if not val: return None
                try: return float(str(val).replace(',', '.').strip())
                except: return None

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


@login_required
def hapus_l4_audit(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk, atlet__in=get_atlet_boxing(request.user))
    nama = audit.atlet_name
    audit.delete()
    messages.success(request, f"Data L4 {nama} berhasil dihapus.")
    return redirect('boxing:l4_speed_agility')


@login_required
def detail_l4_audit(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk, atlet__in=get_atlet_boxing(request.user))
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