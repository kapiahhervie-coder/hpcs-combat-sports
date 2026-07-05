content = open("combat/templates/combat/tambah_atlet.html", "r", encoding="utf-8").read()
old = "  if (usia <= 9)  return { kategori: 'JUNIOR', ltad: 'fundamental' };"
new = "  if (usia <= 9)  return { kategori: 'JUNIOR', ltad: 'fundamental' };  // FUNdamental"
# Cek dulu apakah value fundamental ada di select
print("Value fundamental ada:", "value=\"fundamental\"" in content)
print("Script auto-set LTAD ada:", "rec.ltad" in content)
