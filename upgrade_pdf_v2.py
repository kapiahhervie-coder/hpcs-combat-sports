fpath = "boxing/templates/boxing/l1_correction.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

# 1. Tambah no_hp ke pemanggilan cetakAudit di template
old_call = """onclick=\"cetakAudit({{ audit.id }},'{{ audit.atlet.nama_atlet|escapejs }}','{{ audit.kategori_usia }}','{{ audit.atlet.gender }}','{{ audit.atlet.kelas_berat }}',{{ audit.score_rotation|default:0 }},{{ audit.score_extension|default:0 }},{{ audit.score_stability|default:0 }},{{ audit.score_ankle|default:0 }},{{ audit.score_posture|default:0 }},{{ audit.score_breathing|default:0 }},{{ audit.total_skor|default:0 }},'{{ audit.predikat }}','{{ audit.rekomendasi|default:''|escapejs }}','{{ audit.timestamp|date:\"d/m/Y H:i\" }}')\""""

new_call = """onclick=\"cetakAudit({{ audit.id }},'{{ audit.atlet.nama_atlet|escapejs }}','{{ audit.kategori_usia }}','{{ audit.atlet.gender }}','{{ audit.atlet.kelas_berat }}',{{ audit.score_rotation|default:0 }},{{ audit.score_extension|default:0 }},{{ audit.score_stability|default:0 }},{{ audit.score_ankle|default:0 }},{{ audit.score_posture|default:0 }},{{ audit.score_breathing|default:0 }},{{ audit.total_skor|default:0 }},'{{ audit.predikat }}','{{ audit.rekomendasi|default:''|escapejs }}','{{ audit.timestamp|date:\"d/m/Y H:i\" }}','{{ audit.atlet.pelatih.profil_pelatih.no_hp|default:'' }}','{{ audit.atlet.pelatih.get_full_name|default:audit.atlet.pelatih.username|default:'' }}')\""""

if old_call in content:
    content = content.replace(old_call, new_call)
    print("OK: parameter no_hp ditambahkan ke cetakAudit call")
else:
    print("WARN: pattern call tidak ditemukan, skip step 1")

# 2. Update signature fungsi cetakAudit
old_sig = "function cetakAudit(id,nama,kategori,gender,berat,rotation,extension,stability,ankle,posture,breathing,totalScore,predikat,rekomendasi,tanggal){"
new_sig = "function cetakAudit(id,nama,kategori,gender,berat,rotation,extension,stability,ankle,posture,breathing,totalScore,predikat,rekomendasi,tanggal,noHpCoach,namaCoach){"

if old_sig in content:
    content = content.replace(old_sig, new_sig)
    print("OK: signature fungsi diupdate")
else:
    print("WARN: signature tidak ditemukan")

# 3. Ganti bagian window.open dan win.document.write dengan versi baru yang punya 3 tombol
old_open = """  const win=window.open('','_blank','width=900,height=750');
  if(!win){alert('Izinkan pop-up di browser Anda.');return;}
  win.document.write(html);
  win.document.close();
  win.focus();
  win.onload=()=>{setTimeout(()=>{win.print();win.onafterprint=()=>win.close();},600);};
}"""

