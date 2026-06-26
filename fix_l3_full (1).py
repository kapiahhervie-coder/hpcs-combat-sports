path = r'combat\templates\combat\l3_power.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

results = []

# ══════════════════════════════════════════════════════
# FIX 1: Hapus tombol Print duplikat di header
# Tinggalkan hanya 1 di kanan atas
# ══════════════════════════════════════════════════════
old_print_btn = '''      <button type="button" class="btn btn-ghost" onclick="handlePrint()">
        <i class="bi bi-printer-fill"></i> Print
      </button>'''

if old_print_btn in c:
    c = c.replace(old_print_btn, '')
    results.append('OK 1: tombol Print duplikat di header dihapus')
else:
    results.append('SKIP 1')

# ══════════════════════════════════════════════════════
# FIX 2: Ganti warna tema L3 dari amber/orange ke Power Gold
# L3 Power = warna emas/kuning yang powerful
# ══════════════════════════════════════════════════════
color_fixes = [
    ('--amber: #f59e0b', '--amber: #fbbf24'),
    ('--amber: #F59E0B', '--amber: #fbbf24'),
]
for old, new in color_fixes:
    if old in c:
        c = c.replace(old, new)
        results.append(f'OK 2: warna {old[:15]} diupdate')

# ══════════════════════════════════════════════════════
# FIX 3: Tambah tombol Cetak PDF di tabel history
# ══════════════════════════════════════════════════════
old_hapus = '''              <a href="{% url 'combat:hapus_l3_audit' item.pk %}" class="btn-del-sm"
                 onclick="return confirm('Hapus data {{ item.atlet_name|escapejs }}?')">
                <i class="bi bi-trash"></i>
              </a>'''

new_hapus = '''              <a href="{% url 'combat:hapus_l3_audit' item.pk %}" class="btn-del-sm"
                 onclick="return confirm('Hapus data {{ item.atlet_name|escapejs }}?')">
                <i class="bi bi-trash"></i>
              </a>
              <button class="btn-del-sm" onclick="window.print()" title="Cetak PDF"
                      style="background:transparent;border:1px solid rgba(56,189,248,0.3);color:#38bdf8;margin-left:4px;border-radius:6px;padding:4px 8px;cursor:pointer;">
                <i class="bi bi-printer-fill"></i>
              </button>'''

if old_hapus in c:
    c = c.replace(old_hapus, new_hapus)
    results.append('OK 3: tombol cetak PDF ditambahkan di tabel')
else:
    results.append('SKIP 3: pola hapus tidak ditemukan')

# ══════════════════════════════════════════════════════
# FIX 4: Tambah panel Narasi Kondisi Atlet + Rekomendasi
# di bawah radar chart (kolom tengah)
# ══════════════════════════════════════════════════════
NARASI_PANEL = '''
          <!-- Narasi Kondisi Atlet -->
          <div id="narasi_panel_l3" style="display:none;margin-top:12px;text-align:left;">
            <div class="card-title" style="font-size:11px;margin-bottom:6px;">
              <i class="bi bi-person-lines-fill" style="color:#fbbf24"></i> Profil Kondisi Atlet
            </div>
            <div id="narasi_box_l3" style="
              background:rgba(251,191,36,0.05);
              border:1px solid rgba(251,191,36,0.2);
              border-radius:10px;
              padding:12px 14px;
              font-size:11px;
              line-height:1.7;
              color:#9ca3af;
              max-height:300px;
              overflow-y:auto;
            "></div>
          </div>'''

# Sisipkan setelah canvas radar
target = '<img id="chartPrintImg" alt="Radar" style="display:none;width:100%;max-width:400px">'
if target in c and 'narasi_panel_l3' not in c:
    c = c.replace(target, target + NARASI_PANEL)
    results.append('OK 4: panel narasi L3 ditambahkan')
else:
    results.append('SKIP 4: target tidak ditemukan atau sudah ada')

