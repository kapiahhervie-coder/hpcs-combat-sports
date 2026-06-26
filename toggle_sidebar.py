path = r'templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Tambah CSS toggle sidebar
TOGGLE_CSS = '''
    .sidebar{transition:width .25s ease;}
    .sidebar.collapsed{width:54px;}
    .sidebar.collapsed .brand-sub,
    .sidebar.collapsed .nav-section,
    .sidebar.collapsed .nav-badge,
    .sidebar.collapsed .nav-link-text,
    .sidebar.collapsed .user-name,
    .sidebar.collapsed .logout-link{display:none !important;}
    .sidebar.collapsed .brand-name{font-size:13px;letter-spacing:1px;}
    .sidebar.collapsed .nav-link{padding:10px 0;justify-content:center;}
    .sidebar.collapsed .nav-icon{width:54px;text-align:center;font-size:17px;}
    .sidebar.collapsed .sidebar-brand{padding:14px 0;text-align:center;}
    .sidebar.collapsed .sidebar-footer{padding:10px 0;justify-content:center;}
    .sidebar-toggle{position:absolute;top:14px;right:-12px;width:24px;height:24px;
      background:#ef4444;border-radius:50%;display:flex;align-items:center;
      justify-content:center;cursor:pointer;z-index:200;font-size:12px;
      color:#fff;border:2px solid #0f0f0f;transition:transform .25s;}
    .sidebar.collapsed .sidebar-toggle{transform:rotate(180deg);}
    .main-content{transition:margin-left .25s ease;}
    .main-content.expanded{margin-left:54px;}
'''

# Wrap teks nav-link dengan span.nav-link-text
import re
c = re.sub(
    r'(<span class="nav-icon">[^<]*</span>)\s*([^\n<]+?)(<span class="nav-badge">)',
    r'\1 <span class="nav-link-text">\2</span>\3',
    c
)
c = re.sub(
    r'(<span class="nav-icon">[^<]*</span>)\s*([A-Za-z][^\n<]+)\n(\s*</a>)',
    r'\1 <span class="nav-link-text">\2</span>\n\3',
    c
)

# Tambah tombol toggle di sidebar
c = c.replace(
    '<div class="sidebar-brand">',
    '<div class="sidebar-toggle" onclick="toggleSidebar()">&#9664;</div>\n    <div class="sidebar-brand">'
)

# Tambah CSS
c = c.replace('</style>', TOGGLE_CSS + '\n</style>', 1)

# Tambah JavaScript toggle
TOGGLE_JS = '''
<script>
function toggleSidebar() {
    var sb = document.querySelector('.sidebar');
    var mc = document.querySelector('.main-content');
    sb.classList.toggle('collapsed');
    if (mc) mc.classList.toggle('expanded');
    localStorage.setItem('sidebar_collapsed', sb.classList.contains('collapsed'));
}
// Restore state
window.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('sidebar_collapsed') === 'true') {
        var sb = document.querySelector('.sidebar');
        var mc = document.querySelector('.main-content');
        if (sb) sb.classList.add('collapsed');
        if (mc) mc.classList.add('expanded');
    }
});
</script>'''

c = c.replace('</body>', TOGGLE_JS + '\n</body>')
print('OK: toggle sidebar ditambahkan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
