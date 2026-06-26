path = r'combat\templates\combat\l3_power.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Hapus tombol Cetak PDF biru (btn-print-sm)
old_biru = '''          <button type="button" class="btn-print-sm no-print" onclick="handlePrint()">
            <i class="bi bi-file-earmark-pdf-fill"></i> Cetak PDF
          </button>'''
if old_biru in c:
    c = c.replace(old_biru, '')
    print('OK 1: tombol Cetak PDF biru dihapus')
else:
    print('SKIP 1')

# FIX 2: Hapus tombol cetak duplikat kedua di tabel
import re
# Cari semua tombol print di tabel - hapus yang kedua
buttons = list(re.finditer(r'<button onclick="window\.print\(\)".*?</button>', c, re.DOTALL))
print(f'Jumlah tombol print: {len(buttons)}')
if len(buttons) >= 2:
    # Hapus yang kedua
    second = buttons[1]
    c = c[:second.start()] + c[second.end():]
    print('OK 2: tombol print duplikat kedua dihapus')

# FIX 3: Pindahkan narasi dari kolom kanan ke kolom tengah (bawah radar)
# Hapus dari kolom kanan
old_narasi = '''          <!-- Profil Kondisi Atlet -->
          <div id="narasi_l3" style="display:none;margin-top:10px;text-align:left;">
            <div style="font-size:10px;font-weight:700;color:var(--amber);letter-spacing:1px;margin-bottom:6px;">
              &#9889; PROFIL KONDISI ATLET
            </div>
            <div id="narasi_box_l3" style="
              background:rgba(245,158,11,0.05);
              border:1px solid rgba(245,158,11,0.2);
              border-radius:10px;padding:12px;
              font-size:11px;line-height:1.7;
              color:#9ca3af;max-height:280px;
              overflow-y:auto;text-align:left;">
            </div>
          </div>'''

new_narasi = ''  # hapus dari kolom kanan

if old_narasi in c:
    c = c.replace(old_narasi, new_narasi)
    print('OK 3: narasi dihapus dari kolom kanan')

# Sisipkan narasi di bawah score-pills (kolom tengah)
old_pills = '''        <div class="score-pills">
          <span class="score-pill" id="p_jump">Jump: —</span>
          <span class="score-pill" id="p_sprint">Sprint: —</span>
          <span class="score-pill" id="p_throw">Throw: —</span>
          <span class="score-pill" id="p_rsi">RSI: —</span>
          <span class="score-pill" id="p_agility">Agility: —</span>
        </div>'''

new_pills = '''        <div class="score-pills">
          <span class="score-pill" id="p_jump">Jump: —</span>
          <span class="score-pill" id="p_sprint">Sprint: —</span>
          <span class="score-pill" id="p_throw">Throw: —</span>
          <span class="score-pill" id="p_rsi">RSI: —</span>
          <span class="score-pill" id="p_agility">Agility: —</span>
        </div>
        <!-- Profil Kondisi Atlet di bawah radar -->
        <div id="narasi_l3" style="display:none;margin-top:12px;text-align:left;">
          <div style="font-size:10px;font-weight:700;color:var(--amber);letter-spacing:1px;margin-bottom:6px;padding:0 4px;">
            &#9889; PROFIL KONDISI ATLET
          </div>
          <div id="narasi_box_l3" style="
            background:rgba(245,158,11,0.05);
            border:1px solid rgba(245,158,11,0.2);
            border-radius:10px;padding:12px;
            font-size:11px;line-height:1.7;
            color:#9ca3af;max-height:320px;
            overflow-y:auto;text-align:left;">
          </div>
        </div>'''

if old_pills in c:
    c = c.replace(old_pills, new_pills)
    print('OK 3b: narasi dipindah ke bawah radar')
else:
    print('SKIP 3b')

# FIX 4: Perbesar kolom tengah & kecilkan kolom kanan via CSS
old_css = '.l3-col-right{'
if old_css in c:
    # Cari dan update grid
    c = re.sub(
        r'grid-template-columns:[^;]+;',
        'grid-template-columns: 1fr 1.4fr 1fr;',
        c, count=1
    )
    print('OK 4: grid columns disesuaikan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
