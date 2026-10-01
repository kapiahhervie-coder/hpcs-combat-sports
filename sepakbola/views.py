from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from combat.models import Atlet
from .models import (
    CorrectionAuditL1SB, StrengthAuditL2SB,
    PowerAuditL3SB, SpeedAgilityAuditL4SB,
)

# ============================================================
# RUBRIK L1 SEPAK BOLA — DRAFT, belum berdasarkan SOP resmi.
# Struktur & fungsi interpolasi mengikuti pola RUBRIK_L1 Boxing persis.
# Ganti angka norma ini begitu SOP sepak bola dari Coach Fanny siap.
# ============================================================
NORMA_ANKLE = {
    'YOUTH_PUTRA': (8, 10), 'YOUTH_PUTRI': (8, 10),
    'JUNIOR_PUTRA': (9, 11), 'JUNIOR_PUTRI': (9, 11),
    'SENIOR_PUTRA': (10, 13), 'SENIOR_PUTRI': (9, 12),
    'ELITE_PUTRA': (11, 14), 'ELITE_PUTRI': (10, 13),
}
NORMA_ASLR = {
    'YOUTH_PUTRA': (55, 70), 'YOUTH_PUTRI': (55, 70),
    'JUNIOR_PUTRA': (60, 75), 'JUNIOR_PUTRI': (60, 75),
    'SENIOR_PUTRA': (65, 80), 'SENIOR_PUTRI': (65, 80),
    'ELITE_PUTRA': (70, 85), 'ELITE_PUTRI': (70, 85),
}
NORMA_HIP = {
    'YOUTH': (25, 35), 'JUNIOR': (30, 40),
    'SENIOR': (35, 45), 'ELITE': (35, 45),
}
BATAS_ASIMETRI_HIP = 10
PENALTI_ASIMETRI_HIP = 2


def interpolasi_skor(nilai, batas_bawah, batas_atas):
    """Persis meniru interpolasiSkor() JS di Boxing: <10 non-linear, 10 = skala penuh."""
    if nilai is None:
        return None
    if nilai < batas_bawah:
        return min(1 + 3 * (nilai / batas_bawah), 4.0) if batas_bawah > 0 else 1.0
    if nilai <= batas_atas:
        p = (nilai - batas_bawah) / (batas_atas - batas_bawah) if batas_atas > batas_bawah else 1
        return 5 + 2 * p
    rentang_atas = batas_atas * 0.5 if batas_atas > 0 else 1
    p2 = min((nilai - batas_atas) / rentang_atas, 1.0)
    return min(8 + 2 * p2, 10.0)


def hitung_predikat(total):
    if total >= 9.0:
        return 'ELITE'
    if total >= 7.0:
        return 'READY'
    if total >= 5.0:
        return 'DEVELOPING'
    return 'NOVICE'


