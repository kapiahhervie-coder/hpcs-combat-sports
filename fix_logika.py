path = r'combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = """  var kuatHTML=kuat.map(function(p){
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
  }).join('');"""

new = """  var kuatHTML=kuat.map(function(p){
    return '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
      +'<div style="width:6px;height:6px;border-radius:50%;background:var(--green);flex-shrink:0;"></div>'
      +'<span><strong style="color:var(--green)">'+p.nama+'</strong> &mdash; '+lbl(p.val)
      +' <span style="color:'+wrn(p.val)+';font-weight:700;">('+p.val.toFixed(1)+'/10)</span>'
      +(p.val>=9?' : pilar unggulan, pertahankan.':p.val>=7.5?' : aset performa bertarung.':' : menunjukkan perkembangan positif.')
      +'</span></div>';
  }).join('');
  var minVal=Math.min.apply(null,filled.map(function(p){return p.val;}));
  var maxVal=Math.max.apply(null,filled.map(function(p){return p.val;}));
  var semuaPrima=(maxVal-minVal)<=0.5 && minVal>=8.5;
  var lemahHTML=semuaPrima
    ?'<div style="display:flex;align-items:center;gap:8px;padding:8px 10px;background:rgba(0,255,136,0.07);border-radius:6px;border:1px solid rgba(0,255,136,0.2);">'
      +'<span style="font-size:16px;">&#127942;</span>'
      +'<span style="color:var(--green);font-weight:600;">Semua pilar dalam kondisi prima &mdash; tidak ada kelemahan signifikan yang perlu dikoreksi.</span>'
      +'</div>'
    :lemah.map(function(p){
      var catatan=p.val<5.5?' : prioritas utama program korektif.':p.val<7.5?' : perlu perhatian dalam program latihan.':' : jaga konsistensi, masih bisa ditingkatkan.';
      return '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
        +'<div style="width:6px;height:6px;border-radius:50%;background:'+wrn(p.val)+';flex-shrink:0;"></div>'
        +'<span><strong style="color:'+wrn(p.val)+'">'+p.nama+'</strong> &mdash; '+lbl(p.val)
        +' <span style="color:'+wrn(p.val)+';font-weight:700;">('+p.val.toFixed(1)+'/10)</span>'
        +catatan+'</span></div>';
    }).join('');"""

if old in c:
    c = c.replace(old, new)
    print('OK: logika kelemahan diperbaiki')
else:
    print('SKIP: pattern tidak ditemukan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
