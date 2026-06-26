path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

REKO_JS = """
var REKO_L2 = {
  Lower:{
    low:[
      'Goblet Squat 4x8 dengan beban 40-50% BW — fokus teknik',
      'Box Squat 3x10 untuk membangun pola gerak dasar',
      'Romanian Deadlift 3x12 untuk posterior chain',
      'Leg Press 4x12 sebagai alternatif beban terkontrol'
    ],
    mid:[
      'Goblet Squat progresif: tambah 2.5kg tiap minggu',
      'Pause Squat 3x6 untuk membangun kekuatan bottom position',
      'Single Leg Squat (Bulgarian Split Squat) 3x8 tiap sisi'
    ],
    high:[
      'Pertahankan volume: Goblet Squat 4x5 dengan beban maksimal',
      'Tambahkan Tempo Squat (3-1-1) untuk hipertrofi',
      'Variasi: Front Squat untuk keseimbangan quad-posterior'
    ]
  },
  Push:{
    low:[
      'Push Up progresif: mulai dari incline, lanjut flat 3x10',
      'Dumbbell Floor Press 4x12 dengan beban ringan',
      'Wall Push Up ke Standard Push Up — 4 minggu program',
      'Band-Assisted Bench Press untuk pola gerak benar'
    ],
    mid:[
      'Floor Press 4x8 dengan beban 70% maks',
      'Push Up variasi: Diamond, Wide, Archer 3x8',
      'Dumbbell Bench Press 3x10 unilateral untuk keseimbangan'
    ],
    high:[
      'Pertahankan dengan Volume Push: 4x12 bodyweight',
      'Tambah Plyometric Push Up untuk power komponen',
      'Medicine Ball Chest Pass 3x8 untuk explosive push'
    ]
  },
  Pull:{
    low:[
      'Inverted Row (TRX/bar rendah) 4x10 sebagai dasar',
      'Band-Assisted Pull Up 3x8 — kurangi band tiap 2 minggu',
      'Lat Pulldown 4x12 untuk membangun kekuatan lats',
      'Dumbbell Row 3x12 tiap sisi untuk upper back'
    ],
    mid:[
      'Pull Up 4x6 dengan full ROM',
      'Weighted Pull Up: tambah 2.5kg vest tiap 2 minggu',
      'Chin Up superset dengan Row 3x8 tiap gerakan'
    ],
    high:[
      'Weighted Pull Up 4x5 dengan beban tambahan',
      'L-Sit Pull Up 3x5 untuk core integration',
      'Muscle Up progression untuk athletic peak performance'
    ]
  },
  Core:{
    low:[
      'Dead Bug 3x10 tiap sisi — anti-extension dasar',
      'Plank progressi: 3x20 detik, tambah 5 dtk/minggu',
      'Bird Dog 3x12 untuk lumbar stability',
      'Hollow Body Hold 3x20 detik untuk bracing pattern'
    ],
    mid:[
      'Weighted Plank 3x30 detik dengan plate 5kg di punggung',
      'Ab Wheel Rollout 3x8 untuk anti-extension lanjut',
      'Pallof Press 3x12 tiap sisi untuk anti-rotation'
    ],
    high:[
      'Weighted Plank 3x60 detik — tambah beban tiap minggu',
      'Dragon Flag progression 3x5',
      'Barbell Rollout 3x8 untuk peak core strength'
    ]
  },
  Iso:{
    low:[
      'Split Squat Hold 3x20 detik tiap sisi — tanpa beban',
      'Wall Sit 3x30 detik untuk membangun durasi isometrik',
      'Isometric Lunge Hold 3x20 detik — fokus postur tegak',
      'Quad Set 3x30 detik untuk aktivasi awal'
    ],
    mid:[
      'Spanish Squat Hold 3x40 detik dengan band',
      'Single Leg Wall Sit 3x30 detik tiap sisi',
      'Split Squat dengan beban ringan 3x40 detik'
    ],
    high:[
      'Weighted Split Squat Hold 3x60 detik dengan dumbbell',
      'Bulgarian Split Squat Isometric 3x45 detik tiap sisi',
      'Pertahankan CNS Tremor Ratio > 65% sebagai standar'
    ]
  }
};

function generateRekoL2(pilars) {
  var panel = document.getElementById('reko_panel');
  var list  = document.getElementById('reko_list');
  var filled = pilars.filter(function(p){ return p.val > 0; });
  if (!filled.length) { panel.style.display='none'; return; }

  var sorted  = filled.slice().sort(function(a,b){ return a.val-b.val; });
  var weakest = sorted.slice(0,3);
  var html = '';

  weakest.forEach(function(p) {
    var db = REKO_L2[p.nama];
    if (!db) return;
    var tips = p.val < 5.5 ? db.low : p.val < 7.5 ? db.mid : db.high;
    var icon = p.val < 5.5 ? '&#128308;' : p.val < 7.5 ? '&#128993;' : '&#128994;';
    var col  = p.val < 5.5 ? '#f87171' : p.val < 7.5 ? '#f59e0b' : '#10b981';
    html += '<div style="margin-bottom:10px;padding:10px;background:rgba(16,185,129,0.04);border-radius:8px;border-left:3px solid '+col+';">'
      + '<div style="font-size:10px;font-weight:700;color:'+col+';letter-spacing:1px;margin-bottom:6px;">'
      + icon+' '+p.nama.toUpperCase()+' &mdash; '+p.val.toFixed(1)+'/10</div>';
    tips.forEach(function(t) {
      html += '<div style="display:flex;align-items:flex-start;gap:6px;margin-bottom:4px;font-size:10.5px;color:#9ca3af;">'
        +'<span style="color:'+col+';flex-shrink:0;margin-top:1px;">&#8594;</span><span>'+t+'</span></div>';
    });
    html += '</div>';
  });

  list.innerHTML = html;
  panel.style.display = 'block';
}
"""

# Tambah sebelum closing script tag atau sebelum window.addEventListener
if 'REKO_L2' not in c:
    if 'window.addEventListener' in c:
        c = c.replace('window.addEventListener', REKO_JS + '\nwindow.addEventListener')
    else:
        c = c.replace('</script>\n{% endblock %}', REKO_JS + '\n</script>\n{% endblock %}')
    print('OK 1: database rekomendasi L2 ditambahkan')
else:
    print('SKIP 1: sudah ada')

# Tambah panggilan generateRekoL2 di dalam liveUpdate
old_live = 'updateRadar(scores);\n    generateNarasiL2(scores, total, pred);'
new_live = 'updateRadar(scores);\n    generateNarasiL2(scores, total, pred);\n    generateRekoL2([{nama:"Lower",val:scores[0]},{nama:"Push",val:scores[1]},{nama:"Pull",val:scores[2]},{nama:"Core",val:scores[3]},{nama:"Iso",val:scores[4]}]);'

if old_live in c:
    c = c.replace(old_live, new_live)
    print('OK 2: generateRekoL2 dipanggil di liveUpdate')
else:
    print('SKIP 2: cari manual')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
