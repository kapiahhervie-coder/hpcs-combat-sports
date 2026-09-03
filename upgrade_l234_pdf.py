import re

# ══════════════════════════════════════════════
# TEMPLATE FLOATING ACTION BAR (sama untuk semua)
# ══════════════════════════════════════════════

def buat_action_bar(level, warna, cabang="BOXING"):
    return f"""
<!-- FLOATING ACTION BAR — ditambah otomatis oleh upgrade script -->
<div id="hpcs-action-bar" class="no-print" style="position:fixed;bottom:0;left:0;right:0;background:#0f172a;padding:10px 20px;display:flex;gap:10px;justify-content:center;align-items:center;z-index:9999;border-top:2px solid {warna};box-shadow:0 -4px 20px rgba(0,0,0,0.4)">
  <span style="color:#64748b;font-size:11px;margin-right:8px">📄 L{level} {cabang}</span>
  <button onclick="hpcsDownloadPDF()" style="background:{warna};color:#0f172a;border:none;padding:9px 20px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer">
    ⬇️ Download PDF
  </button>
  <button onclick="hpcsKirimWA()" style="background:#25D366;color:#fff;border:none;padding:9px 20px;border-radius:8px;font-weight:800;font-size:12px;cursor:pointer">
    💬 Kirim WhatsApp
  </button>
  <button onclick="hpcsPrint()" style="background:transparent;color:{warna};border:1px solid {warna};padding:9px 20px;border-radius:8px;font-weight:700;font-size:12px;cursor:pointer">
    🖨️ Print
  </button>
</div>
<div class="no-print" style="height:56px"></div>
"""

def buat_script_wa(level, pilar_list, warna):
    pilar_js = "\n".join([f"    `{p['icon']} {p['label']}: ${{getVal('{p['id']}')}}\\n` +" for p in pilar_list])
    return f"""
<script id="hpcs-action-script">
function getVal(id){{
  const el = document.getElementById(id);
  if(!el) return '-';
  return el.value || el.textContent || '-';
}}

function getNamaAtlet(){{
  // Coba berbagai selector untuk nama atlet
  const selectors = ['#nama_atlet_display','#atlet_nama','.atlet-nama','[data-atlet-nama]'];
  for(const s of selectors){{
    const el = document.querySelector(s);
    if(el && el.textContent.trim()) return el.textContent.trim();
  }}
  // Fallback: cari di select option yang terpilih
  const sel = document.querySelector('select[name="atlet_id"], #atlet_select');
  if(sel && sel.selectedIndex > 0) return sel.options[sel.selectedIndex].text;
  return 'Atlet';
}}

function getNoHpCoach(){{
  const meta = document.querySelector('meta[name="coach-hp"]');
  return meta ? meta.content : '';
}}

function hpcsPrint(){{
  // Gunakan handlePrint jika ada, fallback ke window.print
  if(typeof handlePrint === 'function') handlePrint();
  else window.print();
}}

function hpcsDownloadPDF(){{
  const bar = document.getElementById('hpcs-action-bar');
  const spacer = bar ? bar.nextElementSibling : null;
  if(bar) bar.style.display='none';
  if(spacer) spacer.style.display='none';
  
  if(typeof handlePrint === 'function') handlePrint();
  else window.print();
  
  setTimeout(()=>{{
    if(bar) bar.style.display='flex';
    if(spacer) spacer.style.display='block';
  }}, 1500);
}}

function hpcsKirimWA(){{
  const nama = getNamaAtlet();
  const noHp = getNoHpCoach();
  
  // Format nomor WA
  let waNum = noHp.replace(/\\D/g,'');
  if(waNum.startsWith('0')) waNum = '62' + waNum.slice(1);
  else if(!waNum.startsWith('62') && waNum.length > 0) waNum = '62' + waNum;
  
  const tgl = new Date().toLocaleDateString('id-ID',{{day:'2-digit',month:'long',year:'numeric'}});
  
  const pesan = encodeURIComponent(
    `*LAPORAN AUDIT L{level} — HPCS {cabang.upper() if isinstance(cabang, str) else "BOXING"}*\\n` +
    `━━━━━━━━━━━━━━━━━━━━\\n` +
    `👤 *Atlet:* ${{nama}}\\n` +
    `📅 *Tanggal:* ${{tgl}}\\n` +
    `━━━━━━━━━━━━━━━━━━━━\\n` +
    `_Laporan lengkap tersedia di sistem HPCS_\\n` +
    `_Dikirim otomatis oleh HPCS Boxing System_`
  );
  
  if(waNum.length > 8){{
    window.open(`https://wa.me/${{waNum}}?text=${{pesan}}`, '_blank');
  }} else {{
    // Tidak ada nomor — tanya manual
    const nomorInput = prompt('Masukkan nomor WhatsApp tujuan (contoh: 08123456789):');
    if(!nomorInput) return;
    let num = nomorInput.replace(/\\D/g,'');
    if(num.startsWith('0')) num = '62' + num.slice(1);
    window.open(`https://wa.me/${{num}}?text=${{pesan}}`, '_blank');
  }}
}}
</script>
"""

