path = r'combat\templates\combat\l2_strenght.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Pastikan Chart.js ada dan dipanggil sebelum script kita
chartjs = '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
if chartjs not in c:
    c = c.replace('<script>\n// ── Auto Scoring', chartjs + '\n<script>\n// ── Auto Scoring')
    print('OK: Chart.js ditambahkan')
else:
    print('Chart.js sudah ada di:', c.find(chartjs))

# Panggil updateRadar setelah DOM ready
if 'window.addEventListener' not in c:
    init = '''
<script>
window.addEventListener('load', function() {
    updateRadar([0,0,0,0,0]);
});
</script>'''
    c = c.replace('{% endblock %}', init + '\n{% endblock %}')
    print('OK: init radar ditambahkan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
