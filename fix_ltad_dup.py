content = open("combat/templates/combat/tambah_atlet.html", "r", encoding="utf-8").read()

# Hitung kemunculan
count = content.count('name="tahap_ltad"')
print(f"Select tahap_ltad ditemukan: {count} kali")

if count == 2:
    # Hapus select kedua yang kosong (-- Pilih Tahap -- tanpa options)
    import re
    # Cari dan hapus select duplikat yang hanya punya placeholder
    old = """        <div class="form-group" style="margin-bottom:0">
          <label>Tahap Long-Term Athlete Development</label>
          <select name="tahap_ltad">
            <option value="">-- Pilih Tahap --</option>
            <option value="fundamental">FUNdamental (6-9 thn)</option>
            <option value="learn_train">Learn to Train (9-12 thn)</option>
            <option value="train_train">Train to Train (12-16 thn)</option>
            <option value="train_compete">Train to Compete (16-19 thn)</option>
            <option value="train_win">Train to Win (19+ thn)</option>
            <option value="active_life">Active for Life</option>
          </select>
        </div>"""
    
    count_old = content.count(old)
    print(f"Blok LTAD lengkap ditemukan: {count_old} kali")
    
    if count_old == 2:
        # Hapus yang kedua, simpan yang pertama
        idx = content.find(old)
        idx2 = content.find(old, idx + len(old))
        content = content[:idx2] + content[idx2 + len(old):]
        open("combat/templates/combat/tambah_atlet.html", "w", encoding="utf-8").write(content)
        print("Duplikat dihapus!")
    else:
        print("Pola tidak cocok - perlu cek manual")
