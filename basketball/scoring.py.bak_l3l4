"""
HPCS Basketball — Scoring L1 & L2 (server = sumber kebenaran)

Pola sama dengan Boxing (RUBRIK_L1 di views + scoring_l1.py): skor yang
tampil di preview JS HARUS sama dengan yang disimpan server. Bedanya, di sini
ambang batas hanya ditulis SEKALI (RUBRIK_L1 / RUBRIK_L2) lalu dikirim ke
template lewat `json_script`, jadi JS dan server tidak bisa berbeda.

Ambang ANKLE dan STABILITY identik dengan SOP Level 1 Boxing (Revisi 1).
Ambang HIP, SHOULDER, dan seluruh norma L2 adalah NORMA KERJA HPCS Basketball
— validasi dengan data klub/federasi sebelum dipakai untuk keputusan seleksi.
"""

# ══════════════════════════════════════════════════════════════════════
# KATEGORI USIA SOP (bucket) — sama dengan Boxing: 7 / 10 / 15 / 25
# ══════════════════════════════════════════════════════════════════════
KATEGORI_TO_BUCKET = {'YOUTH': '10', 'JUNIOR': '15', 'SENIOR': '25', 'ELITE': '25'}


def bucket_dari_umur(umur):
    try:
        u = int(umur)
    except (TypeError, ValueError):
        return None
    if u <= 8:
        return '7'
    if u <= 11:
        return '10'
    if u <= 17:
        return '15'
    return '25'


def tentukan_bucket(posted, atlet=None, kategori_usia='ELITE'):
    """Prioritas: pilihan pelatih di form -> umur atlet -> kategori_usia."""
    if posted in ('7', '10', '15', '25'):
        return posted
    umur = getattr(atlet, 'umur', None) if atlet else None
    return bucket_dari_umur(umur) or KATEGORI_TO_BUCKET.get(kategori_usia, '25')


# ══════════════════════════════════════════════════════════════════════
# RUBRIK L1 — pasangan [batas_bawah_Cukup, batas_atas_Baik]
# ══════════════════════════════════════════════════════════════════════
RUBRIK_L1 = {
    'ankle': {   # Weight-Bearing Lunge Test (cm)  — SOP Boxing Tabel A
        '7_Putra': [7, 9],   '7_Putri': [7, 9],
        '10_Putra': [8, 10], '10_Putri': [8, 10],
        '15_Putra': [8, 11], '15_Putri': [8, 11],
        '25_Putra': [9, 12], '25_Putri': [8, 11],
    },
    'stability': {  # Single Leg Stance mata tertutup (detik) — SOP Boxing Tabel B
        '7_Putra': [3, 6],   '7_Putri': [3, 6],
        '10_Putra': [4, 9],  '10_Putri': [4, 9],
        '15_Putra': [6, 12], '15_Putri': [6, 12],
        '25_Putra': [8, 15], '25_Putri': [8, 15],
    },
    'hip': {     # Hip flexion ROM pasif/aktif (derajat) — norma kerja Basketball
        '7_Putra': [90, 105],  '7_Putri': [90, 105],
        '10_Putra': [95, 110], '10_Putri': [95, 110],
        '15_Putra': [100, 115], '15_Putri': [100, 115],
        '25_Putra': [100, 115], '25_Putri': [105, 120],
    },
    'shoulder': {  # Shoulder flexion ROM (derajat) — norma kerja Basketball
        '7_Putra': [150, 165],  '7_Putri': [150, 165],
        '10_Putra': [150, 168], '10_Putri': [150, 168],
        '15_Putra': [155, 170], '15_Putri': [155, 170],
        '25_Putra': [160, 172], '25_Putri': [160, 172],
    },
}
ASIMETRI_L1 = {          # (batas selisih kiri-kanan, penalti poin)
    'ankle': (2, 1),     # cm
    'hip': (10, 1),      # derajat
}
SKOR_KUALITATIF = {'baik': 9, 'cukup': 6, 'kurang': 3}


def interpolasi_skor(nilai, bawah, atas):
    """Identik dengan interpolasiSkor() di Boxing L1."""
    if nilai is None or nilai <= 0:
        return None
    if nilai < bawah:
        return min(1 + 3 * (nilai / bawah), 4.0)
    if nilai <= atas:
        p = (nilai - bawah) / (atas - bawah) if atas > bawah else 1
        return 5 + 2 * p
    rentang = atas * 0.5 if atas > 0 else 1
    p2 = min((nilai - atas) / rentang, 1.0)
    return min(8 + 2 * p2, 10.0)


