path = r'combat\templates\combat\report_card.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Tambah library html2pdf setelah chart.js
old_script = '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
new_script = '''<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>'''
if old_script in c:
    c = c.replace(old_script, new_script)
    print('OK 1: html2pdf ditambahkan')

# Ganti fungsi downloadPDF
old_func = '''function downloadPDF() {
    // Buka dialog save as PDF
    var opt = {
        filename: 'HPCS-Report-{{ atlet.nama_atlet }}.pdf'
    };
    // Gunakan print dialog dengan instruksi save as PDF
    var style = document.createElement('style');
    style.textContent = '@page { size: A4 landscape; margin: 0; }';
    document.head.appendChild(style);
    window.print();
    setTimeout(function(){ document.head.removeChild(style); }, 1000);
}'''

new_func = '''function downloadPDF() {
    var btn = document.querySelector('.btn-print');
    if (btn) btn.style.display = 'none';
    var footer = document.querySelector('.report-footer');
    if (footer) footer.style.display = 'none';
    var element = document.body;
    var opt = {
        margin: 0,
        filename: 'HPCS-Report-Benaya.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, backgroundColor: '#05080f' },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
    };
    html2pdf().set(opt).from(element).save().then(function() {
        if (btn) btn.style.display = '';
        if (footer) footer.style.display = '';
    });
}'''

if old_func in c:
    c = c.replace(old_func, new_func)
    print('OK 2: fungsi downloadPDF diupdate')
else:
    # Cari dan ganti apapun yang ada
    import re
    c = re.sub(r'function downloadPDF\(\)\s*\{[^}]+\}', new_func, c)
    print('OK 2: fungsi downloadPDF diupdate (regex)')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
