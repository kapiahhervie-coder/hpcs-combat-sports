path = r'combat\templates\combat\l3_power.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

results = []

# ══════════════════════════════════════════════════════
# FIX 1: Hapus tombol AI Camera di setiap pilar
# ══════════════════════════════════════════════════════
import re

# Hapus semua button btn-cam di dalam pilar form (bukan di header)
patterns_to_remove = [
    r'<button type="button" class="btn btn-cam" style="width:100%[^"]*"[^>]*>\s*<i class="bi bi-camera-video-fill"></i>[^<]*</button>',
]
for pat in patterns_to_remove:
    before = len(c)
    c = re.sub(pat, '', c, flags=re.DOTALL)
    if len(c) < before:
        results.append('OK 1: tombol AI Camera di pilar dihapus')

results.append('OK 1: selesai hapus kamera pilar')

# ══════════════════════════════════════════════════════
# FIX 2: Tambah panel Narasi + Risiko Cedera + Rekomendasi L4
# Ganti rekomendasi lama dengan yang lebih lengkap
# ══════════════════════════════════════════════════════
OLD_REKO_PANEL = '''          <div class="rekomendasi" id="rekomendasi">
            <div class="rekomendasi-title">Analisis Power L3:</div>
            <div id="rekomendasi_text"></div>
          </div>'''

NEW_REKO_PANEL = '''          <!-- Profil Kondisi Atlet -->
          <div id="narasi_l3" style="display:none;margin-top:10px;text-align:left;">
            <div style="font-size:10px;font-weight:700;color:var(--amber);letter-spacing:1px;margin-bottom:6px;">
              &#9889; PROFIL KONDISI ATLET
            </div>
            <div id="narasi_box_l3" style="
              background:rgba(245,158,11,0.05);
              border:1px solid rgba(245,158,11,0.2);
              border-radius:10px;padding:12px;
              font-size:11px;line-height:1.7;
              color:#9ca3af;max-height:280px;
              overflow-y:auto;text-align:left;">
            </div>
          </div>

          <!-- Rekomendasi Latihan -->
          <div class="rekomendasi" id="rekomendasi" style="text-align:left;">
            <div class="rekomendasi-title">&#128203; Rekomendasi Pelatih:</div>
            <div id="rekomendasi_text"></div>
          </div>'''

if OLD_REKO_PANEL in c:
    c = c.replace(OLD_REKO_PANEL, NEW_REKO_PANEL)
    results.append('OK 2: panel narasi & rekomendasi ditambahkan')
else:
    results.append('SKIP 2: panel lama tidak ditemukan')

# ══════════════════════════════════════════════════════
# FIX 3: Tambah tombol cetak di tabel history
# ══════════════════════════════════════════════════════
old_hapus = """              <a href="{% url 'combat:hapus_l3_audit' item.pk %}" class="btn-del-sm"
                 onclick="return confirm('Hapus data {{ item.atlet_name|escapejs }}?')">
                <i class="bi bi-trash"></i>
              </a>"""

new_hapus = """              <a href="{% url 'combat:hapus_l3_audit' item.pk %}" class="btn-del-sm"
                 onclick="return confirm('Hapus data {{ item.atlet_name|escapejs }}?')">
                <i class="bi bi-trash"></i>
              </a>
              <button onclick="window.print()" title="Cetak PDF"
                style="background:transparent;border:1px solid rgba(245,158,11,0.4);
                       color:#f59e0b;margin-left:4px;border-radius:6px;
                       padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-printer-fill"></i>
              </button>"""

if old_hapus in c:
    c = c.replace(old_hapus, new_hapus)
    results.append('OK 3: tombol cetak PDF di tabel ditambahkan')
else:
    results.append('SKIP 3: pattern hapus tidak ditemukan')