import math


def _r1(x):
    """Pembulatan 1 desimal half-up (sama dengan Math.round di JS)."""
    return None if x is None else math.floor(x * 10 + 0.5) / 10


def _pair(a, b):
    return [v for v in (a, b) if v is not None and v > 0]


def skor_l1(bucket, gender, ankle_kiri=None, ankle_kanan=None,
            hip_kiri=None, hip_kanan=None, shoulder=None,
            balance_kiri=None, balance_kanan=None, posture=None):
    """Return dict score_ankle/hip/shoulder/stability/posture (0 bila kosong)."""
    g = 'Putri' if gender == 'Putri' else 'Putra'
    key = f'{bucket}_{g}'
    out = {}

    # Ankle: sisi terlemah, penalti asimetri
    v = _pair(ankle_kiri, ankle_kanan)
    if v:
        s = interpolasi_skor(min(v), *RUBRIK_L1['ankle'][key])
        lim, pen = ASIMETRI_L1['ankle']
        if len(v) == 2 and abs(v[0] - v[1]) > lim:
            s = max(1.0, s - pen)
        out['score_ankle'] = _r1(s)
    # Hip: sisi terlemah, penalti asimetri
    v = _pair(hip_kiri, hip_kanan)
    if v:
        s = interpolasi_skor(min(v), *RUBRIK_L1['hip'][key])
        lim, pen = ASIMETRI_L1['hip']
        if len(v) == 2 and abs(v[0] - v[1]) > lim:
            s = max(1.0, s - pen)
        out['score_hip'] = _r1(s)
    # Shoulder: nilai terbaik lengan tembak
    if shoulder and shoulder > 0:
        out['score_shoulder'] = _r1(interpolasi_skor(shoulder, *RUBRIK_L1['shoulder'][key]))
    # Stability: rata-rata skor kiri & kanan (sama dengan Boxing)
    bawah, atas = RUBRIK_L1['stability'][key]
    sk = [interpolasi_skor(x, bawah, atas) for x in (balance_kiri, balance_kanan)]
    sk = [x for x in sk if x is not None]
    if sk:
        out['score_stability'] = _r1(sum(sk) / len(sk))
    # Posture: kualitatif (clamp 0–10)
    if posture is not None and posture > 0:
        out['score_posture'] = _r1(max(0.0, min(10.0, posture)))
    for k in ('score_ankle', 'score_hip', 'score_shoulder', 'score_stability', 'score_posture'):
        out.setdefault(k, 0.0)
    return out


# ══════════════════════════════════════════════════════════════════════
# RUBRIK L2 — 4 ambang awal pita: Fair, Good, Excellent, Superior
# Pita skor: Novice 1.5 · Fair 3.5 · Good 5.5 · Excellent 7.5 · Superior 9.5
# ══════════════════════════════════════════════════════════════════════
BAND_L2 = [1.5, 3.5, 5.5, 7.5, 9.5]
RUBRIK_L2 = {
    'SENIOR': {
        'Putra': {'lower': [1.00, 1.25, 1.50, 1.75], 'upper': [0.75, 1.00, 1.25, 1.50],
                  'core': [45, 75, 105, 135], 'single_leg': [3, 6, 9, 12],
                  'broad': [2.00, 2.30, 2.55, 2.80]},
        'Putri': {'lower': [0.75, 1.00, 1.25, 1.50], 'upper': [0.40, 0.55, 0.70, 0.85],
                  'core': [40, 65, 95, 120], 'single_leg': [3, 6, 9, 12],
                  'broad': [1.60, 1.85, 2.10, 2.30]},
    },
    'JUNIOR': {
        'Putra': {'lower': [0.70, 0.95, 1.20, 1.45], 'upper': [0.60, 0.80, 1.00, 1.20],
                  'core': [40, 65, 95, 120], 'single_leg': [2, 5, 8, 11],
                  'broad': [1.80, 2.10, 2.35, 2.60]},
        'Putri': {'lower': [0.55, 0.75, 1.00, 1.25], 'upper': [0.35, 0.50, 0.65, 0.80],
                  'core': [35, 55, 80, 105], 'single_leg': [2, 5, 8, 11],
                  'broad': [1.50, 1.75, 1.95, 2.15]},
    },
}
RUBRIK_L2['ELITE'] = RUBRIK_L2['SENIOR']
YOUTH_SKOR_L2 = 7.0           # Youth: kualitatif, otomatis 7.0 bila data terisi
ASIMETRI_SINGLE_LEG = (2, 1)  # selisih reps kiri-kanan > 2 -> -1 poin


