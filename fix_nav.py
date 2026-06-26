content = open("templates/base.html", "r", encoding="utf-8").read()

old = """      <div class="nav-section">Laporan</div>
      <div class="nav-divider"></div>
      <div class="nav-section">Sistem</div>"""

new = """      <div class="nav-section">Sistem</div>"""

if old in content:
    content = content.replace(old, new)
    open("templates/base.html", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
