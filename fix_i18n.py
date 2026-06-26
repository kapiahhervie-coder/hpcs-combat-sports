path = r'templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Tambah terjemahan konten halaman ke TRANSLATIONS
old_trans = "  en: {"
new_trans = """  page: {
    id: {
      'IDENTITAS ATLET': 'IDENTITAS ATLET',
      'DATA MENTAH PILAR L2': 'DATA MENTAH PILAR L2',
      'STRENGTH DISTRIBUTION RADAR': 'RADAR DISTRIBUSI KEKUATAN',
      'AUDIT RESULT': 'HASIL AUDIT',
      'Pilih Atlet': 'Pilih Atlet',
      'SIMPAN DATA L2': 'SIMPAN DATA L2',
      'Cetak PDF (Browser)': 'Cetak PDF (Browser)',
      'LOWER': 'LOWER',
      'PUSH': 'PUSH',
      'PULL': 'PULL',
      'CORE': 'CORE',
      'ISOMETRIC': 'ISOMETRIC',
      'Beban': 'Beban',
      'BW Ratio': 'Rasio BB',
      'Reps': 'Repetisi',
      'Detik': 'Detik',
      'Total hold': 'Total tahan',
      'Tremor onset': 'Awal tremor',
      'History Audit L2': 'Riwayat Audit L2',
      'Record': 'Record',
      'Tanggal': 'Tanggal',
      'Atlet': 'Atlet',
      'Kategori': 'Kategori',
      'Total': 'Total',
      'Predikat': 'Predikat',
      'Aksi': 'Aksi',
      'Lihat Standar Rubrik & Protokol': 'Lihat Standar Rubrik & Protokol',
      'Rekomendasi Pelatih': 'Rekomendasi Pelatih',
      'Profil Kondisi Atlet': 'Profil Kondisi Atlet',
      'KEUNGGULAN': 'KEUNGGULAN',
      'AREA KELEMAHAN': 'AREA KELEMAHAN',
      'KESIMPULAN': 'KESIMPULAN',
      'History Audit L1': 'Riwayat Audit L1',
      'Database & History Audit': 'Database & Riwayat Audit',
      'Biomechanics Radar': 'Radar Biomekanik',
      'Pilar Analysis': 'Analisis Pilar',
      'Audit Result': 'Hasil Audit',
      'SAVE AUDIT': 'SIMPAN AUDIT',
      'Rekomendasi HPCS': 'Rekomendasi HPCS',
      'Identitas Atlet': 'Identitas Atlet',
      'Pilih Atlet': 'Pilih Atlet',
      'HPCS Level 1': 'HPCS Level 1',
      'HPCS Level 2': 'HPCS Level 2',
      'History Audit L3': 'Riwayat Audit L3',
      'History Audit L4': 'Riwayat Audit L4',
      'SIMPAN DATA L3': 'SIMPAN DATA L3',
      'SIMPAN DATA L4': 'SIMPAN DATA L4',
      'Belum ada data': 'Belum ada data'
    },
    en: {
      'IDENTITAS ATLET': 'ATHLETE IDENTITY',
      'DATA MENTAH PILAR L2': 'L2 RAW PILLAR DATA',
      'STRENGTH DISTRIBUTION RADAR': 'STRENGTH DISTRIBUTION RADAR',
      'AUDIT RESULT': 'AUDIT RESULT',
      'Pilih Atlet': 'Select Athlete',
      'SIMPAN DATA L2': 'SAVE L2 DATA',
      'Cetak PDF (Browser)': 'Print PDF',
      'LOWER': 'LOWER',
      'PUSH': 'PUSH',
      'PULL': 'PULL',
      'CORE': 'CORE',
      'ISOMETRIC': 'ISOMETRIC',
      'Beban': 'Load',
      'BW Ratio': 'BW Ratio',
      'Reps': 'Reps',
      'Detik': 'Seconds',
      'Total hold': 'Total hold',
      'Tremor onset': 'Tremor onset',
      'History Audit L2': 'L2 Audit History',
      'Record': 'Record',
      'Tanggal': 'Date',
      'Atlet': 'Athlete',
      'Kategori': 'Category',
      'Total': 'Total',
      'Predikat': 'Predicate',
      'Aksi': 'Action',
      'Lihat Standar Rubrik & Protokol': 'View Rubric & Protocol Standards',
      'Rekomendasi Pelatih': 'Coach Recommendations',
      'Profil Kondisi Atlet': 'Athlete Condition Profile',
      'KEUNGGULAN': 'STRENGTHS',
      'AREA KELEMAHAN': 'WEAKNESS AREAS',
      'KESIMPULAN': 'CONCLUSION',
      'History Audit L1': 'L1 Audit History',
      'Database & History Audit': 'Database & Audit History',
      'Biomechanics Radar': 'Biomechanics Radar',
      'Pilar Analysis': 'Pillar Analysis',
      'Audit Result': 'Audit Result',
      'SAVE AUDIT': 'SAVE AUDIT',
      'Rekomendasi HPCS': 'HPCS Recommendations',
      'Identitas Atlet': 'Athlete Identity',
      'Pilih Atlet': 'Select Athlete',
      'HPCS Level 1': 'HPCS Level 1',
      'HPCS Level 2': 'HPCS Level 2',
      'History Audit L3': 'L3 Audit History',
      'History Audit L4': 'L4 Audit History',
      'SIMPAN DATA L3': 'SAVE L3 DATA',
      'SIMPAN DATA L4': 'SAVE L4 DATA',
      'Belum ada data': 'No data available'
    }
  },
  en: {"""

