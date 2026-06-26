content = open("hpcs_config/urls.py", "r", encoding="utf-8-sig").read()
open("hpcs_config/urls.py", "w", encoding="utf-8").write(content)
print("BOM dihapus. Cek:")
print(open("hpcs_config/urls.py", encoding="utf-8").read()[:50])
