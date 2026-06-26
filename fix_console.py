path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Ganti type="number" yang display:none jadi type="hidden"
import re
c = re.sub(
    r'<input type="number" name="score_(\w+)" id="score_(\w+)" style="display:none">',
    r'<input type="hidden" name="score_\1" id="score_\2">',
    c
)
# Juga fix score_push yang masih type=number display:none
c = re.sub(
    r'<input type="number" (name="score_[^"]*" id="score_[^"]*")[^>]*style="display:none[^"]*"[^>]*>',
    r'<input type="hidden" \1>',
    c
)
print('OK 1: score inputs dijadikan type=hidden')

# FIX 2: Pindahkan Chart.js ke atas script kita
chartjs = '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
if chartjs in c:
    # Hapus dari posisi lama
    c = c.replace(chartjs, '')
    # Tambah sebelum script kita
    c = c.replace('<script>\n// ── Auto Scoring', chartjs + '\n<script>\n// ── Auto Scoring')
    print('OK 2: Chart.js dipindah ke atas')
else:
    # Tambah sebelum script
    c = c.replace('<script>\n// ── Auto Scoring', chartjs + '\n<script>\n// ── Auto Scoring')
    print('OK 2: Chart.js ditambahkan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