# ══════════════════════════════════════════════════════
# FIX 5: Tambah fungsi generateNarasiL3 + generateRekoL3
# ══════════════════════════════════════════════════════
NARASI_JS = """
// ── Narasi & Rekomendasi L3 Power ────────────────────
var REKO_L3 = {
  jump:{
    low:[
      'Box Jump 3x5 dari ketinggian 30cm — fokus pendaratan lembut',
      'Squat Jump 4x6 dengan BW — bangun kekuatan awal',
      'Depth Drop 3x8 untuk aktivasi SSC dasar',
      'Kembali ke L2 untuk perkuat Lower Strength terlebih dahulu'
    ],
    mid:[
      'CMJ progresif: tambah 2cm target tiap 2 minggu',
      'Weighted Jump Squat 3x5 dengan 10-20% BW',
      'Reactive Jump dengan box 40-50cm 3x6'
    ],
    high:[
      'Pertahankan CMJ > 55cm dengan Nordic Hamstring 2x/minggu',
      'Depth Jump dari 60cm 3x5 untuk peak SSC',
      'Variasi: Single Leg Box Jump untuk power simetri'
    ]
  },
  sprint:{
    low:[
      'Acceleration Drill 10m x 8 reps — fokus postur',
      'A-Skip & B-Skip 3x20m untuk mekanika sprint',
      'Hill Sprint 6x30m untuk power output dasar',
      'Resistance Band Sprint 4x20m'
    ],
    mid:[
      'Flying Sprint 30m x 6 dengan istirahat penuh',
      'Wicket Drill untuk stride frequency',
      'Block Start Practice 5x30m'
    ],
    high:[
      'Pertahankan dengan Max Velocity Sprint 1x/minggu',
      'Overspeed Training dengan tali elastis 3x30m',
      'Sprint dengan GPS tracking untuk monitoring'
    ]
  },
  throw:{
    low:[
      'Medicine Ball Chest Pass 3x10 dengan 3kg',
      'Overhead MB Throw 4x8 untuk total body power',
      'Rotational Throw 3x10 tiap sisi dengan 4kg',
      'Wall Ball 3x12 untuk explosive upper body'
    ],
    mid:[
      'MB Slam 4x8 dengan 5-6kg',
      'Standing Long Throw progresif: tambah 0.5m target',
      'Rotational Power Throw 3x8 dengan resistance'
    ],
    high:[
      'MB Shot Put 4x6 untuk peak upper power',
      'Pertahankan dengan Rotational Medicine Ball 2x/minggu',
      'Integrate throwing dalam drill spesifik boxing'
    ]
  },
  rsi:{
    low:[
      'Ankle Stiffness Drill: Quick Hop 3x15 detik',
      'Pogo Jump 3x20 untuk SSC dasar',
      'Double Leg Bound 3x8 untuk ground contact time',
      'Calf Raise explosive 4x15 untuk ankle stiffness'
    ],
    mid:[
      'Single Leg Pogo 3x15 tiap kaki',
      'Hurdle Hop 3x6 dengan mini hurdle 30cm',
      'Drop Jump dari 40cm — target GCT < 0.2 detik'
    ],
    high:[
      'Depth Jump dari 60cm dengan minimal GCT',
      'Continuous Hurdle Hop 3x8 untuk peak RSI',
      'Pertahankan RSI > 2.5 dengan reactive drill 2x/minggu'
    ]
  },
  agility:{
    low:[
      'Ladder Drill: 2-in 2-out 3x1 panjang',
      'T-Test dasar 4x dengan fokus teknik cutting',
      'Cone Drill 5-10-5 untuk change of direction dasar',
      '4 Corner Drill 3x untuk koordinasi'
    ],
    mid:[
      '505 Agility Test 4x tiap arah',
      'Reactive Agility dengan visual stimulus 3x6',
      'Mirror Drill dengan partner 3x30 detik'
    ],
    high:[
      'Sport-specific Agility: boxing footwork drill 3x1 menit',
      'Pertahankan dengan Reactive Drill 2x/minggu',
      'Video analysis untuk optimasi cutting mechanics'
    ]
  }
};

function generateNarasiL3(pilarData, total, pred) {
  var panel = document.getElementById('narasi_panel_l3');
  var box   = document.getElementById('narasi_box_l3');
  if (!panel || !box) return;

  var filled = pilarData.filter(function(p){ return p.val > 0; });
  if (!filled.length) { panel.style.display = 'none'; return; }

  var namaEl = document.querySelector('select option:checked') ||
               document.querySelector('#h_atlet_name');
  var nama = namaEl ? (namaEl.getAttribute('data-nama') || namaEl.value || namaEl.text || 'Atlet') : 'Atlet';
  if (nama === '— Pilih Atlet —' || nama === '') nama = 'Atlet';

  function wrn(v){ return v>=9?'#fbbf24':v>=7?'#38bdf8':v>=5?'#f59e0b':'#f87171'; }
  function lbl(v){ return v>=9?'sangat baik':v>=7?'baik':v>=5?'cukup':'perlu perhatian'; }

  var sorted = filled.slice().sort(function(a,b){ return b.val-a.val; });
  var kuat   = sorted.slice(0,2);
  var lemah  = sorted.slice(-2).reverse();

  var min = Math.min.apply(null, filled.map(function(p){return p.val;}));
  var max = Math.max.apply(null, filled.map(function(p){return p.val;}));
  var prima = (max-min) <= 0.5 && min >= 8.5;
  var layak = total >= 7.5;

  var kPred = {
    ELITE:      'menunjukkan kapasitas power eksplosif <strong style="color:#fbbf24">ELIT</strong> — SIAP KOMPETISI PENUH.',
    READY:      'berada di level <strong style="color:#38bdf8">SIAP (READY)</strong> — power solid, tinggal optimasi detail.',
    DEVELOPING: 'sedang <strong style="color:#f59e0b">BERKEMBANG</strong> — fondasi power mulai terbentuk, butuh konsistensi.',
    NOVICE:     'di level <strong style="color:#f87171">PEMULA</strong> — perlu kembali ke L2 Strength 6-8 minggu.'
  };

  var layakStr = total >= 9.0
    ? '<span style="color:#fbbf24;font-weight:700">&#127942; ELITE — Atlet SIAP KOMPETISI PENUH</span>'
    : layak
    ? '<span style="color:#38bdf8;font-weight:700">&#9989; LAYAK bertahan di L3, optimasi menuju kompetisi</span>'
    : '<span style="color:#f87171;font-weight:700">&#9940; BELUM LAYAK — Kembali ke L2 Strength</span>';

  var lemahHTML = prima
    ? '<div style="padding:8px 10px;background:rgba(251,191,36,0.07);border-radius:6px;border:1px solid rgba(251,191,36,0.2);"><span style="color:#fbbf24;font-weight:600">&#127942; Semua pilar power dalam kondisi prima!</span></div>'
    : lemah.map(function(p){
        return '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
          +'<div style="width:6px;height:6px;border-radius:50%;background:'+wrn(p.val)+';flex-shrink:0;"></div>'
          +'<span><strong style="color:'+wrn(p.val)+'">'+p.nama+'</strong> — '+lbl(p.val)
          +' <span style="color:'+wrn(p.val)+';font-weight:700;">('+p.val.toFixed(1)+'/10)</span>'
          +(p.val<5.5?' : prioritas program korektif.':' : perlu peningkatan.')+'</span></div>';
      }).join('');

  var fokus = prima
    ? 'Pertahankan semua pilar. Tingkatkan volume kompetisi.'
    : layak
    ? 'Fokus tingkatkan <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> dengan program plyometric spesifik.'
    : 'Kembali ke L2 Strength, perkuat <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> dan <strong>'+(lemah[1]?lemah[1].nama:'-')+'</strong>.';

  box.innerHTML = ''
    +'<div style="margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid rgba(251,191,36,0.1);">'
    +'<span style="color:#fbbf24;font-weight:700;font-size:12px;">&#9889; '+nama+'</span> '+(kPred[pred]||'')
    +' Total skor: <strong style="font-size:13px;color:'+wrn(total)+'">'+total.toFixed(1)+'/10</strong></div>'
    +'<div style="margin-bottom:10px;"><div style="color:#6b7280;font-size:10px;margin-bottom:5px;letter-spacing:1px;">&#9650; KEUNGGULAN POWER</div>'
    +kuat.map(function(p){return '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><div style="width:6px;height:6px;border-radius:50%;background:#fbbf24;flex-shrink:0;"></div><span><strong style="color:#fbbf24">'+p.nama+'</strong> — '+lbl(p.val)+' <span style="color:'+wrn(p.val)+';font-weight:700;">('+p.val.toFixed(1)+'/10)</span></span></div>';}).join('')+'</div>'
    +'<div style="margin-bottom:10px;"><div style="color:#6b7280;font-size:10px;margin-bottom:5px;letter-spacing:1px;">&#9660; AREA KELEMAHAN</div>'+lemahHTML+'</div>'
    +'<div style="padding:10px 12px;border-radius:8px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);">'
    +'<div style="color:#6b7280;font-size:10px;margin-bottom:6px;letter-spacing:1px;">&#128203; KESIMPULAN</div>'
    +layakStr+'<br><span style="color:#9ca3af;font-size:10.5px;">'+fokus+'</span></div>';

  panel.style.display = 'block';
}

function generateRekoL3(pilarData) {
  var panel = document.getElementById('rekomendasi');
  var list  = document.getElementById('rekomendasi_text');
  if (!panel || !list) return;

  var filled  = pilarData.filter(function(p){ return p.val > 0; });
  if (!filled.length) { panel.classList.remove('show'); return; }

  var sorted  = filled.slice().sort(function(a,b){ return a.val-b.val; });
  var weakest = sorted.slice(0,3);
  var html = '<div style="font-size:10px;font-weight:700;color:#fbbf24;margin-bottom:8px;letter-spacing:1px;">PROGRAM REKOMENDASI PELATIH</div>';

  weakest.forEach(function(p) {
    var key = p.nama.toLowerCase();
    var db  = REKO_L3[key];
    if (!db) return;
    var tips = p.val < 5.5 ? db.low : p.val < 7.5 ? db.mid : db.high;
    var col  = p.val < 5.5 ? '#f87171' : p.val < 7.5 ? '#f59e0b' : '#fbbf24';
    var icon = p.val < 5.5 ? '&#128308;' : p.val < 7.5 ? '&#128993;' : '&#128994;';
    html += '<div style="margin-bottom:10px;padding:8px 10px;background:rgba(251,191,36,0.04);border-radius:6px;border-left:3px solid '+col+';">'
      + '<div style="font-size:10px;font-weight:700;color:'+col+';margin-bottom:5px;">'+icon+' '+p.nama.toUpperCase()+' — '+p.val.toFixed(1)+'/10</div>';
    tips.forEach(function(t) {
      html += '<div style="display:flex;gap:6px;margin-bottom:3px;font-size:10.5px;color:#9ca3af;">'
        +'<span style="color:'+col+';flex-shrink:0;">&#8594;</span><span>'+t+'</span></div>';
    });
    html += '</div>';
  });

  list.innerHTML = html;
  panel.classList.add('show');
}
"""

