content = open("combat/templates/combat/tambah_atlet.html", "r", encoding="utf-8").read()

old = """// Auto-sinkron LTAD berdasarkan Kategori Usia
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
});"""

new = """// Hitung usia dari tanggal lahir
function hitungUsia(tglLahir) {
  const today = new Date();
  const lahir = new Date(tglLahir);
  let usia = today.getFullYear() - lahir.getFullYear();
  const m = today.getMonth() - lahir.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < lahir.getDate())) usia--;
  return usia;
}

// Tentukan kategori dari usia
function kategoriDariUsia(usia) {
  if (usia <= 9)  return { kategori: 'JUNIOR', ltad: 'fundamental' };
  if (usia <= 13) return { kategori: 'JUNIOR', ltad: 'learn_train' };
  if (usia <= 17) return { kategori: 'YOUTH',  ltad: 'train_train' };
  if (usia <= 23) return { kategori: 'ELITE',  ltad: 'train_compete' };
  return           { kategori: 'SENIOR', ltad: 'train_win' };
}

// Auto-isi kategori & LTAD saat tanggal lahir diisi
document.querySelector('[name="tanggal_lahir"]').addEventListener('change', function() {
  if (!this.value) return;
  const usia = hitungUsia(this.value);
  const rec = kategoriDariUsia(usia);

  // Set kategori otomatis
  document.querySelector('[name="kategori_umur"]').value = rec.kategori;
  // Set LTAD otomatis
  document.querySelector('[name="tahap_ltad"]').value = rec.ltad;

  // Tampilkan info usia
  let info = document.getElementById('info-usia');
  if (!info) {
    info = document.createElement('small');
    info.id = 'info-usia';
    info.style.cssText = 'display:block;margin-top:4px;color:#10b981;font-size:11px';
    document.querySelector('[name="tanggal_lahir"]').parentNode.appendChild(info);
  }
  info.textContent = 'Usia: ' + usia + ' tahun -> Kategori ' + rec.kategori + ' otomatis';
});

// Validasi sinkron saat submit
document.querySelector('form').addEventListener('submit', function(e) {
  const tgl = document.querySelector('[name="tanggal_lahir"]').value;
  if (!tgl) return; // Tanggal opsional, skip validasi

  const usia = hitungUsia(tgl);
  const rec = kategoriDariUsia(usia);
  const kategoriDipilih = document.querySelector('[name="kategori_umur"]').value;

  if (kategoriDipilih && kategoriDipilih !== rec.kategori) {
    e.preventDefault();
    let warn = document.getElementById('warn-kategori');
    if (!warn) {
      warn = document.createElement('div');
      warn.id = 'warn-kategori';
      warn.style.cssText = 'background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);color:#f59e0b;padding:10px 14px;border-radius:8px;font-size:12px;margin-bottom:14px';
      document.querySelector('.card-body').prepend(warn);
    }
    warn.innerHTML = '&#9888; Peringatan: Usia atlet <strong>' + usia + ' tahun</strong> tidak sesuai dengan kategori <strong>' + kategoriDipilih + '</strong>. Kategori yang sesuai adalah <strong>' + rec.kategori + '</strong>. Klik Simpan lagi untuk tetap menyimpan dengan data ini.';
    // Hapus validasi setelah peringatan ditampilkan (izinkan submit kedua)
    this.removeEventListener('submit', arguments.callee);
  }
});

// Auto-sinkron LTAD saat kategori diubah manual
const kategoriToLtad = {
  'YOUTH':  'train_train',
  'JUNIOR': 'learn_train',
  'ELITE':  'train_compete',
  'SENIOR': 'train_win',
};
document.querySelector('[name="kategori_umur"]').addEventListener('change', function() {
  const ltadSelect = document.querySelector('[name="tahap_ltad"]');
  const mapped = kategoriToLtad[this.value];
  if (mapped) ltadSelect.value = mapped;
});"""

if old in content:
    content = content.replace(old, new)
    open("combat/templates/combat/tambah_atlet.html", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
