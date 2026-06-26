path = r'combat\templates\combat\l4_speed_agility.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Sembunyikan Kategori/Gender/BB/Kondisi/Catatan via CSS
HIDE_CSS = '''
    /* Sembunyikan field yang ada di admin */
    .r3, .fg:has(select[name="kategori_usia"]),
    .fg:has(select[name="gender"]),
    .fg:has(input[name="kelas_berat"]),
    .fg:has(.cond-btns),
    .fg:has(textarea[name="catatan"]) { display: none !important; }
'''
c = c.replace('</style>', HIDE_CSS + '\n</style>', 1)
print('OK 1: field disembunyikan')

# FIX 2: Tambah hidden inputs agar data dari admin terkirim
old_hidden = '<input type="hidden" name="kondisi_uji" id="kondisi_uji" value="FRESH">'
new_hidden = '''<input type="hidden" name="kondisi_uji" id="kondisi_uji" value="FRESH">
          <input type="hidden" name="kategori_usia" id="h_kat_l4">
          <input type="hidden" name="gender" id="h_gen_l4">
          <input type="hidden" name="kelas_berat" id="h_bb_l4">'''
if old_hidden in c:
    c = c.replace(old_hidden, new_hidden)
    print('OK 2: hidden inputs ditambahkan')

# FIX 3: Update fungsi onAtletChange untuk isi hidden inputs
old_kat = '''  const kat = document.querySelector('select[name="kategori_usia"]');
  const gen = document.querySelector('select[name="gender"]');
  const bb  = document.querySelector('input[name="kelas_berat"]');'''
new_kat = '''  const kat = document.querySelector('select[name="kategori_usia"]');
  const gen = document.querySelector('select[name="gender"]');
  const bb  = document.querySelector('input[name="kelas_berat"]');
  const hKat = document.getElementById('h_kat_l4');
  const hGen = document.getElementById('h_gen_l4');
  const hBb  = document.getElementById('h_bb_l4');'''
if old_kat in c:
    c = c.replace(old_kat, new_kat)
    print('OK 3: hidden vars ditambahkan')

# Tambah pengisian hidden inputs di bawah pengisian select
old_fill = '  if (gen) gen.value = opt.dataset.gender;'
new_fill = '''  if (gen) gen.value = opt.dataset.gender;
  if (hKat) hKat.value = opt.dataset.kategori || 'ELITE';
  if (hGen) hGen.value = opt.dataset.gender   || 'Putra';
  if (hBb)  hBb.value  = opt.dataset.berat    || '';'''
if old_fill in c:
    c = c.replace(old_fill, new_fill)
    print('OK 4: hidden inputs diisi dari atlet data')

# FIX 5: Perbesar grid — kolom kiri lebih kecil, tengah & kanan lebih besar
# Cek grid yang ada
import re
c = re.sub(
    r'(grid-template-columns\s*:\s*)[\d\w\s]+fr[\d\w\s]+fr[\d\w\s]+fr',
    r'\g<1>300px 1fr 320px',
    c, count=1
)
print('OK 5: grid disesuaikan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