def hitung_skor_l1_sb(data, kategori_usia, gender):
    def f(key):
        val = data.get(key)
        try:
            return float(val) if val not in (None, '') else None
        except ValueError:
            return None

    key_ag = f"{kategori_usia}_{gender}"

    # Pilar 1: Ankle (bilateral, ambil yang terlemah seperti Boxing)
    ankle_kiri, ankle_kanan = f('ankle_kiri'), f('ankle_kanan')
    nilai_ankle = [v for v in [ankle_kiri, ankle_kanan] if v is not None]
    score_ankle = None
    if nilai_ankle:
        bawah, atas = NORMA_ANKLE.get(key_ag, (10, 13))
        score_ankle = interpolasi_skor(min(nilai_ankle), bawah, atas)

    # Pilar 2: ASLR (bilateral, rata-rata seperti Stability Boxing)
    aslr_kiri, aslr_kanan = f('aslr_kiri'), f('aslr_kanan')
    bawah_a, atas_a = NORMA_ASLR.get(key_ag, (65, 80))
    s_kiri_a = interpolasi_skor(aslr_kiri, bawah_a, atas_a)
    s_kanan_a = interpolasi_skor(aslr_kanan, bawah_a, atas_a)
    nilai_aslr = [v for v in [s_kiri_a, s_kanan_a] if v is not None]
    score_aslr = sum(nilai_aslr) / len(nilai_aslr) if nilai_aslr else None

    # Pilar 3: Hip Rotation (bilateral, rata-rata + penalti asimetri)
    hip_kiri, hip_kanan = f('hip_kiri'), f('hip_kanan')
    bawah_h, atas_h = NORMA_HIP.get(kategori_usia, (35, 45))
    s_kiri_h = interpolasi_skor(hip_kiri, bawah_h, atas_h)
    s_kanan_h = interpolasi_skor(hip_kanan, bawah_h, atas_h)
    nilai_hip = [v for v in [s_kiri_h, s_kanan_h] if v is not None]
    score_hip = None
    kena_penalti = False
    if nilai_hip:
        score_hip = sum(nilai_hip) / len(nilai_hip)
        if hip_kiri is not None and hip_kanan is not None:
            kena_penalti = abs(hip_kiri - hip_kanan) > BATAS_ASIMETRI_HIP
        if kena_penalti:
            score_hip = max(1.0, score_hip - PENALTI_ASIMETRI_HIP)

    # Pilar 4-6: kualitatif, langsung dari dropdown (1/2/3 -> 3/6/9 mirip Boxing)
    skor_trunk = f('skor_trunk')
    skor_postur = f('skor_postur')
    skor_napas = f('skor_napas')

    semua = {
        'Ankle Mobility': score_ankle, 'ASLR': score_aslr, 'Hip Rotation': score_hip,
        'Trunk Rotation': skor_trunk, 'Postur': skor_postur, 'Napas': skor_napas,
    }
    terisi = {k: v for k, v in semua.items() if v is not None and v > 0}
    total = round(sum(terisi.values()) / len(terisi), 1) if terisi else 0
    pilar_terendah = min(terisi, key=terisi.get) if terisi else ''

    return {
        'score_ankle': score_ankle, 'score_aslr': score_aslr, 'score_hip': score_hip,
        'skor_trunk': skor_trunk, 'skor_postur': skor_postur, 'skor_napas': skor_napas,
        'kena_penalti': kena_penalti, 'total': total,
        'predikat': hitung_predikat(total), 'pilar_terendah': pilar_terendah,
    }


class DashboardSepakbolaView(LoginRequiredMixin, TemplateView):
    template_name = 'sepakbola/dashboard_sepakbola.html'

    def get_context_data(self, **kwargs):
        import json
        ctx = super().get_context_data(**kwargs)
        daftar_atlet = Atlet.objects.filter(cabang='sepakbola')
        ctx['atlet_list'] = daftar_atlet
        ctx['daftar_atlet'] = daftar_atlet

        atlet_id = self.request.GET.get('atlet_id')
        atlet = None
        if atlet_id:
            atlet = daftar_atlet.filter(pk=atlet_id).first()
        elif daftar_atlet.exists():
            atlet = daftar_atlet.first()
        ctx['atlet'] = atlet

        score_data, score_labels = [], []
        if atlet:
            riwayat = CorrectionAuditL1SB.objects.filter(atlet=atlet).order_by('timestamp')[:10]
            score_data = [r.total_skor for r in riwayat]
            score_labels = [r.timestamp.strftime('%d/%m') for r in riwayat]
        ctx['score_data'] = json.dumps(score_data)
        ctx['score_labels'] = json.dumps(score_labels)
        ctx['training_load'] = 0
        return ctx


class L1CorrectionSBView(LoginRequiredMixin, View):
    template_name = 'sepakbola/l1_correction.html'

    def get(self, request):
        selected_category = request.GET.get('category', '')
        atlet_qs = Atlet.objects.filter(cabang='sepakbola')
        if selected_category:
            atlet_qs = atlet_qs.filter(kategori_usia__iexact=selected_category)
        history = CorrectionAuditL1SB.objects.select_related('atlet').all()[:50]
        return render(request, self.template_name, {
            'atlet_list': atlet_qs,
            'history': history,
            'selected_category': selected_category,
            'atlet_id_terpilih': request.GET.get('atlet_id'),
        })

    def post(self, request):
        from django.contrib import messages
        atlet_id = request.POST.get('atlet_id')
        kategori_usia = request.POST.get('kategori_usia', 'SENIOR')
        gender = request.POST.get('gender', 'PUTRA')

        if not atlet_id:
            messages.error(request, 'Pilih atlet terlebih dahulu sebelum menyimpan audit.')
            return redirect('sepakbola:l1_correction')

        hasil = hitung_skor_l1_sb(request.POST, kategori_usia, gender)

        def f(key):
            val = request.POST.get(key)
            try:
                return float(val) if val not in (None, '') else None
            except ValueError:
                return None

        CorrectionAuditL1SB.objects.create(
            atlet_id=atlet_id,
            kategori_usia=kategori_usia,
            gender=gender,
            ankle_kiri_cm=f('ankle_kiri'), ankle_kanan_cm=f('ankle_kanan'),
            score_ankle=hasil['score_ankle'],
            aslr_kiri_derajat=f('aslr_kiri'), aslr_kanan_derajat=f('aslr_kanan'),
            score_aslr=hasil['score_aslr'],
            hip_kiri_derajat=f('hip_kiri'), hip_kanan_derajat=f('hip_kanan'),
            score_hip=hasil['score_hip'], kena_penalti_asimetri=hasil['kena_penalti'],
            skor_trunk=hasil['skor_trunk'],
            skor_postur=hasil['skor_postur'],
            skor_napas=hasil['skor_napas'],
            total_skor=hasil['total'],
            predikat=hasil['predikat'],
            pilar_terendah=hasil['pilar_terendah'],
            catatan_pelatih=request.POST.get('catatan', ''),
        )
        return redirect('sepakbola:l1_correction')


