content = open("hpcs_config/urls.py", "r", encoding="utf-8").read()
content = content.rstrip()
if content.endswith("]"):
    content = content[:-1].rstrip()
open("hpcs_config/urls.py", "w", encoding="utf-8").write(content + "\n")
print("Selesai. Isi file:")
print(open("hpcs_config/urls.py").read())
