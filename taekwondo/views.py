import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from .models import CorrectionAuditL1TKD
from combat.models import (
    Atlet,
    StrengthAuditL2,
    PowerAuditL3,
    SpeedAgilityAuditL4,
    CorrectionAuditL1,   # placeholder generik — lihat catatan #3 di atas
)

CABANG_TKD = 'tkd'  # value asli di CABANG_CHOICES (combat/models.py), bukan 'taekwondo'


def get_atlet_taekwondo(user):
    qs = Atlet.objects.filter(cabang=CABANG_TKD)
    if user.is_superuser or user.is_staff:
        return qs
    return qs.filter(pelatih=user)


# ══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════

class DashboardTaekwondoView(LoginRequiredMixin, View):
    template_name = 'taekwondo/dashboard_taekwondo.html'

    def get(self, request):
        atlet_id     = request.GET.get('atlet_id')
        daftar_atlet = get_atlet_taekwondo(request.user).order_by('nama_atlet')
        atlet = daftar_atlet.filter(id=atlet_id).first() if atlet_id else daftar_atlet.first()

        score_labels, score_data = [], []
        if atlet:
            riwayat = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('timestamp')[:8]
            for r in riwayat:
                score_labels.append(r.timestamp.strftime('%d/%m'))
                score_data.append(float(r.total_skor))

        if not score_data:
            score_labels = ['-']
            score_data   = [0]

        l1_last = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first() if atlet else None
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

class DaftarAtletTaekwondoView(LoginRequiredMixin, View):
    template_name = 'taekwondo/daftar_atlet.html'

    def get(self, request):
        daftar_atlet = get_atlet_taekwondo(request.user).order_by('nama_atlet')
        return render(request, self.template_name, {
            'daftar_atlet': daftar_atlet,
            'total_atlet':  daftar_atlet.count(),
        })


# ══════════════════════════════════════════════════════════════════════
# L1 — SCREENING BIOMEKANIK (Taekwondo)
# SOP & Rubrik HPCS Level 1 Taekwondo — Revisi Final 2026
# ══════════════════════════════════════════════════════════════════════
#
# 9 bagian rubrik: A) Ankle WBLT, B) Static Balance (SLST mata tertutup),
# C) Dynamic Balance (YBT-LQ, asimetri Anterior), D) Seated Trunk Rotation,
# E) Hip Internal Rotation, F) Hip External Rotation, G) Lumbar Extension
# Clearing (safety gate), H) Fixed Plumb Line Posture (observasional),
# I) Hi-Lo Breathing (observasional). Angka HARUS identik dengan
# RUBRIK_L1_JS di taekwondo/l1_correction.html.
#
# ⚠️ SOP memakai 3 kategori usia (Anak 6-11 / Remaja 12-17 / Dewasa 18-35),
# BUKAN kategori usia app ini (kemungkinan YOUTH/JUNIOR/SENIOR/ELITE dari
# KATEGORI_USIA_CHOICES combat/models.py — field itu TIDAK diubah supaya
# tidak mengganggu L2/L3/L4). Pemetaan yang dipakai (lihat _band_usia_l1):
# YOUTH -> ANAK, JUNIOR -> REMAJA, SENIOR & ELITE -> DEWASA. Ini ASUMSI —
# ganti mapping-nya di sini kalau Coach Fanny konfirmasi beda.
#
# Semua rubrik SOP ini 3 tingkat (Kurang 1-4 / Cukup 5-7 / Baik 8-10), beda
# dari L2/L3/L4 yang 4 tingkat — representasi skor numerik per tingkat:
# Baik->9.5, Cukup->6, Kurang->2.5 (skor 0 kalau data kosong).
RUBRIK_L1 = {
    'ANAK': {
        'ankle':    [(9, 9.5), (7, 6)],
        'balance':  [(10, 9.5), (5, 6)],
        # Y-Balance anak: SOP tidak beri norma numerik ("Observasi kualitatif"
        # di semua tingkat) — dipakai skor netral non-gating, lihat catatan
        # di hitung_skor_l1_ybalance().
    },
    'REMAJA': {
        'ankle':    [(11, 9.5), (8, 6)],
        'balance':  [(12, 9.5), (7, 6)],
        'ybalance': [(2, 9.5), (4, 6)],  # asimetri ANT (cm), makin kecil makin baik
    },
    'DEWASA': {
        'ankle':    [(12, 9.5), (9, 6)],
        'balance':  [(15, 9.5), (8, 6)],
        'ybalance': [(2, 9.5), (4, 6)],
    },
}
# Trunk Rotation & Hip IR/ER: SOP TIDAK menstratifikasi per usia untuk
# item-item ini (satu tabel umum) — dipakai sama untuk ANAK/REMAJA/DEWASA.
ROM_TUNGGAL_ROTASI = [(45, 9.5), (35, 6)]        # trunk rotation (derajat), makin besar makin baik
ROM_TUNGGAL_HIP    = [(40, 9.5), (30, 6)]        # hip IR/ER (derajat), makin besar makin baik
ASIMETRI_ROTASI    = [(5, 9.5), (10, 6)]         # asimetri kanan-kiri (derajat), makin kecil makin baik