class DaftarAtletSBView(LoginRequiredMixin, TemplateView):
    template_name = 'sepakbola/daftar_atlet.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        daftar_atlet = Atlet.objects.filter(cabang='sepakbola', pelatih=self.request.user)
        ctx['daftar_atlet'] = daftar_atlet
        ctx['total_atlet'] = daftar_atlet.count()
        return ctx


class L1DeleteSBView(LoginRequiredMixin, View):
    def post(self, request, audit_id):
        from django.http import JsonResponse
        audit = get_object_or_404(CorrectionAuditL1SB, id=audit_id)
        audit.delete()
        return JsonResponse({'status': 'success'})


NORMA_LOWER_BW = {
    'YOUTH': (0.7, 1.0), 'JUNIOR': (0.9, 1.3), 'SENIOR': (1.2, 1.6), 'ELITE': (1.2, 1.6),
}
NORMA_POSTERIOR_BW = {
    'YOUTH': (0.8, 1.1), 'JUNIOR': (1.0, 1.4), 'SENIOR': (1.3, 1.8), 'ELITE': (1.3, 1.8),
}
NORMA_SINGLELEG_BW = {
    'YOUTH': (0.25, 0.4), 'JUNIOR': (0.35, 0.55), 'SENIOR': (0.45, 0.7), 'ELITE': (0.45, 0.7),
}
NORMA_CORE_DETIK = {
    'YOUTH': (40, 60), 'JUNIOR': (60, 90), 'SENIOR': (90, 120), 'ELITE': (90, 120),
}
NORMA_ISO_DETIK = {
    'YOUTH': (40, 60), 'JUNIOR': (60, 90), 'SENIOR': (90, 120), 'ELITE': (90, 120),
}
BATAS_ASIMETRI_SINGLELEG_PCT = 0.15
PENALTI_ASIMETRI_SINGLELEG = 2


