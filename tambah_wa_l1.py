"""
tambah_wa_l1.py
Nambahin tombol WhatsApp per-baris di history L1 Correction, persis
di sebelah tombol Cetak PDF yang udah ada. Data (nama, kategori,
total skor, predikat, tanggal, no HP coach) dipakai ulang dari yang
udah ke-passing ke cetakAudit() -- gak perlu meta tag coach-hp
karena L1 udah passing noHpCoach langsung sebagai parameter per-baris.
"""

fpath = "boxing/templates/boxing/l1_correction.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

# --- 1. Sisipkan tombol WA setelah tombol Cetak PDF -----------------
tombol_lama = '''<button type="button" class="btn btn-sm btn-outline-info py-0 px-2 me-1" title="Cetak PDF"
                      onclick="cetakAudit({{ audit.id }},'{{ audit.atlet.nama_atlet|escapejs }}','{{ audit.kategori_usia }}','{{ audit.atlet.gender }}','{{ audit.atlet.kelas_berat }}',{{ audit.score_rotation|default:0 }},{{ audit.score_extension|default:0 }},{{ audit.score_stability|default:0 }},{{ audit.score_ankle|default:0 }},{{ audit.score_posture|default:0 }},{{ audit.score_breathing|default:0 }},{{ audit.total_skor|default:0 }},'{{ audit.predikat }}','{{ audit.rekomendasi|default:''|escapejs }}','{{ audit.timestamp|date:"d/m/Y H:i" }}','{{ audit.atlet.pelatih.profil_pelatih.no_hp|default:'' }}','{{ audit.atlet.pelatih.get_full_name|default:audit.atlet.pelatih.username|default:'' }}')">
                <i class="bi bi-printer-fill"></i>
              </button>'''

tombol_baru = tombol_lama + '''
              <button type="button" class="btn btn-sm btn-outline-success py-0 px-2 ms-1" title="Kirim WhatsApp"
                      onclick="kirimWARowL1('{{ audit.atlet.nama_atlet|escapejs }}','{{ audit.kategori_usia }}',{{ audit.total_skor|default:0 }},'{{ audit.predikat }}','{{ audit.timestamp|date:"d/m/Y H:i" }}','{{ audit.atlet.pelatih.profil_pelatih.no_hp|default:'' }}')">
                <i class="bi bi-whatsapp"></i>
              </button>'''

if tombol_lama in content:
    content = content.replace(tombol_lama, tombol_baru)
    print("OK: tombol WA berhasil disisipkan.")
else:
    print("SKIP: pola tombol Cetak PDF tidak ditemukan persis, cek manual.")

# --- 2. Sisipkan function JS kirimWARowL1() setelah cetakAudit() ----
anchor_js = "function cetakAudit(id,nama,kategori,gender,berat,rotation,extension,stability,ankle,posture,breathing,totalScore,predikat,rekomendasi,tanggal,noHpCoach,namaCoach){"

js_baru = '''function kirimWARowL1(nama,kat,total,predikat,tgl,noHpCoach){
  var waNum=(noHpCoach||"").replace(/[^0-9]/g,"");
  if(waNum.startsWith("0"))waNum="62"+waNum.slice(1);
  else if(!waNum.startsWith("62")&&waNum.length>0)waNum="62"+waNum;
  var pesan=encodeURIComponent(
    "*LAPORAN AUDIT L1 - HPCS BOXING*\\n"+
    "========================\\n"+
    "Atlet: "+nama+"\\n"+
    "Kategori: "+kat+"\\n"+
    "Tanggal: "+tgl+"\\n"+
    "========================\\n"+
    "Total Skor: "+parseFloat(total).toFixed(1)+"/10\\n"+
    "Predikat: "+predikat+"\\n"+
    "========================\\n"+
    "Dikirim otomatis oleh HPCS Boxing System"
  );
  if(waNum.length>8){
    window.open("https://wa.me/"+waNum+"?text="+pesan,"_blank");
  } else {
    var n=prompt("Nomor WhatsApp tujuan (contoh: 08123456789):");
    if(!n)return;
    var num=n.replace(/[^0-9]/g,"");
    if(num.startsWith("0"))num="62"+num.slice(1);
    window.open("https://wa.me/"+num+"?text="+pesan,"_blank");
  }
}

''' + anchor_js

if anchor_js in content:
    content = content.replace(anchor_js, js_baru)
    print("OK: function kirimWARowL1() berhasil disisipkan.")
else:
    print("SKIP: anchor function cetakAudit tidak ditemukan persis, cek manual.")

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)

print("\nSELESAI, tersimpan ke", fpath)
