content = open("combat/templates/combat/tambah_atlet.html", "r", encoding="utf-8").read()

old = """</body>
</html>"""

new = """<script>
// Auto-sinkron LTAD berdasarkan Kategori Usia
const kategoriToLtad = {
  'YOUTH':  'learn_train',    // Youth 14-17 -> Learn to Train
  'JUNIOR': 'train_train',    // Junior 10-13 -> Train to Train
  'ELITE':  'train_compete',  // Elite 18-23 -> Train to Compete
  'SENIOR': 'train_win',      // Senior 24+  -> Train to Win
};

document.querySelector('[name="kategori_umur"]').addEventListener('change', function() {
  const ltadSelect = document.querySelector('[name="tahap_ltad"]');
  const mapped = kategoriToLtad[this.value];
  if (mapped) ltadSelect.value = mapped;
});
</script>
</body>
</html>"""

if old in content:
    content = content.replace(old, new)
    open("combat/templates/combat/tambah_atlet.html", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
