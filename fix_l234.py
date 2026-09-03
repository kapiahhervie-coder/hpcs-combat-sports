configs = [
    ("boxing/templates/boxing/l2_strenght.html", 2, "#60a5fa", "BOXING"),
    ("boxing/templates/boxing/l3_power.html", 3, "#f59e0b", "BOXING"),
    ("boxing/templates/boxing/l4_speed_agility.html", 4, "#06b6d4", "BOXING"),
]

for fpath, level, warna, cabang in configs:
    print(f"=== L{level} ===")
    with open(fpath, encoding="utf-8") as f:
        c = f.read()
    if "hpcs-action-bar" in c:
        print(f"SKIP"); continue

    meta = f'<meta name="coach-hp" content="{{{{ request.user.profil_pelatih.no_hp|default:\'\' }}}}">'
    if 'coach-hp' not in c:
        c = c.replace("<head>", f"<head>\n{meta}", 1)

    bar = f'''
<div id="hpcs-action-bar" class="no-print" style="position:fixed;bottom:0;left:0;right:0;background:#0f172a;padding:10px 20px;display:flex;gap:10px;justify-content:center;align-items:center;z-index:9999;border-top:2px solid {warna}">
  <span style="color:#64748b;font-size:11px">L{level} {cabang}</span>
  <button onclick="hpcsDownloadPDF()" style="background:{warna};color:#0f172a;border:none;padding:9px 20px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer">&#11015; Download PDF</button>
  <button onclick="hpcsKirimWA()" style="background:#25D366;color:#fff;border:none;padding:9px 20px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer">&#128172; Kirim WhatsApp</button>
  <button onclick="hpcsPrint()" style="background:transparent;color:{warna};border:1px solid {warna};padding:9px 20px;border-radius:8px;font-weight:700;font-size:12px;cursor:pointer">&#128424; Print</button>
</div>
<div class="no-print" style="height:56px"></div>'''

    script = f'''<script id="hpcs-action-script">
function getNamaAtlet(){{var sel=document.querySelector('select[name="atlet_id"],#atlet_select');if(sel&&sel.selectedIndex>0)return sel.options[sel.selectedIndex].text;return 'Atlet';}}
function hpcsPrint(){{if(typeof handlePrint==='function')handlePrint();else window.print();}}
function hpcsDownloadPDF(){{var bar=document.getElementById('hpcs-action-bar');var sp=bar?bar.nextElementSibling:null;if(bar)bar.style.display='none';if(sp)sp.style.display='none';if(typeof handlePrint==='function')handlePrint();else window.print();setTimeout(function(){{if(bar)bar.style.display='flex';if(sp)sp.style.display='block';}},1500);}}
function hpcsKirimWA(){{var nama=getNamaAtlet();var meta=document.querySelector('meta[name="coach-hp"]');var noHp=meta?meta.content:'';var waNum=noHp.replace(/\\D/g,'');if(waNum.startsWith('0'))waNum='62'+waNum.slice(1);else if(!waNum.startsWith('62')&&waNum.length>0)waNum='62'+waNum;var tgl=new Date().toLocaleDateString('id-ID',{{day:'2-digit',month:'long',year:'numeric'}});var pesan=encodeURIComponent('*LAPORAN AUDIT L{level} - HPCS {cabang}*\\n'+'Atlet: '+nama+'\\n'+'Tanggal: '+tgl+'\\n'+'Dikirim otomatis HPCS System');if(waNum.length>8){{window.open('https://wa.me/'+waNum+'?text='+pesan,'_blank');}}else{{var n=prompt('Nomor WhatsApp tujuan (contoh: 08123456789):');if(!n)return;var num=n.replace(/\\D/g,'');if(num.startsWith('0'))num='62'+num.slice(1);window.open('https://wa.me/'+num+'?text='+pesan,'_blank');}}}}
</script>'''

    c = c.replace("</body>", bar + "\n" + script + "\n</body>", 1)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(c)
    print(f"OK: L{level} diupgrade!")

print("Selesai!")