def hitung_skor_l2_sb(data, kategori_usia):
    def f(key):
        val = data.get(key)
        try:
            return float(val) if val not in (None, '') else None
        except ValueError:
            return None

    berat = f('berat_badan_kg') or 0

    def skor_bw_ratio(beban, berat, norma_tuple):
        if beban is None or not berat:
            return None
        rasio = beban / berat
        bawah, atas = norma_tuple
        return interpolasi_skor(rasio, bawah, atas)

    def skor_durasi(detik, norma_tuple):
        if detik is None:
            return None
        bawah, atas = norma_tuple
        return interpolasi_skor(detik, bawah, atas)

    lower_kg = f('lower_5rm_kg')
    score_lower = skor_bw_ratio(lower_kg, berat, NORMA_LOWER_BW.get(kategori_usia, (1.2, 1.6)))

    posterior_kg = f('posterior_5rm_kg')
    score_posterior = skor_bw_ratio(posterior_kg, berat, NORMA_POSTERIOR_BW.get(kategori_usia, (1.3, 1.8)))

    sl_kiri, sl_kanan = f('singleleg_kiri_kg'), f('singleleg_kanan_kg')
    norma_sl = NORMA_SINGLELEG_BW.get(kategori_usia, (0.45, 0.7))
    s_kiri = skor_bw_ratio(sl_kiri, berat, norma_sl)
    s_kanan = skor_bw_ratio(sl_kanan, berat, norma_sl)
    nilai_sl = [v for v in [s_kiri, s_kanan] if v is not None]
    score_singleleg = None
    kena_penalti = False
    if nilai_sl:
        score_singleleg = sum(nilai_sl) / len(nilai_sl)
        if sl_kiri is not None and sl_kanan is not None and max(sl_kiri, sl_kanan) > 0:
            selisih_pct = abs(sl_kiri - sl_kanan) / max(sl_kiri, sl_kanan)
            kena_penalti = selisih_pct > BATAS_ASIMETRI_SINGLELEG_PCT
        if kena_penalti:
            score_singleleg = max(1.0, score_singleleg - PENALTI_ASIMETRI_SINGLELEG)

    score_core = skor_durasi(f('core_durasi_detik'), NORMA_CORE_DETIK.get(kategori_usia, (90, 120)))
    score_isometric = skor_durasi(f('iso_durasi_detik'), NORMA_ISO_DETIK.get(kategori_usia, (90, 120)))

    semua = {
        'Lower Body': score_lower, 'Posterior Chain': score_posterior,
        'Single-Leg': score_singleleg, 'Core': score_core, 'Isometric': score_isometric,
    }
    terisi = {k: v for k, v in semua.items() if v is not None and v > 0}
    total = round(sum(terisi.values()) / len(terisi), 1) if terisi else 0
    pilar_terendah = min(terisi, key=terisi.get) if terisi else ''

    return {
        'score_lower': score_lower, 'score_posterior': score_posterior,
        'score_singleleg': score_singleleg, 'score_core': score_core,
        'score_isometric': score_isometric, 'kena_penalti': kena_penalti,
        'total': total, 'predikat': hitung_predikat(total), 'pilar_terendah': pilar_terendah,
    }


class L2StrengthSBView(LoginRequiredMixin, View):
    template_name = 'sepakbola/l2_strength.html'

    def get(self, request):
        atlet_list = Atlet.objects.filter(cabang='sepakbola')
        history = StrengthAuditL2SB.objects.select_related('atlet').all()[:50]
        return render(request, self.template_name, {'atlet_list': atlet_list, 'history': history})

    def post(self, request):
        from django.contrib import messages
        atlet_id = request.POST.get('atlet_id')
        kategori_usia = request.POST.get('kategori_usia', 'SENIOR')
        gender = request.POST.get('gender', 'PUTRA')

        if not atlet_id:
            messages.error(request, 'Pilih atlet terlebih dahulu sebelum menyimpan audit.')
            return redirect('sepakbola:l2_strength')

        hasil = hitung_skor_l2_sb(request.POST, kategori_usia)

        def f(key):
            val = request.POST.get(key)
            try:
                return float(val) if val not in (None, '') else None
            except ValueError:
                return None

        StrengthAuditL2SB.objects.create(
            atlet_id=atlet_id, kategori_usia=kategori_usia, gender=gender,
            berat_badan_kg=f('berat_badan_kg'),
            lower_5rm_kg=f('lower_5rm_kg'), score_lower=hasil['score_lower'],
            posterior_5rm_kg=f('posterior_5rm_kg'), score_posterior=hasil['score_posterior'],
            singleleg_kiri_kg=f('singleleg_kiri_kg'), singleleg_kanan_kg=f('singleleg_kanan_kg'),
            score_singleleg=hasil['score_singleleg'], kena_penalti_asimetri=hasil['kena_penalti'],
            core_durasi_detik=f('core_durasi_detik'), score_core=hasil['score_core'],
            iso_durasi_detik=f('iso_durasi_detik'), iso_tremor_onset_detik=f('iso_tremor_onset_detik'),
            score_isometric=hasil['score_isometric'],
            total_skor=hasil['total'], predikat=hasil['predikat'], pilar_terendah=hasil['pilar_terendah'],
            catatan_pelatih=request.POST.get('catatan', ''),
        )
        return redirect('sepakbola:l2_strength')


class L2DeleteSBView(LoginRequiredMixin, View):
    def post(self, request, audit_id):
        from django.http import JsonResponse
        audit = get_object_or_404(StrengthAuditL2SB, id=audit_id)
        audit.delete()
        return JsonResponse({'status': 'success'})