def _band_usia_l1(kategori_usia):
    """Peta kategori usia app (YOUTH/JUNIOR/SENIOR/ELITE) -> band SOP
    (ANAK/REMAJA/DEWASA). Lihat catatan pemetaan di kepala file ini."""
    kat = (kategori_usia or 'ELITE').upper()
    if kat == 'YOUTH':
        return 'ANAK'
    if kat == 'JUNIOR':
        return 'REMAJA'
    return 'DEWASA'  # SENIOR, ELITE, atau fallback


def _skor_dari_ambang(nilai, ambang, kecil_lebih_baik=False):
    """Cocokkan satu nilai mentah ke rubrik SOP 3-tingkat (batas, skor).
    Skor 0 kalau tidak ada data, fallback 2.5 (Kurang) kalau ada data tapi
    di bawah/di atas semua ambang."""
    if nilai is None or nilai <= 0:
        return 0
    for batas, skor in ambang:
        if (nilai <= batas) if kecil_lebih_baik else (nilai >= batas):
            return skor
    return 2.5


def _rata2(*nilai):
    vals = [v for v in nilai if v is not None]
    return sum(vals) / len(vals) if vals else None


def hitung_skor_l1_ankle(kanan_cm, kiri_cm, kategori_usia='ELITE'):
    """A. WBLT — rata-rata kanan/kiri (cm), makin besar makin baik."""
    band = _band_usia_l1(kategori_usia)
    nilai = _rata2(kanan_cm, kiri_cm)
    return _skor_dari_ambang(nilai, RUBRIK_L1[band]['ankle'])


def hitung_skor_l1_balance(kanan_detik, kiri_detik, kategori_usia='ELITE'):
    """B. SLST mata tertutup — rata-rata waktu terbaik kanan/kiri (detik)."""
    band = _band_usia_l1(kategori_usia)
    nilai = _rata2(kanan_detik, kiri_detik)
    return _skor_dari_ambang(nilai, RUBRIK_L1[band]['balance'])


def hitung_skor_l1_ybalance(ant_kanan, ant_kiri, kategori_usia='ELITE'):
    """C. YBT-LQ — skor berbasis asimetri jangkauan Anterior kanan-kiri
    (cm), makin kecil makin baik. Kategori Anak <12 tahun: SOP tidak
    memberi ambang numerik ("Observasi kualitatif" di semua tingkat),
    jadi dipakai skor netral 6.0 non-gating kalau ada data, 0 kalau
    belum diukur sama sekali — TIDAK memaksa gagal/lulus dari angka ini."""
    band = _band_usia_l1(kategori_usia)
    if ant_kanan is None or ant_kiri is None:
        return 0
    if band == 'ANAK':
        return 6.0
    asimetri = abs(ant_kanan - ant_kiri)
    return _skor_dari_ambang(asimetri if asimetri > 0 else 0.01, RUBRIK_L1[band]['ybalance'], kecil_lebih_baik=True)


