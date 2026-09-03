fpath = "boxing/templates/boxing/l3_power.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

old_btn = """              <button onclick="window.print()" title="Cetak PDF"
                style="background:transparent;border:1px solid rgba(245,158,11,0.4);
                       color:#f59e0b;margin-left:4px;border-radius:6px;
                       padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-printer-fill"></i>
              </button>"""

new_btn = """              <button onclick="cetakL3Row('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}','{{ item.atlet.gender|default:item.gender }}','{{ item.timestamp|date:\"d/m/Y H:i\" }}',{{ item.score_jump }},{{ item.score_sprint }},{{ item.score_throw }},{{ item.score_rsi }},{{ item.score_agility }},{{ item.total_skor }},'{{ item.predikat }}')" title="Cetak PDF"
                style="background:transparent;border:1px solid rgba(245,158,11,0.4);color:#f59e0b;margin-left:4px;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-printer-fill"></i>
              </button>
              <button onclick="kirimWARow('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}',{{ item.total_skor }},'{{ item.predikat }}','{{ item.timestamp|date:\"d/m/Y H:i\" }}')" title="Kirim WhatsApp"
                style="background:transparent;border:1px solid rgba(37,211,102,0.4);color:#25D366;margin-left:4px;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-whatsapp"></i>
              </button>"""

if old_btn in content:
    content = content.replace(old_btn, new_btn)
    print("OK: tombol WA ditambahkan ke setiap baris!")
else:
    print("WARN: pattern tidak ditemukan")

