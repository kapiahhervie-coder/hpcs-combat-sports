path = r'combat\templates\combat\l4_speed_agility.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

results = []

# ══════════════════════════════════════════════════════
# FIX 1: Hapus tombol Print duplikat di header
# ══════════════════════════════════════════════════════
old_print = '''      <button class="btn btn-ghost no-print" onclick="window.print()">
        <i class="bi bi-printer-fill"></i> Print
      </button>'''
if old_print in c:
    c = c.replace(old_print, '')
    results.append('OK 1: tombol Print header dihapus')
else:
    results.append('SKIP 1')

# ══════════════════════════════════════════════════════
# FIX 2: Tambah tombol Cetak PDF di tabel history
# ══════════════════════════════════════════════════════
old_hapus = '''              <a href="{% url 'combat:hapus_l4_audit' item.pk %}"
                 class="btn-del-sm"
                 onclick="return confirm('Hapus data {{ item.atlet_name }}?')">
                <i class="bi bi-trash"></i>
              </a>'''

new_hapus = '''              <a href="{% url 'combat:hapus_l4_audit' item.pk %}"
                 class="btn-del-sm"
                 onclick="return confirm('Hapus data {{ item.atlet_name }}?')">
                <i class="bi bi-trash"></i>
              </a>
              <button onclick="window.print()" title="Cetak PDF"
                style="background:transparent;border:1px solid rgba(6,182,212,0.4);
                       color:#06b6d4;margin-left:4px;border-radius:6px;
                       padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-printer-fill"></i>
              </button>'''

if old_hapus in c:
    c = c.replace(old_hapus, new_hapus)
    results.append('OK 2: tombol cetak PDF di tabel ditambahkan')
else:
    results.append('SKIP 2')

# ══════════════════════════════════════════════════════
# FIX 3: Tambah panel Narasi di bawah rekomendasi
# ══════════════════════════════════════════════════════
OLD_REKO = '''          <div class="rekomendasi" id="rekomendasi">
            <div class="rek-title">Analisis Speed & Metabolic:</div>
            <div id="rek_text" style="font-size:12.5px;"></div>
          </div>'''

NEW_REKO = '''          <!-- Profil Kondisi Atlet -->
          <div id="narasi_l4" style="display:none;margin-top:10px;text-align:left;">
            <div style="font-size:10px;font-weight:700;color:#06b6d4;letter-spacing:1px;margin-bottom:6px;">
              &#9889; PROFIL KONDISI ATLET
            </div>
            <div id="narasi_box_l4" style="
              background:rgba(6,182,212,0.05);
              border:1px solid rgba(6,182,212,0.2);
              border-radius:10px;padding:12px;
              font-size:11px;line-height:1.7;
              color:#9ca3af;max-height:300px;
              overflow-y:auto;text-align:left;">
            </div>
          </div>

          <div class="rekomendasi" id="rekomendasi">
            <div class="rek-title">&#128203; Rekomendasi Pelatih:</div>
            <div id="rek_text" style="font-size:11px;text-align:left;"></div>
          </div>'''

if OLD_REKO in c:
    c = c.replace(OLD_REKO, NEW_REKO)
    results.append('OK 3: panel narasi L4 ditambahkan')
else:
    results.append('SKIP 3')

# ══════════════════════════════════════════════════════
# FIX 4: Ganti logika rekomendasi + tambah narasi lengkap
# ══════════════════════════════════════════════════════
OLD_LOGIC = """  if (a >= 9.0) {
    badge.className = 'result-badge rb-elite'; badge.innerText = 'ELITE';
    rekT.innerHTML = '<b>Kapasitas Speed-Agility-Metabolik Tingkat Tinggi.</b> Atlet siap kompetisi penuh. Pertahankan Yo-Yo IR1 monitoring bulanan dan hex drill 2x/minggu.';
  } else if (a >= 7.0) {
    badge.className = 'result-badge rb-ready'; badge.innerText = 'READY';
    rekT.innerHTML = '<b>Kompeten.</b> Fokus interval training 3x/minggu untuk tingkatkan VO2 Max. Target hex jump < 10.5 detik dalam 6 minggu.';
  } else if (a >= 5.0) {
    badge.className = 'result-badge rb-developing'; badge.innerText = 'DEVELOPING';
    rekT.innerHTML = '<b>Dalam Pengembangan.</b> Prioritaskan aerobik base 4x/minggu. Hexagon drill setiap sesi latihan. Cek recovery CNS antara sesi.';
  } else {
    badge.className = 'result-badge rb-novice'; badge.innerText = 'NOVICE';
    rekT.innerHTML = '<b>Kapasitas Metabolik Lemah.</b> Kembali ke L3 dan perkuat fondasi power. Tambah volume aerobik base 6–8 minggu sebelum re-test.';
  }"""