RUBRIK_L3 = {
    'YOUTH': {
        'PUTRA': {'jump': [(38, 9.5), (31, 7.5), (24, 5.5), (17, 3.5)], 'sprint': [(4.70, 9.5), (5.10, 7.5), (5.50, 5.5), (5.90, 3.5)],
                  'broad': [(1.60, 9.5), (1.35, 7.5), (1.10, 5.5), (0.85, 3.5)], 'rsi': [(1.40, 9.5), (1.10, 7.5), (0.85, 5.5), (0.55, 3.5)],
                  'agility': [(10.80, 9.5), (11.80, 7.5), (12.80, 5.5), (13.80, 3.5)]},
        'PUTRI': {'jump': [(33, 9.5), (27, 7.5), (21, 5.5), (15, 3.5)], 'sprint': [(5.10, 9.5), (5.50, 7.5), (5.90, 5.5), (6.30, 3.5)],
                  'broad': [(1.40, 9.5), (1.15, 7.5), (0.95, 5.5), (0.70, 3.5)], 'rsi': [(1.15, 9.5), (0.90, 7.5), (0.70, 5.5), (0.45, 3.5)],
                  'agility': [(11.80, 9.5), (12.80, 7.5), (13.80, 5.5), (14.80, 3.5)]},
    },
    'JUNIOR': {
        'PUTRA': {'jump': [(56, 9.5), (47, 7.5), (38, 5.5), (29, 3.5)], 'sprint': [(4.00, 9.5), (4.30, 7.5), (4.60, 5.5), (4.90, 3.5)],
                  'broad': [(2.20, 9.5), (1.95, 7.5), (1.70, 5.5), (1.45, 3.5)], 'rsi': [(2.00, 9.5), (1.65, 7.5), (1.30, 5.5), (0.95, 3.5)],
                  'agility': [(9.70, 9.5), (10.30, 7.5), (11.00, 5.5), (11.70, 3.5)]},
        'PUTRI': {'jump': [(42, 9.5), (35, 7.5), (28, 5.5), (21, 3.5)], 'sprint': [(4.40, 9.5), (4.70, 7.5), (5.00, 5.5), (5.30, 3.5)],
                  'broad': [(1.90, 9.5), (1.65, 7.5), (1.40, 5.5), (1.15, 3.5)], 'rsi': [(1.65, 9.5), (1.35, 7.5), (1.05, 5.5), (0.75, 3.5)],
                  'agility': [(10.50, 9.5), (11.20, 7.5), (12.00, 5.5), (12.70, 3.5)]},
    },
    'SENIOR': {
        'PUTRA': {'jump': [(65, 9.5), (56, 7.5), (47, 5.5), (38, 3.5)], 'sprint': [(3.80, 9.5), (4.00, 7.5), (4.30, 5.5), (4.60, 3.5)],
                  'broad': [(2.60, 9.5), (2.35, 7.5), (2.10, 5.5), (1.85, 3.5)], 'rsi': [(2.30, 9.5), (1.90, 7.5), (1.50, 5.5), (1.10, 3.5)],
                  'agility': [(8.80, 9.5), (9.40, 7.5), (10.00, 5.5), (10.70, 3.5)]},
        'PUTRI': {'jump': [(47, 9.5), (40, 7.5), (33, 5.5), (26, 3.5)], 'sprint': [(4.10, 9.5), (4.40, 7.5), (4.70, 5.5), (5.00, 3.5)],
                  'broad': [(2.15, 9.5), (1.90, 7.5), (1.65, 5.5), (1.40, 3.5)], 'rsi': [(1.90, 9.5), (1.60, 7.5), (1.30, 5.5), (1.00, 3.5)],
                  'agility': [(9.60, 9.5), (10.30, 7.5), (11.00, 5.5), (11.70, 3.5)]},
    },
}
RUBRIK_L3['ELITE'] = RUBRIK_L3['SENIOR']
ARAH_L3 = {'jump': 'tinggi', 'sprint': 'rendah', 'broad': 'tinggi', 'rsi': 'tinggi', 'agility': 'rendah'}


def skor_l3(pilar, nilai, kategori_usia, gender):
    if not nilai or nilai <= 0:
        return None
    tabel_kat = RUBRIK_L3.get(kategori_usia, RUBRIK_L3['SENIOR'])
    ambang = tabel_kat.get(gender, tabel_kat['PUTRA'])[pilar]
    if ARAH_L3[pilar] == 'rendah':
        for batas, skor in ambang:
            if nilai <= batas:
                return skor
    else:
        for batas, skor in ambang:
            if nilai >= batas:
                return skor
    return 1.5


