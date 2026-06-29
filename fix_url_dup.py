content = open("combat/urls.py", "r", encoding="utf-8").read()
old = "    path('tambah-atlet/', views.TambahAtletView.as_view(), name='tambah_atlet'),\r\n    path('tambah-atlet/', views.TambahAtletView.as_view(), name='tambah_atlet'),"
new = "    path('tambah-atlet/', views.TambahAtletView.as_view(), name='tambah_atlet'),"
if old in content:
    content = content.replace(old, new)
    open("combat/urls.py", "w", encoding="utf-8").write(content)
    print("Duplikat dihapus!")
else:
    print("Tidak ditemukan, cek manual")