new_open = """
  // Bersihkan nomor HP untuk WhatsApp (hanya angka, ganti 0 depan dengan 62)
  let waNumber = (noHpCoach||'').replace(/\\D/g,'');
  if(waNumber.startsWith('0')) waNumber = '62' + waNumber.slice(1);
  if(!waNumber.startsWith('62')) waNumber = '62' + waNumber;

  // Pesan WhatsApp ringkasan audit
  const skorLabel = parseFloat(totalScore)>=9?'ELITE':parseFloat(totalScore)>=7?'READY':parseFloat(totalScore)>=5?'DEVELOPING':'NOVICE';
  const pesanWA = encodeURIComponent(
    `*LAPORAN AUDIT L1 — HPCS BOXING*\\n` +
    `━━━━━━━━━━━━━━━━━━━━\\n` +
    `👤 *Atlet:* ${nama}\\n` +
    `🏷 *Kategori:* ${kategori} | ${gender}\\n` +
    `⚖ *Berat:* ${berat} kg\\n` +
    `📅 *Tanggal:* ${tanggal}\\n` +
    `━━━━━━━━━━━━━━━━━━━━\\n` +
    `📊 *HASIL AUDIT*\\n` +
    `Total Skor: *${parseFloat(totalScore).toFixed(1)}/10*\\n` +
    `Predikat: *${predikat}*\\n` +
    `━━━━━━━━━━━━━━━━━━━━\\n` +
    `📋 *SKOR PILAR*\\n` +
    `↺ Rotation: ${parseFloat(rotation).toFixed(1)}\\n` +
    `↕ Extension: ${parseFloat(extension).toFixed(1)}\\n` +
    `⬡ Stability: ${parseFloat(stability).toFixed(1)}\\n` +
    `⚡ Ankle Mob: ${parseFloat(ankle).toFixed(1)}\\n` +
    `▲ Posture: ${parseFloat(posture).toFixed(1)}\\n` +
    `◎ Breathing: ${parseFloat(breathing).toFixed(1)}\\n` +
    `━━━━━━━━━━━━━━━━━━━━\\n` +
    `_Dikirim otomatis oleh HPCS Boxing System_`
  );
  const waUrl = `https://wa.me/${waNumber}?text=${pesanWA}`;

  // Inject 3 tombol aksi ke dalam HTML sebelum </body>
  const actionBar = `
  <div id="action-bar" style="position:fixed;bottom:0;left:0;right:0;background:#0f172a;padding:12px 28px;display:flex;gap:12px;justify-content:center;align-items:center;z-index:999;border-top:2px solid #38bdf8">
    <button onclick="window.print()" style="background:#38bdf8;color:#0f172a;border:none;padding:10px 24px;border-radius:8px;font-weight:800;font-size:13px;cursor:pointer;display:flex;align-items:center;gap:8px">
      🖨️ Print / Simpan PDF
    </button>
    <button onclick="downloadPDF()" style="background:#10b981;color:#fff;border:none;padding:10px 24px;border-radius:8px;font-weight:800;font-size:13px;cursor:pointer;display:flex;align-items:center;gap:8px">
      ⬇️ Download PDF
    </button>
    ${waNumber.length>5?`<a href="${waUrl}" target="_blank" style="background:#25D366;color:#fff;border:none;padding:10px 24px;border-radius:8px;font-weight:800;font-size:13px;cursor:pointer;text-decoration:none;display:flex;align-items:center;gap:8px">
      💬 Kirim WhatsApp
    </a>`:'<span style="color:#6b7280;font-size:12px">WhatsApp: nomor HP coach belum diisi</span>'}
    <button onclick="window.close()" style="background:transparent;color:#94a3b8;border:1px solid #374151;padding:10px 20px;border-radius:8px;font-weight:600;font-size:13px;cursor:pointer">
      ✕ Tutup
    </button>
  </div>
  <div style="height:60px"></div>
  <script>
  function downloadPDF(){
    // Sembunyikan action bar saat print/save
    document.getElementById('action-bar').style.display='none';
    window.print();
    setTimeout(()=>document.getElementById('action-bar').style.display='flex',1000);
  }
  <\\/script>`;

  const htmlFinal = html.replace('</body></html>', actionBar + '</body></html>');

  const win=window.open('','_blank','width=960,height=800');
  if(!win){alert('Izinkan pop-up di browser Anda.');return;}
  win.document.write(htmlFinal);
  win.document.close();
  win.focus();
}"""

if old_open in content:
    content = content.replace(old_open, new_open)
    print("OK: tombol Download + WhatsApp berhasil ditambahkan!")
else:
    print("WARN: pattern window.open tidak ditemukan")
    # Debug
    idx = content.find("const win=window.open")
    print(f"Posisi window.open: {idx}")

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)
print("File tersimpan!")