def band_skor(nilai, ambang):
    s = BAND_L2[0]
    for i in range(4):
        if nilai >= ambang[i]:
            s = BAND_L2[i + 1]
    return s


def skor_l2(kategori_usia, gender, bb=None, squat_1rm=None, bench_1rm=None,
            plank=None, sl_kiri=None, sl_kanan=None, broad_m=None):
    """Return dict score_lower/upper/core/single_leg/broad (0 bila kosong)."""
    kat = kategori_usia if kategori_usia in ('ELITE', 'SENIOR', 'JUNIOR', 'YOUTH') else 'ELITE'
    g = 'Putri' if gender == 'Putri' else 'Putra'
    youth = kat == 'YOUTH'
    tbl = None if youth else RUBRIK_L2[kat][g]
    out = {k: 0.0 for k in ('score_lower', 'score_upper', 'score_core', 'score_single_leg', 'score_broad')}

    def pos(x):
        return x is not None and x > 0

    if pos(squat_1rm) and pos(bb):
        out['score_lower'] = YOUTH_SKOR_L2 if youth else band_skor(squat_1rm / bb, tbl['lower'])
    if pos(bench_1rm) and pos(bb):
        out['score_upper'] = YOUTH_SKOR_L2 if youth else band_skor(bench_1rm / bb, tbl['upper'])
    if pos(plank):
        out['score_core'] = YOUTH_SKOR_L2 if youth else band_skor(plank, tbl['core'])
    if pos(sl_kiri) and pos(sl_kanan):
        if youth:
            out['score_single_leg'] = YOUTH_SKOR_L2
        else:
            s = band_skor(min(sl_kiri, sl_kanan), tbl['single_leg'])
            lim, pen = ASIMETRI_SINGLE_LEG
            if abs(sl_kiri - sl_kanan) > lim:
                s = max(1.0, s - pen)
            out['score_single_leg'] = s
    if pos(broad_m):
        out['score_broad'] = YOUTH_SKOR_L2 if youth else band_skor(broad_m, tbl['broad'])
    return out


# ══════════════════════════════════════════════════════════════════════
# L3 & L4 — pola sama dengan L2: ambang ditulis SEKALI di sini, dikirim ke
# template lewat json_script; JS hanya preview, skor final dihitung server.
# Pita skor: Novice 1.5 · Fair 3.5 · Good 5.5 · Excellent 7.5 · Superior 9.5
# Tes berbasis waktu (lo=True): ambang = batas MAKSIMAL waktu tiap pita
# [Fair, Good, Excellent, Superior]; makin kecil makin baik.
# SEMUA ANGKA = NORMA KERJA HPCS Basketball — validasi dengan data klub/federasi.
# ══════════════════════════════════════════════════════════════════════
YOUTH_SKOR = 7.0   # Youth: kualitatif, otomatis 7.0 bila data terisi (kecuali penilaian coach 0–10)

RUBRIK_L3 = {'SENIOR': {'Putra': {'vj': [35, 45, 55, 65],
                      'sp30': [4.8, 4.5, 4.3, 4.1],
                      'spct': [3.7, 3.45, 3.3, 3.15],
                      'lane': [12.0, 11.5, 11.0, 10.5],
                      'rsi': [1.2, 1.6, 2.0, 2.4],
                      'cod': [11.0, 10.5, 10.0, 9.5]},
            'Putri': {'vj': [25, 33, 41, 49],
                      'sp30': [5.3, 5.0, 4.75, 4.5],
                      'spct': [4.1, 3.85, 3.65, 3.5],
                      'lane': [13.0, 12.4, 11.8, 11.3],
                      'rsi': [1.0, 1.35, 1.7, 2.05],
                      'cod': [12.0, 11.5, 11.0, 10.5]}},
 'JUNIOR': {'Putra': {'vj': [30, 40, 50, 60],
                      'sp30': [5.0, 4.7, 4.45, 4.25],
                      'spct': [3.85, 3.6, 3.4, 3.25],
                      'lane': [12.4, 11.9, 11.4, 10.9],
                      'rsi': [1.0, 1.4, 1.8, 2.2],
                      'cod': [11.5, 11.0, 10.5, 10.0]},
            'Putri': {'vj': [22, 29, 36, 43],
                      'sp30': [5.5, 5.2, 4.95, 4.7],
                      'spct': [4.2, 3.95, 3.75, 3.6],
                      'lane': [13.4, 12.8, 12.2, 11.7],
                      'rsi': [0.9, 1.2, 1.5, 1.85],
                      'cod': [12.4, 11.9, 11.4, 10.9]}}}
