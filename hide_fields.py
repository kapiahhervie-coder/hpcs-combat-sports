path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Sembunyikan via CSS saja — AMAN, tidak potong HTML
if '.hide-admin-fields' not in c:
    css = '''<style>
/* Sembunyikan field yang sudah ada di admin */
#usia_atlet, #gender_atlet, #input_berat,
label[for="usia_atlet"], label[for="gender_atlet"], label[for="input_berat"],
.col-4:has(#usia_atlet), .col-4:has(#gender_atlet), .col-4:has(#input_berat) {
    display: none !important;
}
</style>'''
    c = c.replace('</head>', css + '\n</head>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('OK: field BB/Gender/Kategori disembunyikan via CSS')
else:
    print('SKIP: sudah ada')