# ══════════════════════════════════════════════════════
# FIX 4: Ganti logika rekomendasi lama + tambah narasi lengkap
# ══════════════════════════════════════════════════════
OLD_LOGIC = """    if (a >= 9.0) {
      badge.className = 'result-badge elite'; badge.textContent = 'ELITE';
      rekT.innerHTML = '<b>Kapasitas Power Eksplosif Tinggi.</b> Atlet SIAP KOMPETISI. Pertahankan RSI > 2.5 dan sprint < 3.8 dtk.';
    } else if (a >= 7.0) {
      badge.className = 'result-badge ready'; badge.textContent = 'READY';
      rekT.innerHTML = '<b>Kompeten.</b> Tingkatkan pilar terendah dengan plyometric progresif 2x/minggu. Target ELITE dalam 8minggu.';
    } else if (a >= 5.0) {
      badge.className = 'result-badge developing'; badge.textContent = 'DEVELOPING';
      rekT.innerHTML = '<b>Dalam Pengembangan.</b> Pastikan fondasi L2 solid sebelum menambah volume power. Fokus RSI dan sprint.';
    } else {
      badge.className = 'result-badge novice'; badge.textContent = 'NOVICE';
      rekT.innerHTML = '<b>Power Dasar Lemah.</b> Kembali perkuat L2 Strength. Power tidak bisa dibangun tanpa fondasi kekuatan.';
    }"""