def hitung_skor_l1_trunk_rotation(kanan_derajat, kiri_derajat):
    """D. Seated Trunk Rotation — nilai terendah antara skor ROM
    rata-rata (makin besar makin baik) dan skor asimetri kanan-kiri
    (makin kecil makin baik), sesuai 2 baris rubrik SOP (ROM & asimetri).
    Tidak distratifikasi usia (satu tabel umum SOP)."""
    rom = _rata2(kanan_derajat, kiri_derajat)
    skor_rom = _skor_dari_ambang(rom, ROM_TUNGGAL_ROTASI)
    if kanan_derajat is None or kiri_derajat is None:
        return skor_rom
    asimetri = abs(kanan_derajat - kiri_derajat)
    skor_asimetri = _skor_dari_ambang(asimetri if asimetri > 0 else 0.01, ASIMETRI_ROTASI, kecil_lebih_baik=True)
    return min(skor_rom, skor_asimetri) if skor_rom and skor_asimetri else (skor_rom or skor_asimetri)


def _hitung_skor_l1_hip_rom(kanan_derajat, kiri_derajat):
    """Dipakai bersama oleh Hip IR & Hip ER — sama seperti trunk rotation:
    nilai terendah antara ROM rata-rata & asimetri kanan-kiri."""
    rom = _rata2(kanan_derajat, kiri_derajat)
    skor_rom = _skor_dari_ambang(rom, ROM_TUNGGAL_HIP)
    if kanan_derajat is None or kiri_derajat is None:
        return skor_rom
    asimetri = abs(kanan_derajat - kiri_derajat)
    skor_asimetri = _skor_dari_ambang(asimetri if asimetri > 0 else 0.01, ASIMETRI_ROTASI, kecil_lebih_baik=True)
    return min(skor_rom, skor_asimetri) if skor_rom and skor_asimetri else (skor_rom or skor_asimetri)


def hitung_skor_l1_hip_ir(kanan_derajat, kiri_derajat):
    """E. Seated Hip Internal Rotation — dinilai TERPISAH dari ER."""
    return _hitung_skor_l1_hip_rom(kanan_derajat, kiri_derajat)


def hitung_skor_l1_hip_er(kanan_derajat, kiri_derajat):
    """F. Seated Hip External Rotation — dinilai TERPISAH dari IR."""
    return _hitung_skor_l1_hip_rom(kanan_derajat, kiri_derajat)


def hitung_skor_l1_lumbar(status):
    """G. Lumbar Extension Clearing — NYERI wajib skor 0 (safety override,
    ditangani sebagai status_keputusan=MERAH di models.py, BUKAN cuma
    skor rendah biasa)."""
    return {'NYERI': 0, 'TERBATAS': 6, 'MULUS': 9.5}.get(status, 0)


def hitung_skor_l1_postur(status):
    """H. Fixed Plumb Line Posture — observasional, bukan diagnosis."""
    return {'DEVIASI_JELAS': 2.5, 'DEVIASI_RINGAN': 6, 'TANPA_DEVIASI': 9.5}.get(status, 0)


def hitung_skor_l1_napas(status):
    """I. Hi-Lo Breathing — observasional, bukan diagnosis fungsi diafragma."""
    return {'DADA_DOMINAN': 2.5, 'CAMPURAN': 6, 'ABDOMINAL_DOMINAN': 9.5}.get(status, 0)


