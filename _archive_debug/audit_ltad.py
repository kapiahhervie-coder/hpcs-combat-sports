content = open("combat/templates/combat/tambah_atlet.html", "r", encoding="utf-8").read()

# Hitung semua select tahap_ltad
import re
selects = [(m.start(), m.end()) for m in re.finditer(r'<select[^>]*name="tahap_ltad"[^>]*>.*?</select>', content, re.DOTALL)]
print(f"Jumlah select tahap_ltad: {len(selects)}")
for i, (s, e) in enumerate(selects):
    print(f"Select {i+1}: pos {s}-{e}, preview: {repr(content[s:s+60])}")