NEW_LOGIC = """    // ── Predikat & Badge ──
    var pred = 'NOVICE';
    if (a >= 9.0)      { badge.className = 'result-badge elite';      badge.textContent = 'ELITE';      pred = 'ELITE'; }
    else if (a >= 7.0) { badge.className = 'result-badge ready';      badge.textContent = 'READY';      pred = 'READY'; }
    else if (a >= 5.0) { badge.className = 'result-badge developing'; badge.textContent = 'DEVELOPING'; pred = 'DEVELOPING'; }
    else               { badge.className = 'result-badge novice';     badge.textContent = 'NOVICE';     pred = 'NOVICE'; }

    // ── Pilar data ──
    var pilarArr = [
      {nama:'Jump',    val: scores.jump    || 0},
      {nama:'Sprint',  val: scores.sprint  || 0},
      {nama:'Throw',   val: scores.throw   || 0},
      {nama:'RSI',     val: scores.rsi     || 0},
      {nama:'Agility', val: scores.agility || 0}
    ];
    var filled = pilarArr.filter(function(p){return p.val>0;});
    var sorted = filled.slice().sort(function(a,b){return a.val-b.val;});
    var lemah  = sorted.slice(0,2);
    var kuat   = filled.slice().sort(function(a,b){return b.val-a.val;}).slice(0,2);

    function wrn(v){return v>=9?'#fbbf24':v>=7?'#38bdf8':v>=5?'#f59e0b':'#f87171';}
    function lbl(v){return v>=9?'sangat baik':v>=7?'baik':v>=5?'cukup':'perlu perhatian';}

    // ── Narasi Profil Atlet ──
    var namaEl = document.querySelector('select option:checked');
    var nama = namaEl && namaEl.value ? (namaEl.getAttribute('data-nama') || namaEl.textContent.trim()) : 'Atlet';

    // Risiko cedera berdasarkan skor
    var risikoList = [];
    if ((scores.rsi||0) < 5)     risikoList.push('&#9888; RSI rendah — risiko cedera lutut & ankle saat mendarat (kurang kontrol SSC)');
    if ((scores.jump||0) < 5)    risikoList.push('&#9888; Explosive power rendah — risiko strain otot posterior chain');
    if ((scores.sprint||0) < 5)  risikoList.push('&#9888; Sprint lemah — risiko hamstring strain saat akselerasi maksimal');
    if ((scores.agility||0) < 5) risikoList.push('&#9888; Agility rendah — risiko ankle sprain saat change of direction');
    if ((scores.throw||0) < 5)   risikoList.push('&#9888; Upper power lemah — risiko rotator cuff overload');
    if (risikoList.length === 0)  risikoList.push('&#10003; Profil risiko cedera RENDAH — kapasitas power seimbang');

    var risikoHTML = risikoList.map(function(r){
      return '<div style="margin-bottom:4px;font-size:10.5px;color:'+(r.includes('&#9888;')?'#f87171':'#10b981')+';">'+r+'</div>';
    }).join('');

    // Layak ke L4?
    var layakL4 = a >= 7.0;
    var layakStr = a >= 9.0
      ? '<span style="color:#fbbf24;font-weight:700">&#127942; ELITE — Atlet SIAP KOMPETISI & LAYAK ke L4 Speed Agility</span>'
      : layakL4
      ? '<span style="color:#38bdf8;font-weight:700">&#9989; LAYAK ke L4 Speed & Agility — lanjutkan program</span>'
      : '<span style="color:#f87171;font-weight:700">&#9940; BELUM LAYAK ke L4 — Perkuat L3 Power minimal 6 minggu lagi</span>';

    var min2 = Math.min.apply(null, filled.map(function(p){return p.val;}));
    var max2 = Math.max.apply(null, filled.map(function(p){return p.val;}));
    var prima = (max2-min2)<=0.5 && min2>=8.5;

    var kPred = {
      ELITE:      'menunjukkan kapasitas power eksplosif <strong style="color:#fbbf24">ELIT</strong> — siap kompetisi penuh.',
      READY:      'berada di level <strong style="color:#38bdf8">SIAP</strong> — power solid, tinggal optimasi detail.',
      DEVELOPING: 'sedang <strong style="color:#f59e0b">BERKEMBANG</strong> — fondasi power terbentuk, butuh konsistensi.',
      NOVICE:     'di level <strong style="color:#f87171">PEMULA</strong> — perlu kembali ke L2 Strength 6-8 minggu.'
    };

    var narEl = document.getElementById('narasi_l3');
    var narBox = document.getElementById('narasi_box_l3');
    if (narEl && narBox && filled.length > 0) {
      narBox.innerHTML = ''
        +'<div style="margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid rgba(245,158,11,0.1);">'
        +'<span style="color:#fbbf24;font-weight:700;font-size:12px;">&#9889; '+nama+'</span> '+(kPred[pred]||'')
        +' Total: <strong style="color:'+wrn(a)+'">'+a.toFixed(1)+'/10</strong></div>'
        +'<div style="margin-bottom:8px;"><div style="color:#6b7280;font-size:9px;letter-spacing:1px;margin-bottom:4px;">&#9650; KEUNGGULAN POWER</div>'
        +kuat.map(function(p){return '<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;"><div style="width:5px;height:5px;border-radius:50%;background:#fbbf24;"></div><span><strong style="color:#fbbf24">'+p.nama+'</strong> — '+lbl(p.val)+' <span style="color:'+wrn(p.val)+';font-weight:700">('+p.val.toFixed(1)+')</span></span></div>';}).join('')+'</div>'
        +'<div style="margin-bottom:8px;"><div style="color:#6b7280;font-size:9px;letter-spacing:1px;margin-bottom:4px;">&#9660; AREA KELEMAHAN</div>'
        +(prima?'<div style="color:#fbbf24;font-size:10.5px;">&#127942; Semua pilar power prima!</div>':lemah.map(function(p){return '<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;"><div style="width:5px;height:5px;border-radius:50%;background:'+wrn(p.val)+';"></div><span><strong style="color:'+wrn(p.val)+'">'+p.nama+'</strong> — '+lbl(p.val)+' <span style="color:'+wrn(p.val)+';font-weight:700">('+p.val.toFixed(1)+')</span></span></div>';}).join(''))+'</div>'
        +'<div style="margin-bottom:8px;"><div style="color:#6b7280;font-size:9px;letter-spacing:1px;margin-bottom:4px;">&#9888; ANALISIS RISIKO CEDERA</div>'+risikoHTML+'</div>'
        +'<div style="padding:8px 10px;border-radius:8px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);">'
        +'<div style="color:#6b7280;font-size:9px;letter-spacing:1px;margin-bottom:4px;">&#128203; KELAYAKAN KE L4</div>'
        +layakStr+'<br><span style="color:#9ca3af;font-size:10px;">'
        +(a>=9.0?'Atlet siap L4 Speed & Agility dengan beban penuh. Pertahankan volume power.':layakL4?'Lanjut ke L4. Fokus perbaiki '+( lemah[0]?lemah[0].nama:'-')+' selama program L4 berlangsung.':'Selesaikan program L3 dulu. Targetkan skor minimal 7.0 sebelum ke L4.')
        +'</span></div>';
      narEl.style.display = 'block';
    }

    // ── Rekomendasi Latihan Lengkap ──
    var REKO = {
      Jump:    {low:['Box Jump 3x5 dari 30cm — fokus pendaratan lembut','Squat Jump 4x6 dengan BW','Depth Drop 3x8 untuk aktivasi SSC','Kembali ke L2 Lower Strength'],mid:['CMJ progresif: +2cm target tiap 2 minggu','Weighted Jump Squat 3x5 dengan 10% BW','Reactive Jump box 40-50cm 3x6'],high:['Depth Jump 60cm 3x5 untuk peak SSC','Single Leg Box Jump untuk simetri power','Nordic Hamstring 2x/minggu untuk perlindungan']},
      Sprint:  {low:['Acceleration Drill 10m x8 — fokus postur','A-Skip & B-Skip 3x20m untuk mekanika','Hill Sprint 6x30m untuk power dasar','Resistance Band Sprint 4x20m'],mid:['Flying Sprint 30m x6 dengan istirahat penuh','Wicket Drill untuk stride frequency','Block Start Practice 5x30m'],high:['Max Velocity Sprint 1x/minggu','Overspeed Training dengan tali elastis 3x30m','GPS tracking untuk monitoring waktu']},
      Throw:   {low:['MB Chest Pass 3x10 dengan 3kg','Overhead MB Throw 4x8 untuk total body power','Rotational Throw 3x10 tiap sisi dengan 4kg'],mid:['MB Slam 4x8 dengan 5-6kg','Standing Long Throw: +0.5m target per sesi','Rotational Power Throw 3x8 dengan resistance'],high:['MB Shot Put 4x6 untuk peak upper power','Rotational MB 2x/minggu integrate boxing drill']},
      RSI:     {low:['Ankle Stiffness: Quick Hop 3x15 detik','Pogo Jump 3x20 untuk SSC dasar','Double Leg Bound 3x8 untuk GCT','Calf Raise explosive 4x15'],mid:['Single Leg Pogo 3x15 tiap kaki','Hurdle Hop 3x6 dengan mini hurdle 30cm','Drop Jump 40cm — target GCT < 0.2 dtk'],high:['Depth Jump 60cm minimal GCT','Continuous Hurdle Hop 3x8 untuk peak RSI','Pertahankan RSI>2.5 dengan reactive drill']},
      Agility: {low:['Ladder Drill 2-in 2-out 3x panjang','T-Test dasar 4x fokus teknik cutting','Cone Drill 5-10-5 untuk COD dasar'],mid:['505 Agility 4x tiap arah','Reactive Agility visual stimulus 3x6','Mirror Drill dengan partner 3x30 dtk'],high:['Boxing footwork drill 3x1 menit','Reactive Drill 2x/minggu','Video analysis cutting mechanics']}
    };

    var rekoHTML = '<div style="font-size:10px;font-weight:700;color:#f59e0b;margin-bottom:8px;letter-spacing:1px;">PROGRAM REKOMENDASI PELATIH</div>';
    var topLemah = sorted.slice(0,3);
    topLemah.forEach(function(p){
      var db = REKO[p.nama];
      if (!db) return;
      var tips = p.val<5.5?db.low:p.val<7.5?db.mid:db.high;
      var col  = p.val<5.5?'#f87171':p.val<7.5?'#f59e0b':'#fbbf24';
      rekoHTML += '<div style="margin-bottom:8px;padding:7px 10px;background:rgba(245,158,11,0.04);border-radius:6px;border-left:3px solid '+col+';">'
        +'<div style="font-size:10px;font-weight:700;color:'+col+';margin-bottom:4px;">'+(p.val<5.5?'&#128308;':p.val<7.5?'&#128993;':'&#128994;')+' '+p.nama.toUpperCase()+' — '+p.val.toFixed(1)+'/10</div>';
      tips.forEach(function(t){
        rekoHTML += '<div style="display:flex;gap:5px;margin-bottom:2px;font-size:10px;color:#9ca3af;"><span style="color:'+col+';flex-shrink:0;">&#8594;</span><span>'+t+'</span></div>';
      });
      rekoHTML += '</div>';
    });

    rekT.innerHTML = rekoHTML;"""

if OLD_LOGIC in c:
    c = c.replace(OLD_LOGIC, NEW_LOGIC)
    results.append('OK 4: logika rekomendasi & narasi lengkap ditambahkan')
else:
    results.append('SKIP 4: logika lama tidak ditemukan persis')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print()
print('='*55)
print('  HASIL FIX L3 COMPLETE')
print('='*55)
for r in results:
    print(' ', r)
print('='*55)
print('  FILE TERSIMPAN')
print()
print('  Jalankan: python manage.py runserver')