RUBRIK_L3['ELITE'] = RUBRIK_L3['SENIOR']

# Definisi bagian skor per pilar: field POST, kunci tabel, lo (waktu), w (bobot), direct (nilai coach 0-10),
# calc (nilai turunan). Bagian tanpa 'id' tabel & bobot 0 hanya informasi (tidak dinilai).
PILAR_L3 = {
    'jump':    [{'id': 'vj',   'field': 'vertical_jump_cm',   'key': 'vj',   'lo': False, 'w': 1}],
    'sprint':  [{'id': 'sp30', 'field': 'sprint_30m_detik',   'key': 'sp30', 'lo': True,  'w': 1},
                {'id': 'spct', 'field': 'sprint_court_detik', 'key': 'spct', 'lo': True,  'w': 1}],
    'agility': [{'id': 'lane', 'field': 'lane_agility_detik', 'key': 'lane', 'lo': True,  'w': 1}],
    'rsi':     [{'id': 'rsi',  'field': 'rsi_value',          'key': 'rsi',  'lo': False, 'w': 1}],
    'cod':     [{'id': 'cod',  'field': 'cod_detik',          'key': 'cod',  'lo': True,  'w': 1}],
}

RUBRIK_L4 = {'SENIOR': {'Putra': {'ft': [55, 68, 78, 86],
                      'mid': [28, 36, 43, 50],
                      'three': [20, 28, 34, 40],
                      'dom': [10.5, 9.5, 8.7, 8.0],
                      'weak': [75, 85, 90, 95],
                      'lat': [6.2, 5.8, 5.4, 5.0],
                      'cont': [40, 55, 70, 85],
                      'yoyo': [800, 1200, 1600, 2000]},
            'Putri': {'ft': [50, 62, 72, 80],
                      'mid': [25, 32, 39, 45],
                      'three': [18, 25, 31, 37],
                      'dom': [11.5, 10.5, 9.6, 8.8],
                      'weak': [75, 85, 90, 95],
                      'lat': [6.8, 6.4, 6.0, 5.6],
                      'cont': [40, 55, 70, 85],
                      'yoyo': [520, 800, 1120, 1440]}},
 'JUNIOR': {'Putra': {'ft': [50, 62, 72, 80],
                      'mid': [25, 32, 39, 45],
                      'three': [18, 25, 31, 37],
                      'dom': [11.0, 10.0, 9.2, 8.5],
                      'weak': [72, 82, 88, 93],
                      'lat': [6.5, 6.1, 5.7, 5.3],
                      'cont': [35, 50, 65, 80],
                      'yoyo': [680, 1040, 1400, 1800]},
            'Putri': {'ft': [45, 57, 67, 75],
                      'mid': [22, 28, 35, 41],
                      'three': [15, 21, 27, 33],
                      'dom': [12.0, 11.0, 10.1, 9.3],
                      'weak': [72, 82, 88, 93],
                      'lat': [7.0, 6.6, 6.2, 5.8],
                      'cont': [35, 50, 65, 80],
                      'yoyo': [440, 680, 960, 1240]}}}
RUBRIK_L4['ELITE'] = RUBRIK_L4['SENIOR']

