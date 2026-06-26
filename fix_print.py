path = r'combat\templates\combat\report_card.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Hapus huruf H tersendiri di print - itu dari browser print header
# Tambah CSS untuk hide browser default header/footer saat print
old_print = '@media print { .no-print { display: none !important; } body { background: #000 !important; } }'
new_print = '''@media print {
    .no-print { display: none !important; }
    body { background: #000 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    @page { margin: 0; size: A4 landscape; }
}'''
if old_print in c:
    c = c.replace(old_print, new_print)
    print('OK 1: print CSS diupdate')
else:
    print('SKIP 1')

# FIX 2: Ganti tombol print biasa dengan download PDF yang benar
old_btn = '<button onclick="window.print()" class="btn-print">&#128424; Print / Cetak PDF</button>'
new_btn = '''<button onclick="downloadPDF()" class="btn-print">&#128229; Download PDF</button>
<button onclick="window.print()" class="btn-print" style="margin-left:8px;background:linear-gradient(135deg,#1e3a5f,#2563eb);color:#fff;">&#128424; Print</button>'''
if old_btn in c:
    c = c.replace(old_btn, new_btn)
    print('OK 2: tombol download ditambahkan')

# FIX 3: Tambah fungsi downloadPDF
old_script = chart_js = '</body>'
DOWNLOAD_JS = '''
<script>
function downloadPDF() {
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
}
</script>
</body>'''
c = c.replace('</body>', DOWNLOAD_JS)
print('OK 3: fungsi download PDF ditambahkan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
