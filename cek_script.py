import re
path = r'combat\templates\combat\report_card.html'
with open(path, 'r', encoding='utf-8') as f:
    old = f.read()
script_match = re.search(r'(<script>.*?</script>)', old, re.DOTALL)
chart_script = script_match.group(1) if script_match else ''
print('Chart script ditemukan:', len(chart_script), 'chars')
print('Siap untuk redesign')
