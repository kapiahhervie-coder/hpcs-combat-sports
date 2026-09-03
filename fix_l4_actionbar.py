fpath = "boxing/templates/boxing/l4_speed_agility.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

if "hpcs-action-bar" in content:
    print("SKIP: sudah ada")
else:
    bar = """
<div id="hpcs-action-bar" class="no-print" style="position:fixed;bottom:0;left:0;right:0;background:#0f172a;padding:10px 20px;display:flex;gap:10px;justify-content:center;align-items:center;z-index:9999;border-top:2px solid #06b6d4;box-shadow:0 -4px 20px rgba(0,0,0,0.4)">
  <span style="color:#64748b;font-size:11px">L4 BOXING</span>
  <button onclick="hpcsDownloadPDF()" style="background:#06b6d4;color:#0f172a;border:none;padding:9px 20px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer">&#11015; Download PDF</button>
  <button onclick="hpcsKirimWA()" style="background:#25D366;color:#fff;border:none;padding:9px 20px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer">&#128172; Kirim WhatsApp</button>
  <button onclick="hpcsPrint()" style="background:transparent;color:#06b6d4;border:1px solid #06b6d4;padding:9px 20px;border-radius:8px;font-weight:700;font-size:12px;cursor:pointer">&#128424; Print</button>
</div>
<div class="no-print" style="height:56px"></div>
<script id="hpcs-action-script">
function getNamaAtlet(){var sel=document.querySelector('select[name="atlet_id"],#atlet_select');if(sel&&sel.selectedIndex>0)return sel.options[sel.selectedIndex].text;return 'Atlet';}
function hpcsPrint(){window.print();}
function hpcsDownloadPDF(){var bar=document.getElementById('hpcs-action-bar');var sp=bar?bar.nextElementSibling:null;if(bar)bar.style.display='none';if(sp)sp.style.display='none';window.print();setTimeout(function(){if(bar)bar.style.display='flex';if(sp)sp.style.display='block';},1500);}
function hpcsKirimWA(){var nama=getNamaAtlet();var meta=document.querySelector('meta[name="coach-hp"]');var noHp=meta?meta.content:'';var waNum=noHp.replace(/[^0-9]/g,'');if(waNum.startsWith('0'))waNum='62'+waNum.slice(1);else if(!waNum.startsWith('62')&&waNum.length>0)waNum='62'+waNum;var tgl=new Date().toLocaleDateString('id-ID',{day:'2-digit',month:'long',year:'numeric'});var pesan=encodeURIComponent('*LAPORAN AUDIT L4 - HPCS BOXING*\nAtlet: '+nama+'\nTanggal: '+tgl+'\nDikirim otomatis HPCS System');if(waNum.length>8){window.open('https://wa.me/'+waNum+'?text='+pesan,'_blank');}else{var n=prompt('Nomor WhatsApp tujuan:');if(!n)return;var num=n.replace(/[^0-9]/g,'');if(num.startsWith('0'))num='62'+num.slice(1);window.open('https://wa.me/'+num+'?text='+pesan,'_blank');}}
</script>"""

    content = content.replace("{% endblock %}", bar + "\n{% endblock %}", 1)

    if 'coach-hp' not in content:
        meta = '<meta name="coach-hp" content="{{ request.user.profil_pelatih.no_hp|default:\'\' }}">'
        content = content.replace("{% block content %}", "{% block content %}\n" + meta, 1)

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK: action bar L4 berhasil!")
