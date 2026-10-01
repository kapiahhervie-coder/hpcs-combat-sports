# Fix CABANG_CHOICES di combat/models.py
fpath = "combat/models.py"
with open(fpath, encoding="utf-8") as f:
    content = f.read()

old = """CABANG_CHOICES = [
    ('boxing',  'Boxing'),
    ('muaythai', 'Muay Thai'),
    ('tkd',     'Taekwondo'),
    ('krt',     'Karate'),
    ('sepakbola', 'Sepak Bola'),
]"""

new = """CABANG_CHOICES = [
    ('boxing',      'Boxing'),
    ('muaythai',    'Muay Thai'),
    ('tkd',         'Taekwondo'),
    ('krt',         'Karate'),
    ('sepakbola',   'Sepak Bola'),
    ('basketball',  'Bola Basket'),
    ('volleyball',  'Bola Voli'),
    ('badminton',   'Bulutangkis'),
]"""

if old in content:
    content = content.replace(old, new)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK: CABANG_CHOICES diupdate!")
else:
    print("WARN: pattern tidak ditemukan")