def hitung_skor_l3_sb(data, kategori_usia, gender):
    def f(key):
        val = data.get(key)
        try:
            return float(val) if val not in (None, '') else None
        except ValueError:
            return None

    jump = f('jump_height_cm')
    sprint = f('sprint_30m_detik')
    broad = f('broad_jump_m')
    agility = f('agility_ttest_detik')
    rsi_jh, rsi_ct = f('rsi_jump_height_cm'), f('rsi_contact_time_ms')
    rsi_val = (rsi_jh / rsi_ct * 1000) if (rsi_jh and rsi_ct) else None

    score_jump = skor_l3('jump', jump, kategori_usia, gender)
    score_sprint = skor_l3('sprint', sprint, kategori_usia, gender)
    score_broad = skor_l3('broad', broad, kategori_usia, gender)
    score_rsi = skor_l3('rsi', rsi_val, kategori_usia, gender)
    score_agility = skor_l3('agility', agility, kategori_usia, gender)

    semua = {'Jump': score_jump, 'Sprint': score_sprint, 'Broad Jump': score_broad, 'RSI': score_rsi, 'Agility': score_agility}
    terisi = {k: v for k, v in semua.items() if v is not None and v > 0}
    total = round(sum(terisi.values()) / len(terisi), 1) if terisi else 0
    pilar_terendah = min(terisi, key=terisi.get) if terisi else ''

    return {
        'score_jump': score_jump, 'score_sprint': score_sprint, 'score_broad': score_broad,
        'score_rsi': score_rsi, 'score_agility': score_agility, 'rsi_val': rsi_val,
        'total': total, 'predikat': hitung_predikat(total), 'pilar_terendah': pilar_terendah,
    }


class L3PowerSBView(LoginRequiredMixin, View):
    template_name = 'sepakbola/l3_power.html'

    def get(self, request):
        atlet_list = Atlet.objects.filter(cabang='sepakbola')
        history = PowerAuditL3SB.objects.select_related('atlet').all()[:50]
        return render(request, self.template_name, {'atlet_list': atlet_list, 'history': history})

    def post(self, request):
        from django.contrib import messages
        atlet_id = request.POST.get('atlet_id')
        kategori_usia = request.POST.get('kategori_usia', 'SENIOR')
        gender = request.POST.get('gender', 'PUTRA')

        if not atlet_id:
            messages.error(request, 'Pilih atlet terlebih dahulu sebelum menyimpan audit.')
            return redirect('sepakbola:l3_power')

        hasil = hitung_skor_l3_sb(request.POST, kategori_usia, gender)

        def f(key):
            val = request.POST.get(key)
            try:
                return float(val) if val not in (None, '') else None
            except ValueError:
                return None

        PowerAuditL3SB.objects.create(
            atlet_id=atlet_id, kategori_usia=kategori_usia, gender=gender,
            jump_height_cm=f('jump_height_cm'), score_jump=hasil['score_jump'],
            sprint_30m_detik=f('sprint_30m_detik'), score_sprint=hasil['score_sprint'],
            broad_jump_m=f('broad_jump_m'), score_broad=hasil['score_broad'],
            rsi_jump_height_cm=f('rsi_jump_height_cm'), rsi_contact_time_ms=f('rsi_contact_time_ms'),
            rsi_value=hasil['rsi_val'], score_rsi=hasil['score_rsi'],
            agility_ttest_detik=f('agility_ttest_detik'), score_agility=hasil['score_agility'],
            total_skor=hasil['total'], predikat=hasil['predikat'], pilar_terendah=hasil['pilar_terendah'],
            catatan_pelatih=request.POST.get('catatan', ''),
        )
        return redirect('sepakbola:l3_power')


class L3DeleteSBView(LoginRequiredMixin, View):
    def post(self, request, audit_id):
        from django.http import JsonResponse
        audit = get_object_or_404(PowerAuditL3SB, id=audit_id)
        audit.delete()
        return JsonResponse({'status': 'success'})