if 'page:' not in c:
    c = c.replace('  en: {', new_trans)
    print('OK 1: terjemahan halaman ditambahkan')
else:
    print('SKIP 1: sudah ada')

# Update fungsi applyLang untuk juga translate konten halaman
old_apply = """function applyLang(lang) {
  var t = TRANSLATIONS[lang] || TRANSLATIONS['id'];
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });"""

new_apply = """function applyLang(lang) {
  var t = TRANSLATIONS[lang] || TRANSLATIONS['id'];
  // Translate sidebar
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });
  // Translate page content
  var pt = TRANSLATIONS.page[lang] || TRANSLATIONS.page['id'];
  if (pt) {
    // Translate semua elemen teks di halaman
    var selectors = [
      '.card-title', '.section-label', 'h1', 'h2', 'h3', 'h4', 'h5',
      '.pilar-label', '.pilar-name', 'th', 'button[type=submit]',
      '.history-header .card-title', 'label', '.card-title'
    ];
    selectors.forEach(function(sel) {
      document.querySelectorAll(sel).forEach(function(el) {
        var orig = el.getAttribute('data-orig') || el.textContent.trim();
        if (!el.getAttribute('data-orig')) el.setAttribute('data-orig', orig);
        if (pt[orig]) {
          // Jaga ikon/child elements
          if (el.childElementCount === 0) {
            el.textContent = pt[orig];
          } else {
            el.childNodes.forEach(function(node) {
              if (node.nodeType === 3) {
                var txt = node.textContent.trim();
                if (pt[txt]) node.textContent = node.textContent.replace(txt, pt[txt]);
              }
            });
          }
        }
      });
    });
    // Translate placeholder
    document.querySelectorAll('[placeholder]').forEach(function(el) {
      var orig = el.getAttribute('data-orig-ph') || el.placeholder;
      if (!el.getAttribute('data-orig-ph')) el.setAttribute('data-orig-ph', orig);
      if (pt[orig]) el.placeholder = pt[orig];
    });
  }"""

if old_apply in c:
    c = c.replace(old_apply, new_apply)
    print('OK 2: applyLang diupdate untuk translate konten halaman')
else:
    print('SKIP 2')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
