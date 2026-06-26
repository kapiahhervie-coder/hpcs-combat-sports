path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Cek apakah endblock sudah ada
if 'endblock' not in c:
    # Tambahkan endblock sebelum </body></html> di akhir
    if '</body>' in c:
        c = c.replace('</body>\n</html>', '{% endblock %}\n</body>\n</html>')
    else:
        c = c + '\n{% endblock %}'
    print('OK: endblock ditambahkan')
else:
    print('OK: endblock sudah ada')

# Cek juga apakah ada DOCTYPE di dalam block content (tidak perlu)
# Django template tidak butuh DOCTYPE di dalam block
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