# Cari fungsi updateAll atau akhir script untuk sisipkan
if 'generateNarasiL3' not in c:
    # Sisipkan sebelum function handlePrint
    target = 'function handlePrint()'
    if target in c:
        c = c.replace(target, NARASI_JS + '\n' + target)
        results.append('OK 5: fungsi narasi & rekomendasi L3 ditambahkan')
    else:
        c = c + '\n<script>' + NARASI_JS + '\n</script>'
        results.append('OK 5: fungsi ditambahkan di akhir')
else:
    results.append('SKIP 5: sudah ada')

# ══════════════════════════════════════════════════════
# FIX 6: Panggil generateNarasiL3 & generateRekoL3 dari updateAll
# ══════════════════════════════════════════════════════
import re

# Cari fungsi yang memanggil update di L3
# Biasanya ada fungsi update() yang memperbarui tampilan
update_pattern = r'(scores\.jump.*?scores\.agility.*?)(updateRadar|renderRadar|drawRadar)'
m = re.search(update_pattern, c, re.DOTALL)

# Cari pemanggilan scores update dan tambahkan narasi
if 'generateNarasiL3(' not in c:
    # Tambahkan setelah baris yang set rekomendasi_text
    old_reko = "document.getElementById('rekomendasi').classList.add('show')"
    if old_reko in c:
        # Cari konteks sekitar rekomendasi untuk ambil variabel
        new_call = """document.getElementById('rekomendasi').classList.add('show');
  // Panggil narasi dan rekomendasi baru
  var _pilarArr = [
    {nama:'jump',    val: scores.jump    || 0},
    {nama:'sprint',  val: scores.sprint  || 0},
    {nama:'throw',   val: scores.throw   || 0},
    {nama:'rsi',     val: scores.rsi     || 0},
    {nama:'agility', val: scores.agility || 0}
  ];
  var _total = parseFloat(document.getElementById('res_total').textContent) || 0;
  var _pred  = document.getElementById('res_badge').textContent.trim() || 'NOVICE';
  generateNarasiL3(_pilarArr, _total, _pred);
  generateRekoL3(_pilarArr);"""
        c = c.replace(old_reko, new_call)
        results.append('OK 6: generateNarasiL3 & generateRekoL3 dipanggil')
    else:
        results.append('SKIP 6: trigger tidak ditemukan')
else:
    results.append('SKIP 6: sudah ada')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print()
print('='*55)
print('  HASIL FIX L3 POWER')
print('='*55)
for r in results:
    print(' ', r)
print('='*55)
print('  FILE TERSIMPAN')
print()
print('  Jalankan: python manage.py runserver')
