path = r'combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Hapus narasi_panel dari kolom kanan
OLD_NARASI = '''
          <div id="narasi_panel" class="mt-3 text-start" style="display:none">
            <div class="card-title"><i class="bi bi-person-lines-fill" style="color:var(--cyan)"></i> Profil Kondisi Atlet</div>
            <div id="narasi_box" style="background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.2);border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.7;color:var(--text2);"></div>
          </div>'''

if OLD_NARASI in c:
    c = c.replace(OLD_NARASI, '')
    print('OK 1: narasi dihapus dari kolom kanan')
else:
    print('SKIP 1')

# Sisipkan narasi di bawah canvas radarChart
OLD_RADAR = '''            <canvas id="radarChart"></canvas>
            <img id="chart-image" alt="Radar" style="display:none;max-width:100%">
          </div>
        </div>
      </div>'''

NEW_RADAR = '''            <canvas id="radarChart"></canvas>
            <img id="chart-image" alt="Radar" style="display:none;max-width:100%">
          </div>
          <div id="narasi_panel" class="mt-3 text-start" style="display:none">
            <div class="card-title"><i class="bi bi-person-lines-fill" style="color:var(--cyan)"></i> Profil Kondisi Atlet</div>
            <div id="narasi_box" style="background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.2);border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.7;color:var(--text2);text-align:left;"></div>
          </div>
        </div>
      </div>'''

if OLD_RADAR in c:
    c = c.replace(OLD_RADAR, NEW_RADAR)
    print('OK 2: narasi dipindah ke bawah radar')
else:
    print('SKIP 2')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
