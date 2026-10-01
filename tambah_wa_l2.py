"""
tambah_wa_l2.py
Nambahin tombol WhatsApp per-baris di history L2 Strength, di sebelah
tombol Cetak PDF yang udah ada. Nomor HP coach diambil dari meta tag
coach-hp yang udah ditambahkan sebelumnya (waktu floating bar dipasang).
"""

fpath = "boxing/templates/boxing/l2_strenght.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

# --- 1. Sisipkan tombol WA setelah tombol Cetak PDF -----------------
tombol_lama = '''<button class="btn btn-sm btn-outline-info py-0 px-2 ms-1" onclick="window.print()" title="Cetak PDF"><i class="bi bi-printer-fill"></i></button>'''

tombol_baru = tombol_lama + '''
                            <button class="btn btn-sm btn-outline-success py-0 px-2 ms-1" title="Kirim WhatsApp"
                                    onclick="kirimWARowL2('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}',{{ item.total_skor|default:0 }},'{{ item.predikat }}','{{ item.timestamp|date:"d/m/Y H:i" }}')">
                                <i class="bi bi-whatsapp"></i>
                            </button>'''

if tombol_lama in content:
    content = content.replace(tombol_lama, tombol_baru)
    print("OK: tombol WA berhasil disisipkan.")
else:
    print("SKIP: pola tombol Cetak PDF tidak ditemukan persis, cek manual.")

# --- 2. Sisipkan function JS kirimWARowL2() sebelum {% endblock %} --
anchor = '''});
</script>
{% endblock %}'''

js_baru = '''});

function kirimWARowL2(nama,kat,total,predikat,tgl){
  var meta=document.querySelector('meta[name="coach-hp"]');
  var noHp=meta?meta.content:'';
  var waNum=(noHp||"").replace(/[^0-9]/g,"");
  if(waNum.startsWith("0"))waNum="62"+waNum.slice(1);
  else if(!waNum.startsWith("62")&&waNum.length>0)waNum="62"+waNum;
  var pesan=encodeURIComponent(
    "*LAPORAN AUDIT L2 - HPCS BOXING*\\n"+
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

if anchor in content:
    content = content.replace(anchor, js_baru)
    print("OK: function kirimWARowL2() berhasil disisipkan.")
else:
    print("SKIP: anchor akhir script tidak ditemukan persis, cek manual.")

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)

print("\nSELESAI, tersimpan ke", fpath)
