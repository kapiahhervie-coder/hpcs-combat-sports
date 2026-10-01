"""
fix_l4_tambah_wa.py
1. Tambah meta tag coach-hp ke L4.
2. Restyle tombol Print jadi Bootstrap + tambah tombol WA baru
   (L4 belum punya WA sama sekali sebelumnya).
3. Tambah function JS kirimWARowL4().
"""

fpath = "boxing/templates/boxing/l4_speed_agility.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

# --- 1. Tambah meta tag coach-hp setelah {% block extra_css %} -----
anchor_meta = "{% block extra_css %}"
meta_baru = anchor_meta + '\n<meta name="coach-hp" content="{{ request.user.profil_pelatih.no_hp|default:\'\' }}">'

if anchor_meta in content and 'name="coach-hp"' not in content:
    content = content.replace(anchor_meta, meta_baru, 1)
    print("OK: meta tag coach-hp berhasil ditambahkan.")
else:
    print("SKIP: meta tag sudah ada atau anchor tidak ditemukan.")

# --- 2. Restyle tombol Print + tambah tombol WA baru ----------------
tombol_lama = '''<button onclick="window.print()" title="Cetak PDF"
                style="background:transparent;border:1px solid rgba(6,182,212,0.4);
                       color:#06b6d4;margin-left:4px;border-radius:6px;
                       padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-printer-fill"></i>
              </button>'''

tombol_baru = '''<button class="btn btn-sm btn-outline-info py-0 px-2 ms-1" onclick="window.print()" title="Cetak PDF">
                <i class="bi bi-printer-fill"></i>
              </button>
              <button class="btn btn-sm btn-outline-success py-0 px-2 ms-1" title="Kirim WhatsApp"
                      onclick="kirimWARowL4('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}',{{ item.total_skor|default:0 }},'{{ item.predikat }}','{{ item.timestamp|date:"d/m/Y H:i" }}')">
                <i class="bi bi-whatsapp"></i>
              </button>'''

if tombol_lama in content:
    content = content.replace(tombol_lama, tombol_baru)
    print("OK: tombol Print L4 di-restyle + tombol WA baru ditambahkan.")
else:
    print("SKIP: pola tombol lama tidak ditemukan persis, cek manual.")

# --- 3. Sisipkan function JS kirimWARowL4() sebelum {% endblock %} -
anchor_akhir = '''}
</script>
{% endblock %}'''

js_baru = '''}

function kirimWARowL4(nama,kat,total,predikat,tgl){
  var meta=document.querySelector('meta[name="coach-hp"]');
  var noHp=meta?meta.content:'';
  var waNum=(noHp||"").replace(/[^0-9]/g,"");
  if(waNum.startsWith("0"))waNum="62"+waNum.slice(1);
  else if(!waNum.startsWith("62")&&waNum.length>0)waNum="62"+waNum;
  var pesan=encodeURIComponent(
    "*LAPORAN AUDIT L4 - HPCS BOXING*\\n"+
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
</script>
{% endblock %}'''

if anchor_akhir in content:
    content = content.replace(anchor_akhir, js_baru)
    print("OK: function kirimWARowL4() berhasil disisipkan.")
else:
    print("SKIP: anchor akhir script tidak ditemukan persis, cek manual.")

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)

print("\nSELESAI, tersimpan ke", fpath)
