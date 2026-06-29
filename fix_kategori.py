content = open("combat/templates/combat/tambah_atlet.html", "r", encoding="utf-8").read()

old = """              <option value="ELITE">Elite</option>
              <option value="YOUTH">Youth</option>
              <option value="JUNIOR">Junior</option>
              <option value="SENIOR">Senior</option>"""

new = """              <option value="ELITE">Elite (18-23 thn)</option>
              <option value="YOUTH">Youth (14-17 thn)</option>
              <option value="JUNIOR">Junior (10-13 thn)</option>
              <option value="SENIOR">Senior (24+ thn)</option>"""

if old in content:
    content = content.replace(old, new)
    open("combat/templates/combat/tambah_atlet.html", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
