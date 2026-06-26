path = r'combat\templates\combat\l1_correction.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# ── 1. Tambah div panel narasi ────────────────────────────────
OLD_PANEL = '          <div id="reko_panel" class="mt-3 text-start" style="display:none">\n            <div class="card-title"><i class="bi bi-lightbulb-fill" style="color:var(--gold)"></i> Rekomendasi HPCS</div>\n            <div id="reko_list"></div>\n          </div>'
ADD_PANEL = '\n          <div id="narasi_panel" class="mt-3 text-start" style="display:none">\n            <div class="card-title"><i class="bi bi-person-lines-fill" style="color:var(--cyan)"></i> Profil Kondisi Atlet</div>\n            <div id="narasi_box" style="background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.2);border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.7;color:var(--text2);"></div>\n          </div>'

if OLD_PANEL in c:
    c = c.replace(OLD_PANEL, OLD_PANEL + ADD_PANEL)
    print('OK 1: panel narasi ditambahkan')
else:
    print('SKIP 1: reko_panel tidak ditemukan persis')

# ── 2. Panggil generateNarasi di liveUpdate ───────────────────
OLD_CALL = "generateReko([{nama:'Rotation',val:avgRot},{nama:'Extension',val:ext},{nama:'Stability',val:avgSta},{nama:'Posture',val:pos},{nama:'Breathing',val:brth}]);"
NEW_CALL = "generateReko([{nama:'Rotation',val:avgRot},{nama:'Extension',val:ext},{nama:'Stability',val:avgSta},{nama:'Posture',val:pos},{nama:'Breathing',val:brth}]);\n  generateNarasi([{nama:'Rotation',val:avgRot},{nama:'Extension',val:ext},{nama:'Stability',val:avgSta},{nama:'Posture',val:pos},{nama:'Breathing',val:brth}],total,pred);"

if OLD_CALL in c:
    c = c.replace(OLD_CALL, NEW_CALL)
    print('OK 2: generateNarasi dipanggil')
else:
    print('SKIP 2: generateReko call tidak ditemukan')

# ── 3. Tambah fungsi generateNarasi ──────────────────────────
if 'function generateNarasi' not in c:
    FUNC = """
function generateNarasi(pilars,total,pred){
  var panel=document.getElementById('narasi_panel');
  var box=document.getElementById('narasi_box');
  var filled=pilars.filter(function(p){return p.val>0;});
  if(!filled.length){panel.style.display='none';return;}
  var namaEl=document.querySelector('select option:checked');
  var namaAtlet=namaEl?namaEl.textContent.trim():'Atlet';
  function lbl(v){return v>=9?'sangat baik':v>=7.5?'baik':v>=5.5?'cukup':'perlu perhatian khusus';}
  function wrn(v){return v>=9?'var(--green)':v>=7.5?'var(--cyan)':v>=5.5?'var(--gold)':'var(--red)';}
  var sorted=[].concat(filled).sort(function(a,b){return b.val-a.val;});
  var kuat=sorted.slice(0,2);
  var lemah=sorted.slice(-2).reverse();
  var layak=total>=7.5;
  var kPred={
    ELITE:'menunjukkan kapasitas biomekanik <strong style="color:var(--green)">ELIT</strong> &mdash; seluruh pilar berada di level puncak.',
    READY:'berada di level <strong style="color:var(--cyan)">SIAP (READY)</strong> &mdash; fondasi solid dengan beberapa area yang bisa ditingkatkan.',
    DEVELOPING:'sedang <strong style="color:var(--gold)">BERKEMBANG</strong> &mdash; fondasi mulai terbentuk namun pilar kritis perlu koreksi.',
    NOVICE:'berada di level <strong style="color:var(--red)">PEMULA (NOVICE)</strong> &mdash; perlu membangun kapasitas dasar sebelum program beban.'
  };
  var layakStr=layak
    ?'<span style="color:var(--green);font-weight:700">&#9989; LAYAK mengikuti program Latihan Kekuatan (L2 Strength)</span>'
    :'<span style="color:var(--red);font-weight:700">&#9940; BELUM LAYAK ke L2 &mdash; perlu program korektif terlebih dahulu</span>';
  var kuatHTML=kuat.map(function(p){
    return '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
      +'<div style="width:6px;height:6px;border-radius:50%;background:var(--green);flex-shrink:0;"></div>'
      +'<span><strong style="color:var(--green)">'+p.nama+'</strong> &mdash; '+lbl(p.val)
      +' <span style="color:'+wrn(p.val)+';font-weight:700;">('+p.val.toFixed(1)+'/10)</span>'
      +(p.val>=7.5?' : aset performa bertarung.':' : menunjukkan perkembangan positif.')
      +'</span></div>';
  }).join('');
  var lemahHTML=lemah.map(function(p){
    return '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
      +'<div style="width:6px;height:6px;border-radius:50%;background:'+wrn(p.val)+';flex-shrink:0;"></div>'
      +'<span><strong style="color:'+wrn(p.val)+'">'+p.nama+'</strong> &mdash; '+lbl(p.val)
      +' <span style="color:'+wrn(p.val)+';font-weight:700;">('+p.val.toFixed(1)+'/10)</span>'
      +(p.val<5.5?' : prioritas utama program korektif.':' : perlu perhatian dalam program latihan.')
      +'</span></div>';
  }).join('');
  var fokus=layak
    ?'Fondasi biomekanik cukup kuat. Fokus perkuat <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> selama L2.'
    :'Jalankan korektif 4&#8211;6 minggu, fokus <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> dan <strong>'+(lemah[1]?lemah[1].nama:'-')+'</strong>.';
  box.innerHTML=''
    +'<div style="margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid rgba(0,210,255,0.1);">'
    +'<span style="color:var(--cyan);font-weight:700;font-size:12px;">&#128100; '+namaAtlet+'</span> '+(kPred[pred]||'')
    +' Total skor: <strong style="font-size:13px;color:'+wrn(total)+'">'+total.toFixed(1)+'/10</strong></div>'
    +'<div style="margin-bottom:10px;"><div style="color:var(--text3);font-size:10px;margin-bottom:5px;letter-spacing:1px;">&#9650; KEUNGGULAN</div>'+kuatHTML+'</div>'
    +'<div style="margin-bottom:10px;"><div style="color:var(--text3);font-size:10px;margin-bottom:5px;letter-spacing:1px;">&#9660; AREA KELEMAHAN</div>'+lemahHTML+'</div>'
    +'<div style="padding:10px 12px;border-radius:8px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);">'
    +'<div style="color:var(--text3);font-size:10px;margin-bottom:6px;letter-spacing:1px;">&#128203; KESIMPULAN</div>'
    +layakStr+'<br><span style="color:var(--text2);font-size:10.5px;">'+fokus+'</span></div>';
  panel.style.display='block';
}
"""
    c = c.replace('function handlePrint(){', FUNC + '\nfunction handlePrint(){')
    print('OK 3: fungsi generateNarasi ditambahkan')
else:
    print('OK 3: generateNarasi sudah ada')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE - FILE TERSIMPAN')