# ══════════════════════════════════════════════
# UPGRADE L2
# ══════════════════════════════════════════════
print("=== Upgrade L2 ===")
fpath2 = "boxing/templates/boxing/l2_strenght.html"
with open(fpath2, encoding="utf-8") as f:
    c2 = f.read()

if "hpcs-action-bar" not in c2:
    bar2 = buat_action_bar(2, "#60a5fa")
    script2 = buat_script_wa(2, [], "#60a5fa")
    # Tambah meta coach-hp setelah <head>
    c2 = c2.replace("<head>", '<head>\n<meta name="coach-hp" content="{{ request.user.profil_pelatih.no_hp|default:\'\' }}">', 1)
    # Inject sebelum </body>
    c2 = c2.replace("</body>", bar2 + script2 + "\n</body>", 1)
    with open(fpath2, "w", encoding="utf-8") as f:
        f.write(c2)
    print("OK: L2 diupgrade")
else:
    print("SKIP: L2 sudah punya action bar")

# ══════════════════════════════════════════════
# UPGRADE L3
# ══════════════════════════════════════════════
print("=== Upgrade L3 ===")
fpath3 = "boxing/templates/boxing/l3_power.html"
with open(fpath3, encoding="utf-8") as f:
    c3 = f.read()

if "hpcs-action-bar" not in c3:
    bar3 = buat_action_bar(3, "#f59e0b")
    script3 = buat_script_wa(3, [], "#f59e0b")
    c3 = c3.replace("<head>", '<head>\n<meta name="coach-hp" content="{{ request.user.profil_pelatih.no_hp|default:\'\' }}">', 1)
    c3 = c3.replace("</body>", bar3 + script3 + "\n</body>", 1)
    with open(fpath3, "w", encoding="utf-8") as f:
        f.write(c3)
    print("OK: L3 diupgrade")
else:
    print("SKIP: L3 sudah punya action bar")

# ══════════════════════════════════════════════
# UPGRADE L4
# ══════════════════════════════════════════════
print("=== Upgrade L4 ===")
fpath4 = "boxing/templates/boxing/l4_speed_agility.html"
with open(fpath4, encoding="utf-8") as f:
    c4 = f.read()

if "hpcs-action-bar" not in c4:
    bar4 = buat_action_bar(4, "#06b6d4")
    script4 = buat_script_wa(4, [], "#06b6d4")
    c4 = c4.replace("<head>", '<head>\n<meta name="coach-hp" content="{{ request.user.profil_pelatih.no_hp|default:\'\' }}">', 1)
    c4 = c4.replace("</body>", bar4 + script4 + "\n</body>", 1)
    with open(fpath4, "w", encoding="utf-8") as f:
        f.write(c4)
    print("OK: L4 diupgrade")
else:
    print("SKIP: L4 sudah punya action bar")

print("\nSelesai! Refresh browser untuk melihat perubahan.")