PILAR_L4 = {
    'shooting':     [{'id': 'ft',    'field': 'free_throw_pct',  'key': 'ft',    'lo': False, 'w': 1},
                     {'id': 'mid',   'field': 'midrange_pct',    'key': 'mid',   'lo': False, 'w': 1},
                     {'id': 'three', 'field': 'three_point_pct', 'key': 'three', 'lo': False, 'w': 1}],
    'dribbling':    [{'id': 'dom',   'field': 'dribble_speed_dominant', 'key': 'dom',  'lo': True,  'w': 0.6},
                     {'id': 'weak',  'calc': 'weakratio',               'key': 'weak', 'lo': False, 'w': 0.4}],
    'defense':      [{'id': 'lat',   'field': 'lateral_speed_detik', 'key': 'lat',  'lo': True,  'w': 1},
                     {'id': 'cont',  'field': 'contest_rate_pct',    'key': 'cont', 'lo': False, 'w': 1}],
    'iq':           [{'id': 'court_vision_score', 'field': 'court_vision_score', 'direct': True, 'w': 1},
                     {'id': 'decision_speed',     'field': 'decision_speed',     'direct': True, 'w': 1}],
    'conditioning': [{'id': 'yoyo',  'field': 'yoyo_jarak_m', 'key': 'yoyo', 'lo': False, 'w': 1}],
}


def band_skor_lo(nilai, ambang):
    """Tes waktu: ambang = batas maksimal [Fair, Good, Excellent, Superior]."""
    if nilai <= ambang[3]:
        return BAND_L2[4]
    if nilai <= ambang[2]:
        return BAND_L2[3]
    if nilai <= ambang[1]:
        return BAND_L2[2]
    if nilai <= ambang[0]:
        return BAND_L2[1]
    return BAND_L2[0]


def _nilai_bagian(part, vals):
    if part.get('calc') == 'weakratio':
        d, w = vals.get('dribble_speed_dominant'), vals.get('dribble_speed_weak')
        return d / w * 100 if d and w and d > 0 and w > 0 else None
    v = vals.get(part['field'])
    return v if v is not None and v > 0 else None


def skor_pilar(parts, vals, tabel, kategori, gender):
    """Rata-rata berbobot bagian yang terisi (sama dengan scorePilar() di JS). 0.0 bila kosong."""
    kat = kategori if kategori in ('ELITE', 'SENIOR', 'JUNIOR', 'YOUTH') else 'ELITE'
    g = 'Putri' if gender == 'Putri' else 'Putra'
    total, bobot = 0.0, 0.0
    for p in parts:
        v = _nilai_bagian(p, vals)
        if v is None:
            continue
        if p.get('direct'):
            s = min(10.0, v)
        elif kat == 'YOUTH':
            s = YOUTH_SKOR
        else:
            t = tabel[kat][g][p['key']]
            s = band_skor_lo(v, t) if p['lo'] else band_skor(v, t)
        total += s * p['w']
        bobot += p['w']
    return _r1(total / bobot) if bobot else 0.0


def skor_l3(kategori_usia, gender, vj=None, sp30=None, spct=None, lane=None, rsi=None, cod=None):
    vals = {'vertical_jump_cm': vj, 'sprint_30m_detik': sp30, 'sprint_court_detik': spct,
            'lane_agility_detik': lane, 'rsi_value': rsi, 'cod_detik': cod}
    f = lambda k: skor_pilar(PILAR_L3[k], vals, RUBRIK_L3, kategori_usia, gender)
    return {'score_jump': f('jump'), 'score_sprint': f('sprint'), 'score_agility': f('agility'),
            'score_rsi': f('rsi'), 'score_cod': f('cod')}


def skor_l4(kategori_usia, gender, ft=None, mid=None, three=None, dom=None, weak=None,
            lat=None, cont=None, yoyo_m=None, vision=None, decision=None):
    """score_iq ikut dihitung di sini untuk konsistensi preview; model juga menghitungnya sendiri."""
    vals = {'free_throw_pct': ft, 'midrange_pct': mid, 'three_point_pct': three,
            'dribble_speed_dominant': dom, 'dribble_speed_weak': weak,
            'lateral_speed_detik': lat, 'contest_rate_pct': cont, 'yoyo_jarak_m': yoyo_m,
            'court_vision_score': vision, 'decision_speed': decision}
    f = lambda k: skor_pilar(PILAR_L4[k], vals, RUBRIK_L4, kategori_usia, gender)
    return {'score_shooting': f('shooting'), 'score_dribbling': f('dribbling'),
            'score_defense': f('defense'), 'score_iq': f('iq'), 'score_conditioning': f('conditioning')}


def payload_l3():
    return {'tables': RUBRIK_L3, 'band': BAND_L2, 'youth': YOUTH_SKOR, 'pillars': PILAR_L3}


def payload_l4():
    return {'tables': RUBRIK_L4, 'band': BAND_L2, 'youth': YOUTH_SKOR, 'pillars': PILAR_L4}
