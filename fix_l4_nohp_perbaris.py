"""
fix_l4_nohp_perbaris.py
Sama seperti L3 -- ganti sumber nomor HP di L4 dari meta tag jadi
data per-baris (atlet.pelatih.profil_pelatih.no_hp).
"""

fpath = "boxing/templates/boxing/l4_speed_agility.html"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

# --- 1. Tombol: tambah parameter noHpCoach ---------------------------
tombol_lama = '''<button class="btn btn-sm btn-outline-success py-0 px-2 ms-1" title="Kirim WhatsApp"
                      onclick="kirimWARowL4('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}',{{ item.total_skor|default:0 }},'{{ item.predikat }}','{{ item.timestamp|date:"d/m/Y H:i" }}')">'''

tombol_baru = '''<button class="btn btn-sm btn-outline-success py-0 px-2 ms-1" title="Kirim WhatsApp"
                      onclick="kirimWARowL4('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}',{{ item.total_skor|default:0 }},'{{ item.predikat }}','{{ item.timestamp|date:"d/m/Y H:i" }}','{{ item.atlet.pelatih.profil_pelatih.no_hp|default:'' }}')">'''

if tombol_lama in content:
    content = content.replace(tombol_lama, tombol_baru)
    print("OK: parameter noHpCoach ditambahkan ke tombol.")
else:
    print("SKIP: pola tombol tidak ditemukan persis, cek manual.")

# --- 2. Function: baca dari parameter, bukan meta tag ---------------
js_lama = '''function kirimWARowL4(nama,kat,total,predikat,tgl){
  var meta=document.querySelector('meta[name="coach-hp"]');
  var noHp=meta?meta.content:'';
  var waNum=(noHp||"").replace(/[^0-9]/g,"");'''

js_baru = '''function kirimWARowL4(nama,kat,total,predikat,tgl,noHpCoach){
  var noHp=noHpCoach||"";
  var waNum=noHp.replace(/[^0-9]/g,"");'''

if js_lama in content:
    content = content.replace(js_lama, js_baru)
    print("OK: function kirimWARowL4() sekarang baca dari parameter per-baris.")
else:
    print("SKIP: pola function tidak ditemukan persis, cek manual.")

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)

print("\nSELESAI, tersimpan ke", fpath)
