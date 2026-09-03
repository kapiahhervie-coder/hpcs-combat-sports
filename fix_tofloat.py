fpath = "boxing/views.py"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

# Fix semua variasi to_float yang tidak handle koma
old1 = """            def to_float(key):
                val = request.POST.get(key)
                return float(val) if val else None"""

new1 = """            def to_float(key):
                val = request.POST.get(key)
                if not val: return None
                try: return float(str(val).replace(',', '.').strip())
                except: return None"""

count = content.count(old1)
print(f"Ditemukan {count} instance to_float lama")
content = content.replace(old1, new1)

# Fix juga versi dengan try-except
old2 = """            def to_float(key):
                val = request.POST.get(key)
                try:
                    return float(val) if val else None
                except (ValueError, TypeError):
                    return None"""

new2 = """            def to_float(key):
                val = request.POST.get(key)
                if not val: return None
                try: return float(str(val).replace(',', '.').strip())
                except: return None"""

count2 = content.count(old2)
print(f"Ditemukan {count2} instance to_float try-except lama")
content = content.replace(old2, new2)

# Fix float() langsung di POST yang tidak pakai to_float
# Ganti score_jump dll yang pakai float() langsung
import re
def fix_direct_float(m):
    val = m.group(1)
    return f"float(str(request.POST.get('{val}', 0) or 0).replace(',', '.'))"

content = re.sub(
    r"float\(request\.POST\.get\('(score_[^']+)',\s*0\)\)",
    fix_direct_float,
    content
)

with open(fpath, "w", encoding="utf-8") as f:
    f.write(content)
print("OK: semua to_float sudah support koma desimal!")