class L1CorrectionTKDView(LoginRequiredMixin, View):
    template_name = 'taekwondo/l1_correction.html'

    def get(self, request):
        atlet_qs   = get_atlet_taekwondo(request.user)
        history    = CorrectionAuditL1TKD.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        atlet_list = atlet_qs.order_by('nama_atlet')
        return render(request, self.template_name, {
            'history':    history,
            'atlet_list': atlet_list,
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(get_atlet_taekwondo(request.user), pk=atlet_id) if atlet_id else None

            def to_float(key):
                val = request.POST.get(key)
                try:
                    return float(val) if val else None
                except (ValueError, TypeError):
                    return None

            kategori_usia = request.POST.get('kategori_usia', 'ELITE')

            # A. Ankle WBLT
            wblt_kanan = to_float('wblt_kanan_cm')
            wblt_kiri  = to_float('wblt_kiri_cm')

            # B. SLST balance mata tertutup
            slst_kanan = to_float('slst_kanan_detik')
            slst_kiri  = to_float('slst_kiri_detik')

            # C. YBT-LQ
            panjang_kanan = to_float('panjang_tungkai_kanan_cm')
            panjang_kiri  = to_float('panjang_tungkai_kiri_cm')
            ant_kanan = to_float('ybt_ant_kanan_cm')
            ant_kiri  = to_float('ybt_ant_kiri_cm')
            pm_kanan  = to_float('ybt_pm_kanan_cm')
            pm_kiri   = to_float('ybt_pm_kiri_cm')
            pl_kanan  = to_float('ybt_pl_kanan_cm')
            pl_kiri   = to_float('ybt_pl_kiri_cm')

            # D. Trunk rotation
            trunk_kanan = to_float('trunk_rotasi_kanan_derajat')
            trunk_kiri  = to_float('trunk_rotasi_kiri_derajat')

            # E/F. Hip IR & ER
            ir_kanan = to_float('hip_ir_kanan_derajat')
            ir_kiri  = to_float('hip_ir_kiri_derajat')
            er_kanan = to_float('hip_er_kanan_derajat')
            er_kiri  = to_float('hip_er_kiri_derajat')

            # G/H/I. Status observasional
            lumbar_status = request.POST.get('lumbar_status', 'MULUS')
            postur_status = request.POST.get('postur_status', 'TANPA_DEVIASI')
            napas_status  = request.POST.get('napas_status', 'ABDOMINAL_DOMINAN')

            # NOTE: skor_* SENGAJA dihitung ulang di sini dan TIDAK diambil
            # dari request.POST — sama seperti pola boxing/muaythai/karate.
            # Coach hanya input data mentah/observasi; nilai skor final yang
            # tersimpan selalu hasil kalkulasi RUBRIK_L1 server, bukan
            # input manual/JS.
            audit = CorrectionAuditL1TKD(
                atlet         = atlet,
                atlet_name    = atlet.nama_atlet if atlet else request.POST.get('atlet_name', ''),
                kategori_usia = kategori_usia,
                gender        = request.POST.get('gender', 'Putra'),
                kelas_berat   = to_float('kelas_berat'),

                wblt_kanan_cm = wblt_kanan,
                wblt_kiri_cm  = wblt_kiri,
                skor_ankle    = hitung_skor_l1_ankle(wblt_kanan, wblt_kiri, kategori_usia),

                slst_kanan_detik = slst_kanan,
                slst_kiri_detik  = slst_kiri,
                skor_balance     = hitung_skor_l1_balance(slst_kanan, slst_kiri, kategori_usia),

                panjang_tungkai_kanan_cm = panjang_kanan,
                panjang_tungkai_kiri_cm  = panjang_kiri,
                ybt_ant_kanan_cm = ant_kanan, ybt_ant_kiri_cm = ant_kiri,
                ybt_pm_kanan_cm  = pm_kanan,  ybt_pm_kiri_cm  = pm_kiri,
                ybt_pl_kanan_cm  = pl_kanan,  ybt_pl_kiri_cm  = pl_kiri,
                skor_ybalance    = hitung_skor_l1_ybalance(ant_kanan, ant_kiri, kategori_usia),

                trunk_rotasi_kanan_derajat = trunk_kanan,
                trunk_rotasi_kiri_derajat  = trunk_kiri,
                skor_trunk_rotation        = hitung_skor_l1_trunk_rotation(trunk_kanan, trunk_kiri),

                hip_ir_kanan_derajat = ir_kanan, hip_ir_kiri_derajat = ir_kiri,
                skor_hip_ir          = hitung_skor_l1_hip_ir(ir_kanan, ir_kiri),

                hip_er_kanan_derajat = er_kanan, hip_er_kiri_derajat = er_kiri,
                skor_hip_er          = hitung_skor_l1_hip_er(er_kanan, er_kiri),

                lumbar_status = lumbar_status,
                skor_lumbar   = hitung_skor_l1_lumbar(lumbar_status),

                postur_status = postur_status,
                skor_postur   = hitung_skor_l1_postur(postur_status),

                napas_status = napas_status,
                skor_napas   = hitung_skor_l1_napas(napas_status),

                ai_confidence_score = to_float('ai_confidence_score'),
                catatan = request.POST.get('catatan', ''),
            )
            audit.save()

            if audit.status_keputusan == 'MERAH':
                messages.error(request, f'🔴 {audit.atlet_name} — Lumbar Extension NYERI. WAJIB dirujuk, tes dihentikan.')
            elif audit.layak_naik:
                messages.success(request, f'✅ {audit.atlet_name} — Skor {audit.total_skor} ({audit.status_keputusan}). LAYAK naik ke L2!')
            else:
                messages.warning(request, f'⚠️ {audit.atlet_name} — Skor {audit.total_skor} ({audit.status_keputusan}). Belum layak ke L2.')

        except Exception as e:
            messages.error(request, f'Error menyimpan data: {e}')

        return redirect('taekwondo:l1_correction')


@login_required
def hapus_l1_tkd(request, pk):
    audit = get_object_or_404(CorrectionAuditL1TKD, pk=pk, atlet__in=get_atlet_taekwondo(request.user))
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L1 {nama} berhasil dihapus.')
    return redirect('taekwondo:l1_correction')


@login_required
def detail_l1_tkd(request, pk):
    audit = get_object_or_404(CorrectionAuditL1TKD, pk=pk, atlet__in=get_atlet_taekwondo(request.user))
    return JsonResponse({
        'atlet_name': audit.atlet_name, 'kategori_usia': audit.kategori_usia,
        'gender': audit.gender, 'kelas_berat': audit.kelas_berat,
        'skor_ankle': audit.skor_ankle,
        'skor_balance': audit.skor_balance,
        'skor_ybalance': audit.skor_ybalance,
        'skor_trunk_rotation': audit.skor_trunk_rotation,
        'skor_hip_ir': audit.skor_hip_ir,
        'skor_hip_er': audit.skor_hip_er,
        'skor_lumbar': audit.skor_lumbar,
        'skor_postur': audit.skor_postur,
        'skor_napas': audit.skor_napas,
        'total_skor': audit.total_skor, 'predikat': audit.predikat,
        'status_keputusan': audit.status_keputusan,
        'layak_naik': audit.layak_naik, 'item_terlemah': audit.item_terlemah,
        'rekomendasi': audit.rekomendasi_auto,
    })


# ══════════════════════════════════════════════════════════════════════
# L2 — STRENGTH (Taekwondo)
# ══════════════════════════════════════════════════════════════════════

class L2StrengthTKDView(LoginRequiredMixin, View):
    template_name = 'taekwondo/l2_strength.html'

    def get(self, request):
        atlet_qs       = get_atlet_taekwondo(request.user)
        atlet_id       = request.GET.get('atlet_id')
        selected_atlet = atlet_qs.filter(pk=atlet_id).first() if atlet_id else None
        history        = StrengthAuditL2.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history':        history,
            'selected_atlet': selected_atlet,
            'atlet_list':     atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(get_atlet_taekwondo(request.user), pk=atlet_id) if atlet_id else None

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

        return redirect('taekwondo:l2_strength')


@login_required
def hapus_l2_tkd(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk, atlet__in=get_atlet_taekwondo(request.user))
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L2 {nama} berhasil dihapus.')
    return redirect('taekwondo:l2_strength')


@login_required
def detail_l2_tkd(request, pk):
    audit = get_object_or_404(StrengthAuditL2, pk=pk, atlet__in=get_atlet_taekwondo(request.user))
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
# L3 — POWER (Taekwondo)
# ══════════════════════════════════════════════════════════════════════

class L3PowerTKDView(LoginRequiredMixin, View):
    template_name = 'taekwondo/l3_power.html'

    def get(self, request):
        atlet_qs       = get_atlet_taekwondo(request.user)
        atlet_id       = request.GET.get('atlet_id')
        selected_atlet = atlet_qs.filter(pk=atlet_id).first() if atlet_id else None
        history        = PowerAuditL3.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history':        history,
            'selected_atlet': selected_atlet,
            'atlet_list':     atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(get_atlet_taekwondo(request.user), pk=atlet_id) if atlet_id else None

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

        return redirect('taekwondo:l3_power')


@login_required
def hapus_l3_tkd(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk, atlet__in=get_atlet_taekwondo(request.user))
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L3 {nama} berhasil dihapus.')
    return redirect('taekwondo:l3_power')


@login_required
def detail_l3_tkd(request, pk):
    audit = get_object_or_404(PowerAuditL3, pk=pk, atlet__in=get_atlet_taekwondo(request.user))
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
# L4 — SPEED & AGILITY (Taekwondo)
# ══════════════════════════════════════════════════════════════════════

# Tabel konversi level-shuttle ke jarak (meter), protokol standar Yo-Yo IR1.
# HARUS identik dengan YOYO_JARAK di l4_speed_agility.html (JS) dan dengan
# YOYO_JARAK_TABLE di boxing/views.py & muaythai/views.py (norma sama untuk
# semua cabor combat).
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

# Rubrik kategori+gender L4 Taekwondo — HARUS identik dengan RUBRIK_L4 di
# l4_speed_agility.html (JS taekwondo). Pilar hex & yoyo dicopy apa adanya
# dari boxing/muaythai (norma umum combat sport). Pilar 'kick' untuk saat
# ini MASIH pakai angka yang sama dengan 'punch' boxing/muaythai — lihat
# catatan #4 di atas, sebaiknya dikalibrasi ulang.
RUBRIK_L4 = {
    'YOUTH': {
        'Putra': {'hex': [(12.00, 9.5), (14.00, 7.5), (16.00, 5.5), (18.00, 3.5)],
                   'kick': [(59, 9.5), (51, 7.5), (43, 5.5), (35, 3.5)],
                   'yoyo': [(920, 9.5), (680, 7.5), (440, 5.5), (240, 3.5)]},
        'Putri': {'hex': [(13.50, 9.5), (15.50, 7.5), (17.50, 5.5), (19.50, 3.5)],
                   'kick': [(53, 9.5), (46, 7.5), (38, 5.5), (30, 3.5)],
                   'yoyo': [(760, 9.5), (560, 7.5), (360, 5.5), (160, 3.5)]},
    },
    'JUNIOR': {
        'Putra': {'hex': [(10.50, 9.5), (12.00, 7.5), (13.50, 5.5), (15.00, 3.5)],
                   'kick': [(75, 9.5), (65, 7.5), (55, 5.5), (45, 3.5)],
                   'yoyo': [(1640, 9.5), (1240, 7.5), (880, 5.5), (560, 3.5)]},
        'Putri': {'hex': [(11.60, 9.5), (13.20, 7.5), (14.80, 5.5), (16.50, 3.5)],
                   'kick': [(66, 9.5), (58, 7.5), (49, 5.5), (40, 3.5)],
                   'yoyo': [(1320, 9.5), (1000, 7.5), (680, 5.5), (400, 3.5)]},
    },
    'SENIOR': {
        'Putra': {'hex': [(8.80, 9.5), (10.00, 7.5), (11.50, 5.5), (13.00, 3.5)],
                   'kick': [(90, 9.5), (79, 7.5), (67, 5.5), (55, 3.5)],
                   'yoyo': [(2080, 9.5), (1640, 7.5), (1200, 5.5), (800, 3.5)]},
        'Putri': {'hex': [(9.80, 9.5), (11.20, 7.5), (12.80, 5.5), (14.50, 3.5)],
                   'kick': [(79, 9.5), (69, 7.5), (59, 5.5), (48, 3.5)],
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


def hitung_skor_kick(kick_freq, postur_ok=True, kategori_usia='ELITE', gender='Putra'):
    """Jumlah tendangan/10 detik -> skor 0-10, dikurangi 1 jika postur tidak benar.
    Cermin dari autoScoreKick() di JS, kategori/gender-aware. Analog persis
    dengan hitung_skor_punch() di boxing/muaythai views.py."""
    if not kick_freq:
        return 0
    ambang = _tabel_l4(kategori_usia, gender)['kick']
    skor = 1.5  # Novice
    for batas, s in ambang:
        if kick_freq >= batas:
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


class L4SpeedAgilityTKDView(LoginRequiredMixin, View):
    template_name = 'taekwondo/l4_speed_agility.html'

    def get(self, request):
        atlet_qs        = get_atlet_taekwondo(request.user)
        atlet_id        = request.GET.get('atlet_id')
        selected_atlet  = atlet_qs.filter(pk=atlet_id).first() if atlet_id else None
        history         = SpeedAgilityAuditL4.objects.filter(atlet__in=atlet_qs).order_by('-timestamp')[:50]
        return render(request, self.template_name, {
            'history':        history,
            'selected_atlet': selected_atlet,
            'atlet_list':     atlet_qs.order_by('nama_atlet'),
        })

    def post(self, request):
        try:
            atlet_id = request.POST.get('atlet_id')
            atlet    = get_object_or_404(get_atlet_taekwondo(request.user), pk=atlet_id) if atlet_id else None

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

            kick_freq = to_int('kick_freq_10s')
            kick_postur_ok = request.POST.get('kick_postur_ok') == 'true'
            score_kick = hitung_skor_kick(kick_freq, kick_postur_ok, kategori_usia, gender)

            yoyo_level = to_int('yoyo_level_tercapai')
            yoyo_shuttle = to_int('yoyo_shuttle_tercapai')
            yoyo_jarak_input = to_float('yoyo_total_jarak_m')
            score_yoyo, jarak_final = hitung_skor_yoyo(
                yoyo_level, yoyo_shuttle, yoyo_jarak_input, kategori_usia, gender
            )

            # NOTE: score_hex, score_kick, score_yoyo SENGAJA dihitung ulang di
            # sini dan TIDAK diambil dari request.POST — sama seperti pola di
            # boxing/views.py & muaythai/views.py. Nilai final yang tersimpan
            # selalu hasil kalkulasi server, bukan input pelatih/JS, agar tidak
            # ada skor salah/kosong kalau JS di browser gagal jalan.
            #
            # Field kick_* (bukan punch_*) diisi di sini karena atlet cabang
            # 'tkd' — model SpeedAgilityAuditL4.kalkulasi_skor() otomatis
            # mendeteksi cabang atlet dan memakai score_kick untuk total_skor.
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
                kick_freq_10s=kick_freq,
                kick_postur_ok=kick_postur_ok,
                kick_reaction_time_ms=to_float('kick_reaction_time_ms'),
                score_kick=score_kick,
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

        return redirect('taekwondo:l4_speed_agility')


@login_required
def hapus_l4_tkd(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk, atlet__in=get_atlet_taekwondo(request.user))
    nama  = audit.atlet_name
    audit.delete()
    messages.success(request, f'Data L4 {nama} berhasil dihapus.')
    return redirect('taekwondo:l4_speed_agility')


@login_required
def detail_l4_tkd(request, pk):
    audit = get_object_or_404(SpeedAgilityAuditL4, pk=pk, atlet__in=get_atlet_taekwondo(request.user))
    return JsonResponse({
        'atlet_name': audit.atlet_name, 'kategori_usia': audit.kategori_usia,
        'gender': audit.gender, 'kelas_berat': audit.kelas_berat,
        'hex_waktu_rata': audit.hex_waktu_rata, 'score_hex': audit.score_hex,
        'kick_freq_10s': audit.kick_freq_10s, 'score_kick': audit.score_kick,
        'yoyo_total_jarak_m': audit.yoyo_total_jarak_m,
        'yoyo_vo2max': audit.yoyo_vo2max_estimasi,
        'score_yoyo': audit.score_yoyo, 'total_skor': audit.total_skor,
        'predikat': audit.predikat, 'rekomendasi': audit.rekomendasi_auto,
    })


# ══════════════════════════════════════════════════════════════════════
# REPORT CARD (Taekwondo)
# ══════════════════════════════════════════════════════════════════════

class ReportCardTKDView(LoginRequiredMixin, View):
    template_name = 'taekwondo/report_card.html'

    def get(self, request, atlet_id):
        from django.utils import timezone
        atlet_qs = get_atlet_taekwondo(request.user)
        atlet = get_object_or_404(atlet_qs, pk=atlet_id, cabang=CABANG_TKD)

        l1 = CorrectionAuditL1.objects.filter(atlet=atlet).order_by('-timestamp').first()
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