RUBRIK_L4 = {
    'YOUTH': {
        'PUTRA': {'hex': [(12.00, 9.5), (14.00, 7.5), (16.00, 5.5), (18.00, 3.5)], 'ladder': [(62, 9.5), (54, 7.5), (46, 5.5), (38, 3.5)], 'yoyo': [(960, 9.5), (720, 7.5), (480, 5.5), (280, 3.5)]},
        'PUTRI': {'hex': [(13.50, 9.5), (15.50, 7.5), (17.50, 5.5), (19.50, 3.5)], 'ladder': [(56, 9.5), (48, 7.5), (40, 5.5), (32, 3.5)], 'yoyo': [(800, 9.5), (600, 7.5), (400, 5.5), (200, 3.5)]},
    },
    'JUNIOR': {
        'PUTRA': {'hex': [(10.50, 9.5), (12.00, 7.5), (13.50, 5.5), (15.00, 3.5)], 'ladder': [(78, 9.5), (68, 7.5), (58, 5.5), (48, 3.5)], 'yoyo': [(1720, 9.5), (1320, 7.5), (960, 5.5), (640, 3.5)]},
        'PUTRI': {'hex': [(11.60, 9.5), (13.20, 7.5), (14.80, 5.5), (16.50, 3.5)], 'ladder': [(69, 9.5), (61, 7.5), (52, 5.5), (43, 3.5)], 'yoyo': [(1400, 9.5), (1080, 7.5), (760, 5.5), (480, 3.5)]},
    },
    'SENIOR': {
        'PUTRA': {'hex': [(8.80, 9.5), (10.00, 7.5), (11.50, 5.5), (13.00, 3.5)], 'ladder': [(94, 9.5), (82, 7.5), (70, 5.5), (58, 3.5)], 'yoyo': [(2320, 9.5), (1880, 7.5), (1400, 5.5), (960, 3.5)]},
        'PUTRI': {'hex': [(9.80, 9.5), (11.20, 7.5), (12.80, 5.5), (14.50, 3.5)], 'ladder': [(83, 9.5), (73, 7.5), (63, 5.5), (52, 3.5)], 'yoyo': [(1880, 9.5), (1480, 7.5), (1080, 5.5), (720, 3.5)]},
    },
}
RUBRIK_L4['ELITE'] = RUBRIK_L4['SENIOR']

YOYO_JARAK = {
    5: {1: 40, 2: 80, 3: 120, 4: 160},
    7: {1: 200, 2: 240, 3: 280, 4: 320, 5: 360, 6: 400, 7: 440, 8: 480},
    9: {1: 520, 2: 560, 3: 600, 4: 640, 5: 680, 6: 720, 7: 760, 8: 800},
    11: {1: 840, 2: 880, 3: 920, 4: 960, 5: 1000, 6: 1040, 7: 1080, 8: 1120},
    13: {1: 1160, 2: 1200, 3: 1240, 4: 1280, 5: 1320, 6: 1360, 7: 1400, 8: 1440},
    15: {1: 1480, 2: 1520, 3: 1560, 4: 1600, 5: 1640, 6: 1680, 7: 1720, 8: 1760},
    17: {1: 1800, 2: 1840, 3: 1880, 4: 1920, 5: 1960, 6: 2000, 7: 2040, 8: 2080},
    19: {1: 2120, 2: 2160, 3: 2200, 4: 2240, 5: 2280, 6: 2320, 7: 2360, 8: 2400},
    21: {1: 2440, 2: 2480, 3: 2520},
}


def kategori_gender_l4(kategori_usia, gender):
    tabel_kat = RUBRIK_L4.get(kategori_usia, RUBRIK_L4['SENIOR'])
    return tabel_kat.get(gender, tabel_kat['PUTRA'])


