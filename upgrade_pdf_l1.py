import re

fpath = "boxing/templates/boxing/l1_correction.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

new_cetak = r"""function cetakAudit(id,nama,kategori,gender,berat,rotation,extension,stability,ankle,posture,breathing,totalScore,predikat,rekomendasi,tanggal){
  const warna={ELITE:'#10b981',READY:'#38bdf8',DEVELOPING:'#f59e0b',NOVICE:'#ef4444'}[predikat]||'#6b7280';
  const warnaLight={ELITE:'#d1fae5',READY:'#e0f2fe',DEVELOPING:'#fef3c7',NOVICE:'#fee2e2'}[predikat]||'#f3f4f6';
  const icon={ELITE:'? ELITE',READY:'? READY',DEVELOPING:'? DEVELOPING',NOVICE:'? NOVICE'}[predikat]||predikat;

  const pilar=[
    {n:'Rotation',   v:parseFloat(rotation)||0,   icon:'?'},
    {n:'Extension',  v:parseFloat(extension)||0,  icon:'?'},
    {n:'Stability',  v:parseFloat(stability)||0,  icon:'?'},
    {n:'Ankle Mob.', v:parseFloat(ankle)||0,       icon:'?'},
    {n:'Posture',    v:parseFloat(posture)||0,     icon:'?'},
    {n:'Breathing',  v:parseFloat(breathing)||0,  icon:'?'},
  ];

  // Hitung pilar terendah & tertinggi
  const sorted = [...pilar].sort((a,b)=>a.v-b.v);
  const terlemah = sorted[0];
  const terkuat  = sorted[sorted.length-1];

  const pilarHTML = pilar.map(p=>{
    const pct = Math.min(100,(p.v/10)*100).toFixed(0);
    const c = p.v>=8?'#10b981':p.v>=6?'#38bdf8':p.v>=4?'#f59e0b':'#ef4444';
    const bg = p.v>=8?'#d1fae5':p.v>=6?'#e0f2fe':p.v>=4?'#fef3c7':'#fee2e2';
    return `
    <div style="background:${bg};border:1.5px solid ${c};border-radius:10px;padding:12px 8px;text-align:center;min-width:80px">
      <div style="font-size:16px;margin-bottom:2px">${p.icon}</div>
      <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">${p.n}</div>
      <div style="font-size:26px;font-weight:900;color:${c};line-height:1">${p.v.toFixed(1)}</div>
      <div style="font-size:9px;color:#888;margin-top:2px">/10</div>
      <div style="height:4px;background:#e5e7eb;border-radius:2px;margin-top:6px;overflow:hidden">
        <div style="height:100%;width:${pct}%;background:${c};border-radius:2px;transition:width .3s"></div>
      </div>
    </div>`;
  }).join('');

  let rekoHTML='';
  pilar.forEach(p=>{
    const db=REKO_DB[p.n];
    if(!db||p.v===0)return;
    const tips=p.v<5.5?db.low:p.v<7.5?db.mid:db.high;
    const c=p.v<5.5?'#ef4444':p.v<7.5?'#f59e0b':'#10b981';
    const label=p.v<5.5?'PRIORITAS':(p.v<7.5?'PERLU PERHATIAN':'PERTAHANKAN');
    rekoHTML+=`
    <div style="margin-bottom:12px;border-radius:8px;overflow:hidden">
      <div style="background:${c};color:#fff;padding:6px 12px;font-size:10px;font-weight:700;letter-spacing:1px">
        ${p.n.toUpperCase()} — ${p.v.toFixed(1)}/10 &nbsp;|&nbsp; ${label}
      </div>
      <div style="background:#f9fafb;padding:8px 12px">
        ${tips.map(t=>`<div style="padding:4px 0;border-bottom:1px solid #f3f4f6;font-size:11px;color:#374151">? ${t}</div>`).join('')}
      </div>
    </div>`;
  });

  const overallPct = Math.min(100,(parseFloat(totalScore)/10)*100).toFixed(0);

  const html=`<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>Audit L1 — ${nama}</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#111;font-size:13px}
  @media print{body{padding:0}@page{margin:15mm 12mm;size:A4}}
</style>
</head><body>

<!-- HEADER -->
<div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);color:#fff;padding:20px 28px;display:flex;justify-content:space-between;align-items:center">
  <div>
    <div style="font-size:9px;letter-spacing:3px;color:#94a3b8;text-transform:uppercase;margin-bottom:4px">HIGH PERFORMANCE COACHING SYSTEM</div>
    <div style="font-size:22px;font-weight:900;letter-spacing:2px">HPCS <span style="color:#38bdf8">BOXING</span></div>
    <div style="font-size:11px;color:#cbd5e1;margin-top:2px">Audit Level 1 — Core Stability & Correction</div>
  </div>
  <div style="text-align:right">
    <div style="background:${warna};color:#fff;padding:6px 16px;border-radius:20px;font-size:13px;font-weight:800;letter-spacing:2px">${icon}</div>
    <div style="font-size:10px;color:#94a3b8;margin-top:6px">${tanggal}</div>
  </div>
</div>

<!-- IDENTITAS ATLET -->
<div style="padding:16px 28px;background:#f8fafc;border-bottom:1px solid #e2e8f0">
  <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#64748b;margin-bottom:10px">¦ Identitas Atlet</div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
    ${[['Nama Atlet',nama,'??'],['Kategori',kategori,'??'],['Gender',gender,'?'],['Berat Badan',berat+' kg','?'],['Cabang','Boxing ??','??'],['Level','L1 — Correction','??']].map(([l,v,ic])=>`
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px">
      <div style="font-size:9px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px">${ic} ${l}</div>
      <div style="font-size:15px;font-weight:700;color:#0f172a;margin-top:3px">${v}</div>
    </div>`).join('')}
  </div>
</div>

<!-- SKOR TOTAL -->
<div style="padding:16px 28px;display:flex;align-items:center;gap:24px;background:${warnaLight};border-bottom:2px solid ${warna}">
  <div style="text-align:center;min-width:100px">
    <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Total Skor</div>
    <div style="font-size:56px;font-weight:900;color:${warna};line-height:1">${parseFloat(totalScore).toFixed(1)}</div>
    <div style="font-size:10px;color:#888">/10.0</div>
  </div>
  <div style="flex:1">
    <div style="height:12px;background:#e5e7eb;border-radius:6px;overflow:hidden;margin-bottom:8px">
      <div style="height:100%;width:${overallPct}%;background:${warna};border-radius:6px"></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:10px;color:#888">
      <span>0</span><span style="color:${warna};font-weight:700">${overallPct}%</span><span>10</span>
    </div>
    <div style="margin-top:10px;display:flex;gap:8px">
      <div style="background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:6px 12px;font-size:10px">
        <span style="color:#888">Pilar Terkuat:</span> <strong style="color:#10b981">${terkuat.n} (${terkuat.v.toFixed(1)})</strong>
      </div>
      <div style="background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:6px 12px;font-size:10px">
        <span style="color:#888">Prioritas Perbaikan:</span> <strong style="color:#ef4444">${terlemah.n} (${terlemah.v.toFixed(1)})</strong>
      </div>
    </div>
  </div>
</div>

<!-- SKOR PILAR -->
<div style="padding:16px 28px">
  <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#64748b;margin-bottom:12px">¦ Skor Pilar Analysis</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap">${pilarHTML}</div>
</div>

<!-- REKOMENDASI -->
<div style="padding:0 28px 20px">
  <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#64748b;margin-bottom:12px">¦ Rekomendasi Program HPCS</div>
  ${rekoHTML||'<p style="font-size:12px;color:#888">Tidak ada rekomendasi khusus.</p>'}
</div>

<!-- FOOTER -->
<div style="background:#0f172a;color:#94a3b8;padding:12px 28px;display:flex;justify-content:space-between;align-items:center;font-size:10px;margin-top:8px">
  <div>HPCS Boxing — High Performance Coaching System</div>
  <div style="display:flex;gap:24px">
    <div>Tanggal: <strong style="color:#fff">${tanggal}</strong></div>
    <div>Dokumen ini dicetak otomatis oleh sistem HPCS</div>
  </div>
</div>

<!-- TANDA TANGAN -->
<div style="padding:16px 28px;display:flex;justify-content:flex-end">
  <div style="text-align:center;min-width:180px">
    <div style="border-top:1px solid #374151;padding-top:6px;margin-top:40px;font-size:10px;color:#555">
      Coach / Pelatih<br>
      <span style="font-size:9px;color:#94a3b8">(__________________________)</span>
    </div>
  </div>
</div>

</body></html>`;

  const win=window.open('','_blank','width=900,height=750');
  if(!win){alert('Izinkan pop-up di browser Anda.');return;}
  win.document.write(html);
  win.document.close();
  win.focus();
  win.onload=()=>{setTimeout(()=>{win.print();win.onafterprint=()=>win.close();},600);};
}"""

# Cari dan replace fungsi cetakAudit lama
pattern = r'function cetakAudit\(.*?\}\s*(?=function showToast|$)'
match = re.search(pattern, content, re.DOTALL)
if match:
    content = content[:match.start()] + new_cetak + '\n' + content[match.end():]
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK: fungsi cetakAudit berhasil diupgrade!")
else:
    print("ERROR: fungsi cetakAudit tidak ditemukan, cek pattern")