# Tambah fungsi JS cetakL3Row dan kirimWARow sebelum </script> terakhir
wa_functions = """
function cetakL3Row(nama,kat,gender,tgl,jump,sprint,throwv,rsi,agility,total,predikat){
  const warna={ELITE:'#10b981',READY:'#38bdf8',DEVELOPING:'#f59e0b',NOVICE:'#ef4444'}[predikat]||'#6b7280';
  const pilar=[
    {n:'Jump',v:parseFloat(jump)||0},
    {n:'Sprint',v:parseFloat(sprint)||0},
    {n:'Throw',v:parseFloat(throwv)||0},
    {n:'RSI',v:parseFloat(rsi)||0},
    {n:'Agility',v:parseFloat(agility)||0},
  ];
  const pilarHTML=pilar.map(p=>{
    const pct=Math.min(100,(p.v/10)*100).toFixed(0);
    const c=p.v>=8?'#10b981':p.v>=6?'#38bdf8':p.v>=4?'#f59e0b':'#ef4444';
    return '<div style="flex:1;min-width:80px;text-align:center;background:#f8fafc;border:1.5px solid '+c+';border-radius:10px;padding:10px 6px">'+
      '<div style="font-size:9px;color:#555;text-transform:uppercase">'+p.n+'</div>'+
      '<div style="font-size:24px;font-weight:900;color:'+c+'">'+p.v.toFixed(1)+'</div>'+
      '<div style="height:4px;background:#e5e7eb;border-radius:2px;margin-top:4px;overflow:hidden">'+
      '<div style="height:100%;width:'+pct+'%;background:'+c+';border-radius:2px"></div></div></div>';
  }).join('');
  const html='<!DOCTYPE html><html><head><meta charset="UTF-8"><title>L3 '+nama+'</title>'+
    '<style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:Segoe UI,sans-serif;background:#fff;color:#111;font-size:13px}'+
    '@media print{@page{margin:15mm 12mm;size:A4}}</style></head><body>'+
    '<div style="background:linear-gradient(135deg,#0f172a,#1a2e1a);color:#fff;padding:20px 28px;display:flex;justify-content:space-between;align-items:center">'+
    '<div><div style="font-size:9px;letter-spacing:3px;color:#94a3b8;text-transform:uppercase">HIGH PERFORMANCE COACHING SYSTEM</div>'+
    '<div style="font-size:22px;font-weight:900;letter-spacing:2px">HPCS <span style="color:#f59e0b">BOXING</span></div>'+
    '<div style="font-size:11px;color:#cbd5e1">Audit Level 3 — Explosive Power</div></div>'+
    '<div style="background:'+warna+';color:#fff;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:800">'+predikat+'</div></div>'+
    '<div style="padding:14px 28px;background:#f8fafc;border-bottom:1px solid #e2e8f0">'+
    '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">'+
    '[["Nama Atlet",nama],["Kategori",kat],["Gender",gender],["Tanggal",tgl],["Cabang","Boxing"],["Level","L3 - Power"]].map(function(x){'+
    'return "<div style=\'background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px\'>"+'+
    '"<div style=\'font-size:9px;color:#94a3b8;text-transform:uppercase\'>"+x[0]+"</div>"+'+
    '"<div style=\'font-size:14px;font-weight:700;color:#0f172a;margin-top:2px\'>"+x[1]+"</div></div>";}).join("")'+
    '</div></div>'+
    '<div style="padding:14px 28px;display:flex;align-items:center;gap:20px;background:#fef3c7;border-bottom:2px solid '+warna+'">'+
    '<div style="text-align:center;min-width:90px"><div style="font-size:9px;color:#555;text-transform:uppercase">Total Skor</div>'+
    '<div style="font-size:52px;font-weight:900;color:'+warna+'">'+parseFloat(total).toFixed(1)+'</div></div>'+
    '<div style="flex:1"><div style="height:10px;background:#e5e7eb;border-radius:5px;overflow:hidden">'+
    '<div style="height:100%;width:'+Math.min(100,(parseFloat(total)/10)*100).toFixed(0)+'%;background:'+warna+';border-radius:5px"></div></div></div></div>'+
    '<div style="padding:14px 28px"><div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#64748b;margin-bottom:10px">Skor Pilar Power</div>'+
    '<div style="display:flex;gap:8px;flex-wrap:wrap">'+pilarHTML+'</div></div>'+
    '<div style="background:#0f172a;color:#94a3b8;padding:10px 28px;display:flex;justify-content:space-between;font-size:10px;margin-top:8px">'+
    '<div>HPCS Boxing — High Performance Coaching System</div><div>'+tgl+'</div></div>'+
    '<div style="padding:14px 28px;display:flex;justify-content:flex-end">'+
    '<div style="text-align:center;min-width:180px"><div style="border-top:1px solid #374151;padding-top:6px;margin-top:40px;font-size:10px;color:#555">Coach / Pelatih<br><span style="font-size:9px;color:#94a3b8">(__________________________)</span></div></div></div>'+
    '</body></html>';
  const win=window.open('','_blank','width=960,height=800');
  if(!win){alert('Izinkan pop-up.');return;}
  win.document.write(html);win.document.close();win.focus();
  win.onload=function(){setTimeout(function(){win.print();win.onafterprint=function(){win.close();};},600);};
}

function kirimWARow(nama,kat,total,predikat,tgl){
  const meta=document.querySelector('meta[name="coach-hp"]');
  const noHp=meta?meta.content:'';
  let waNum=noHp.replace(/[^0-9]/g,'');
  if(waNum.startsWith('0'))waNum='62'+waNum.slice(1);
  else if(!waNum.startsWith('62')&&waNum.length>0)waNum='62'+waNum;
  const pesan=encodeURIComponent(
    '*LAPORAN AUDIT L3 - HPCS BOXING*\\n'+
    '━━━━━━━━━━━━━━━━━━━━\\n'+
    '👤 Atlet: '+nama+'\\n'+
    '🏷 Kategori: '+kat+'\\n'+
    '📅 Tanggal: '+tgl+'\\n'+
    '━━━━━━━━━━━━━━━━━━━━\\n'+
    '📊 Total Skor: *'+parseFloat(total).toFixed(1)+'/10*\\n'+
    '🏆 Predikat: *'+predikat+'*\\n'+
    '━━━━━━━━━━━━━━━━━━━━\\n'+
    '_Dikirim otomatis oleh HPCS Boxing System_'
  );
  if(waNum.length>8){
    window.open('https://wa.me/'+waNum+'?text='+pesan,'_blank');
  } else {
    const n=prompt('Nomor WhatsApp tujuan (contoh: 08123456789):');
    if(!n)return;
    let num=n.replace(/[^0-9]/g,'');
    if(num.startsWith('0'))num='62'+num.slice(1);
    window.open('https://wa.me/'+num+'?text='+pesan,'_blank');
  }
}
"""

# Inject fungsi sebelum </script> terakhir di area endblock
if "cetakL3Row" not in content:
    content = content.replace("{% endblock %}", "<script>" + wa_functions + "</script>\n{% endblock %}", 1)
    print("OK: fungsi cetakL3Row dan kirimWARow ditambahkan!")

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)
print("File tersimpan!")