NEW_LOGIC = """  // Predikat
  var pred = 'NOVICE';
  if (a >= 9.0)      { badge.className='result-badge rb-elite';      badge.innerText='ELITE';      pred='ELITE'; }
  else if (a >= 7.0) { badge.className='result-badge rb-ready';      badge.innerText='READY';      pred='READY'; }
  else if (a >= 5.0) { badge.className='result-badge rb-developing'; badge.innerText='DEVELOPING'; pred='DEVELOPING'; }
  else               { badge.className='result-badge rb-novice';     badge.innerText='NOVICE';     pred='NOVICE'; }

  // Pilar data
  var pilarL4 = [
    {nama:'Hex',   val: parseFloat(s[0])||0},
    {nama:'Punch', val: parseFloat(s[1])||0},
    {nama:'YoYo',  val: parseFloat(s[2])||0}
  ];
  var filledL4  = pilarL4.filter(function(p){return p.val>0;});
  var sortedL4  = filledL4.slice().sort(function(a,b){return a.val-b.val;});
  var lemahL4   = sortedL4.slice(0,2);
  var kuatL4    = filledL4.slice().sort(function(a,b){return b.val-a.val;}).slice(0,2);

  function wrnL4(v){return v>=9?'#06b6d4':v>=7?'#38bdf8':v>=5?'#f59e0b':'#f87171';}
  function lblL4(v){return v>=9?'sangat baik':v>=7?'baik':v>=5?'cukup':'perlu perhatian';}

  // Nama atlet
  var namaElL4 = document.querySelector('select option:checked') ||
                 document.getElementById('atlet_name');
  var namaL4 = namaElL4 ? (namaElL4.getAttribute('data-nama')||namaElL4.value||namaElL4.textContent||'Atlet').trim() : 'Atlet';
  if (!namaL4 || namaL4.includes('Pilih')) namaL4 = 'Atlet';

  // Risiko cedera
  var risikoL4 = [];
  var hexScore  = parseFloat(s[0])||0;
  var punchScore= parseFloat(s[1])||0;
  var yoyoScore = parseFloat(s[2])||0;
  if (hexScore < 5)  risikoL4.push('&#9888; Hex Jump rendah — risiko ankle sprain & kurang koordinasi kaki');
  if (punchScore < 5) risikoL4.push('&#9888; Punch frequency rendah — risiko kelelahan otot lengan prematur saat tanding');
  if (yoyoScore < 5) risikoL4.push('&#9888; VO2 Max rendah — risiko kelelahan kardio dan penurunan performa di ronde akhir');
  if (risikoL4.length === 0) risikoL4.push('&#10003; Profil risiko RENDAH — kapasitas speed-agility-metabolik seimbang');

  var risikoHTMLL4 = risikoL4.map(function(r){
    return '<div style="margin-bottom:4px;font-size:10.5px;color:'+(r.includes('&#9888;')?'#f87171':'#10b981')+';">'+r+'</div>';
  }).join('');

  // Layak kompetisi?
  var layakKomp = a >= 9.0;
  var layakStr4 = layakKomp
    ? '<span style="color:#06b6d4;font-weight:700">&#127942; ELITE — Atlet SIAP KOMPETISI PENUH</span>'
    : a >= 7.0
    ? '<span style="color:#38bdf8;font-weight:700">&#9989; KOMPETEN — Latihan intensif 6 minggu untuk siap kompetisi</span>'
    : '<span style="color:#f87171;font-weight:700">&#9940; BELUM SIAP KOMPETISI — Perkuat L4 minimal 8 minggu lagi</span>';

  var kPredL4 = {
    ELITE:      'menunjukkan kapasitas speed-agility-metabolik <strong style="color:#06b6d4">ELIT</strong> — siap kompetisi penuh.',
    READY:      'berada di level <strong style="color:#38bdf8">KOMPETEN</strong> — tinggal optimasi detail untuk kompetisi.',
    DEVELOPING: 'sedang <strong style="color:#f59e0b">BERKEMBANG</strong> — kapasitas aerobik perlu ditingkatkan.',
    NOVICE:     'di level <strong style="color:#f87171">PEMULA</strong> — perlu kembali ke L3 Power 6-8 minggu.'
  };

  var narL4 = document.getElementById('narasi_l4');
  var narBoxL4 = document.getElementById('narasi_box_l4');
  if (narL4 && narBoxL4 && filledL4.length > 0) {
    narBoxL4.innerHTML = ''
      +'<div style="margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid rgba(6,182,212,0.1);">'
      +'<span style="color:#06b6d4;font-weight:700;font-size:12px;">&#9889; '+namaL4+'</span> '+(kPredL4[pred]||'')
      +' Total: <strong style="color:'+wrnL4(a)+'">'+a+'/10</strong></div>'
      +'<div style="margin-bottom:8px;"><div style="color:#6b7280;font-size:9px;letter-spacing:1px;margin-bottom:4px;">&#9650; KEUNGGULAN</div>'
      +kuatL4.map(function(p){return '<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;"><div style="width:5px;height:5px;border-radius:50%;background:#06b6d4;"></div><span><strong style="color:#06b6d4">'+p.nama+'</strong> — '+lblL4(p.val)+' <span style="color:'+wrnL4(p.val)+';font-weight:700">('+p.val.toFixed(1)+')</span></span></div>';}).join('')+'</div>'
      +'<div style="margin-bottom:8px;"><div style="color:#6b7280;font-size:9px;letter-spacing:1px;margin-bottom:4px;">&#9660; AREA KELEMAHAN</div>'
      +lemahL4.map(function(p){return '<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;"><div style="width:5px;height:5px;border-radius:50%;background:'+wrnL4(p.val)+';"></div><span><strong style="color:'+wrnL4(p.val)+'">'+p.nama+'</strong> — '+lblL4(p.val)+' <span style="color:'+wrnL4(p.val)+';font-weight:700">('+p.val.toFixed(1)+')</span></span></div>';}).join('')+'</div>'
      +'<div style="margin-bottom:8px;"><div style="color:#6b7280;font-size:9px;letter-spacing:1px;margin-bottom:4px;">&#9888; ANALISIS RISIKO</div>'+risikoHTMLL4+'</div>'
      +'<div style="padding:8px 10px;border-radius:8px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);">'
      +'<div style="color:#6b7280;font-size:9px;letter-spacing:1px;margin-bottom:4px;">&#128203; STATUS KOMPETISI</div>'
      +layakStr4+'<br><span style="color:#9ca3af;font-size:10px;">'
      +(layakKomp?'Pertahankan volume latihan dan monitoring VO2 Max bulanan.':a>=7?'Fokus tingkatkan '+( lemahL4[0]?lemahL4[0].nama:'-')+' dengan program interval 3x/minggu.':'Kembali ke L3 Power, bangun fondasi sebelum re-test L4.')
      +'</span></div>';
    narL4.style.display = 'block';
  }

  // Rekomendasi latihan lengkap
  var REKO_L4 = {
    Hex:   {low:['Hexagon Drill 3x3 putaran — fokus teknik footwork','Ladder Drill 2-in 2-out 3x panjang','4-Corner Cone Drill 3x untuk koordinasi','Kembali ke L3 Agility drill dasar'],mid:['Hex Jump 4x3 putaran dengan target < 11 dtk','Reactive Hex dengan visual cue 3x3','Mini Hurdle Hop 3x6 untuk foot speed'],high:['Kompetitif Hex: 5x3 putaran dengan interval pendek','Sport-specific footwork boxing 3x1 menit']},
    Punch: {low:['Shadow Boxing 3x1 menit fokus frekuensi','Speed Bag 3x2 menit untuk ritme tangan','Jab Combination Drill 4x30 detik','Double End Bag 3x1 menit'],mid:['10-Second Punch Burst 5x dengan istirahat','Combination Speed Drill 4x45 detik','Reactive Pad Work 3x2 menit'],high:['Competition Pace Pad Work 4x3 menit','Pertahankan dengan Speed Bag 3x/minggu']},
    YoYo:  {low:['Lari Aerobik 30 menit 3x/minggu di 65% HRmax','Walk-Jog Interval 20 menit untuk base aerobik','Kembali ke L3 dan tingkatkan VO2 Max base','Renang atau Sepeda 30 menit 3x/minggu'],mid:['Yo-Yo Interval Training Level 1 2x/minggu','HIIT 20 menit: 1 menit kerja, 1 menit rest','Fartlek Run 30 menit 2x/minggu'],high:['Yo-Yo IR1 monitoring bulanan','Supramaksimal Interval 3x/minggu','Sport-specific conditioning: round-based training']}
  };

  var rekoHTML4 = '<div style="font-size:10px;font-weight:700;color:#06b6d4;margin-bottom:8px;letter-spacing:1px;">PROGRAM REKOMENDASI PELATIH</div>';
  sortedL4.slice(0,3).forEach(function(p){
    var db = REKO_L4[p.nama];
    if (!db) return;
    var tips = p.val<5.5?db.low:p.val<7.5?db.mid:db.high;
    var col  = p.val<5.5?'#f87171':p.val<7.5?'#f59e0b':'#06b6d4';
    rekoHTML4 += '<div style="margin-bottom:8px;padding:7px 10px;background:rgba(6,182,212,0.04);border-radius:6px;border-left:3px solid '+col+';">'
      +'<div style="font-size:10px;font-weight:700;color:'+col+';margin-bottom:4px;">'+(p.val<5.5?'&#128308;':p.val<7.5?'&#128993;':'&#128994;')+' '+p.nama.toUpperCase()+' — '+p.val.toFixed(1)+'/10</div>';
    tips.forEach(function(t){
      rekoHTML4 += '<div style="display:flex;gap:5px;margin-bottom:2px;font-size:10px;color:#9ca3af;"><span style="color:'+col+';flex-shrink:0;">&#8594;</span><span>'+t+'</span></div>';
    });
    rekoHTML4 += '</div>';
  });
  rekT.innerHTML = rekoHTML4;"""

if OLD_LOGIC in c:
    c = c.replace(OLD_LOGIC, NEW_LOGIC)
    results.append('OK 4: logika narasi & rekomendasi L4 lengkap')
else:
    results.append('SKIP 4: logika lama tidak ditemukan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print()
print('='*55)
print('  HASIL FIX L4 COMPLETE')
print('='*55)
for r in results:
    print(' ', r)
print('='*55)
print('  FILE TERSIMPAN')
print()
print('  Jalankan: python manage.py runserver')
