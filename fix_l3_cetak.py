path = r'combat\templates\combat\l3_power.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = '''              <a href="{% url 'combat:hapus_l3_audit' item.pk %}" class="btn-del-sm"
                 onclick="return confirm('Hapus data {{ item.atlet_name|escapejs }}?')">
                <i class="bi bi-trash"></i>
              </a>'''

new = '''              <a href="{% url 'combat:hapus_l3_audit' item.pk %}" class="btn-del-sm"
                 onclick="return confirm('Hapus data {{ item.atlet_name|escapejs }}?')">
                <i class="bi bi-trash"></i>
              </a>
              <button onclick="window.print()" title="Cetak PDF"
                style="background:transparent;border:1px solid rgba(56,189,248,0.4);
                       color:#38bdf8;margin-left:4px;border-radius:6px;
                       padding:4px 8px;cursor:pointer;font-size:12px;">
                <i class="bi bi-printer-fill"></i>
              </button>'''

if old in c:
    c = c.replace(old, new)
    print('OK: tombol cetak ditambahkan')
else:
    print('SKIP - cek pattern')
    # Cari alternatif
    idx = c.find('hapus_l3_audit')
    print('hapus_l3_audit ada di index:', idx)
    print('Konteks:', c[idx-50:idx+200])

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