def hitung_skor_l4_sb(data, kategori_usia, gender):
    def f(key):
        val = data.get(key)
        try:
            return float(val) if val not in (None, '') else None
        except ValueError:
            return None

    def fi(key):
        val = data.get(key)
        try:
            return int(val) if val not in (None, '') else None
        except ValueError:
            return None

    ambang = kategori_gender_l4(kategori_usia, gender)

    hex_vals = [v for v in [f('hex_waktu_putaran1'), f('hex_waktu_putaran2'), f('hex_waktu_putaran3')] if v is not None and v > 0]
    hex_avg = round(sum(hex_vals) / len(hex_vals), 2) if hex_vals else None
    score_hex = None
    if hex_avg is not None:
        score_hex = 1.5
        for batas, skor in ambang['hex']:
            if hex_avg <= batas:
                score_hex = skor
                break

    ladder = fi('ladder_touch_10s')
    postur_ok = data.get('ladder_postur_ok') == 'true'
    score_ladder = None
    if ladder:
        score_ladder = 1.5
        for batas, skor in ambang['ladder']:
            if ladder >= batas:
                score_ladder = skor
                break
        if not postur_ok:
            score_ladder = max(1.5, round((score_ladder - 1) * 10) / 10)

    yoyo_level, yoyo_shuttle = fi('yoyo_level_tercapai'), fi('yoyo_shuttle_tercapai')
    jarak = f('yoyo_total_jarak_m')
    if yoyo_level and yoyo_shuttle:
        jarak = YOYO_JARAK.get(yoyo_level, {}).get(yoyo_shuttle, yoyo_level * yoyo_shuttle * 20)
    vo2max = None
    score_yoyo = None
    if jarak and jarak > 0:
        vo2max = round((jarak * 0.0084) + 36.4, 1)
        score_yoyo = 1.5
        for batas, skor in ambang['yoyo']:
            if jarak >= batas:
                score_yoyo = skor
                break

    semua = {'Hex': score_hex, 'Ladder': score_ladder, 'YoYo': score_yoyo}
    terisi = {k: v for k, v in semua.items() if v is not None and v > 0}
    total = round(sum(terisi.values()) / len(terisi), 1) if terisi else 0
    pilar_terendah = min(terisi, key=terisi.get) if terisi else ''

    return {
        'hex_avg': hex_avg, 'score_hex': score_hex, 'score_ladder': score_ladder,
        'jarak': jarak, 'vo2max': vo2max, 'score_yoyo': score_yoyo,
        'total': total, 'predikat': hitung_predikat(total), 'pilar_terendah': pilar_terendah,
    }


class L4SpeedAgilitySBView(LoginRequiredMixin, View):
    template_name = 'sepakbola/l4_speed_agility.html'

    def get(self, request):
        atlet_list = Atlet.objects.filter(cabang='sepakbola')
        history = SpeedAgilityAuditL4SB.objects.select_related('atlet').all()[:50]
        return render(request, self.template_name, {'atlet_list': atlet_list, 'history': history})

    def post(self, request):
        from django.contrib import messages
        atlet_id = request.POST.get('atlet_id')
        kategori_usia = request.POST.get('kategori_usia', 'SENIOR')
        gender = request.POST.get('gender', 'PUTRA')

        if not atlet_id:
            messages.error(request, 'Pilih atlet terlebih dahulu sebelum menyimpan audit.')
            return redirect('sepakbola:l4_speed_agility')

        hasil = hitung_skor_l4_sb(request.POST, kategori_usia, gender)

        def f(key):
            val = request.POST.get(key)
            try:
                return float(val) if val not in (None, '') else None
            except ValueError:
                return None

        def fi(key):
            val = request.POST.get(key)
            try:
                return int(val) if val not in (None, '') else None
            except ValueError:
                return None

        SpeedAgilityAuditL4SB.objects.create(
            atlet_id=atlet_id, kategori_usia=kategori_usia, gender=gender,
            kondisi_uji=request.POST.get('kondisi_uji', 'FRESH'),
            hex_waktu_putaran1=f('hex_waktu_putaran1'), hex_waktu_putaran2=f('hex_waktu_putaran2'),
            hex_waktu_putaran3=f('hex_waktu_putaran3'), hex_avg=hasil['hex_avg'], score_hex=hasil['score_hex'],
            ladder_touch_10s=fi('ladder_touch_10s'),
            ladder_postur_ok=(request.POST.get('ladder_postur_ok') == 'true'), score_ladder=hasil['score_ladder'],
            yoyo_level_tercapai=fi('yoyo_level_tercapai'), yoyo_shuttle_tercapai=fi('yoyo_shuttle_tercapai'),
            yoyo_total_jarak_m=hasil['jarak'], vo2max_estimasi=hasil['vo2max'], score_yoyo=hasil['score_yoyo'],
            total_skor=hasil['total'], predikat=hasil['predikat'], pilar_terendah=hasil['pilar_terendah'],
            catatan_pelatih=request.POST.get('catatan', ''),
        )
        return redirect('sepakbola:l4_speed_agility')


class L4DeleteSBView(LoginRequiredMixin, View):
    def post(self, request, audit_id):
        from django.http import JsonResponse
        audit = get_object_or_404(SpeedAgilityAuditL4SB, id=audit_id)
        audit.delete()
        return JsonResponse({'status': 'success'})











