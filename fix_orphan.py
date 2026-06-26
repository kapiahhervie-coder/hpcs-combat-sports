path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Ganti sisa messages yang rusak dengan blok lengkap yang benar
old = '''</div>
        {% endfor %}
    </div>
    {% endif %}
    <!-- ── HEADER'''

new = '''</div>
    <!-- ── HEADER'''

if old in c:
    c = c.replace(old, new)
    print('OK: sisa messages dihapus')
else:
    print('SKIP: cari manual')
    # Cari endfor yang orphan
    idx = c.find('{% endfor %}\n    </div>\n    {% endif %}')
    if idx > 0:
        end = c.find('{% endif %}', idx) + 11
        c = c[:idx] + c[end:]
        print('OK alt: orphan endfor dihapus')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
