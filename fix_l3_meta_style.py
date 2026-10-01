"""
fix_l3_meta_style.py
1. Tambah meta tag coach-hp ke L3 (biar nomor HP coach auto-detect,
   gak selalu fallback ke prompt manual).
2. Restyle tombol Print + WA di history L3 dari inline-CSS jadi
   Bootstrap classes (samain sama L1/L2).
"""

fpath = "boxing/templates/boxing/l3_power.html"
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

# --- 2. Restyle tombol Print + WA jadi Bootstrap --------------------
tombol_lama = '''<button onclick="cetakL3Row('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}','{{ item.atlet.gender|default:item.gender }}','{{ item.timestamp|date:"d/m/Y H:i" }}',{{ item.score_jump }},{{ item.score_sprint }},{{ item.score_throw }},{{ item.score_rsi }},{{ item.score_agility }},{{ item.total_skor }},'{{ item.predikat }}')" title="Cetak PDF"
                style="background:transparent;border:1px solid rgba(245,158,11,0.4);color:#f59e0b;margin-left:4px;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-printer-fill"></i>
              </button>
              <button onclick="kirimWARow('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}',{{ item.total_skor }},'{{ item.predikat }}','{{ item.timestamp|date:"d/m/Y H:i" }}')" title="Kirim WhatsApp"
                style="background:transparent;border:1px solid rgba(37,211,102,0.4);color:#25D366;margin-left:4px;border-radius:6px;padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-whatsapp"></i>
              </button>'''

tombol_baru = '''<button class="btn btn-sm btn-outline-warning py-0 px-2 ms-1" onclick="cetakL3Row('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}','{{ item.atlet.gender|default:item.gender }}','{{ item.timestamp|date:"d/m/Y H:i" }}',{{ item.score_jump }},{{ item.score_sprint }},{{ item.score_throw }},{{ item.score_rsi }},{{ item.score_agility }},{{ item.total_skor }},'{{ item.predikat }}')" title="Cetak PDF">
                <i class="bi bi-printer-fill"></i>
              </button>
              <button class="btn btn-sm btn-outline-success py-0 px-2 ms-1" onclick="kirimWARow('{{ item.atlet_name|escapejs }}','{{ item.kategori_usia }}',{{ item.total_skor }},'{{ item.predikat }}','{{ item.timestamp|date:"d/m/Y H:i" }}')" title="Kirim WhatsApp">
                <i class="bi bi-whatsapp"></i>
              </button>'''

if tombol_lama in content:
    content = content.replace(tombol_lama, tombol_baru)
    print("OK: tombol Print+WA L3 berhasil di-restyle ke Bootstrap.")
else:
    print("SKIP: pola tombol lama tidak ditemukan persis, cek manual.")

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)

print("\nSELESAI, tersimpan ke", fpath)
