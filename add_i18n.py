path = r'templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Tambah data-i18n ke semua teks sidebar
c = c.replace(
    '<div class="nav-section">Dashboard</div>',
    '<div class="nav-section" data-i18n="nav_dashboard">Dashboard</div>'
)
c = c.replace(
    '<span class="nav-link-text">Boxing Division</span>',
    '<span class="nav-link-text" data-i18n="nav_boxing">Boxing Division</span>'
)
c = c.replace(
    '<div class="nav-section">Assessment</div>',
    '<div class="nav-section" data-i18n="nav_assessment">Assessment</div>'
)
c = c.replace(
    '<span class="nav-link-text">L1 — Correction</span>',
    '<span class="nav-link-text" data-i18n="nav_l1">L1 — Correction</span>'
)
c = c.replace(
    '<span class="nav-link-text">L2 — Strength</span>',
    '<span class="nav-link-text" data-i18n="nav_l2">L2 — Strength</span>'
)
c = c.replace(
    '<span class="nav-link-text">L3 — Power</span>',
    '<span class="nav-link-text" data-i18n="nav_l3">L3 — Power</span>'
)
c = c.replace(
    '<span class="nav-link-text">L4 — Speed & Agility</span>',
    '<span class="nav-link-text" data-i18n="nav_l4">L4 — Speed & Agility</span>'
)
c = c.replace(
    '<div class="nav-section">Sistem</div>',
    '<div class="nav-section" data-i18n="nav_system">Sistem</div>'
)
c = c.replace(
    '<span class="nav-link-text">Admin Panel</span>',
    '<span class="nav-link-text" data-i18n="nav_admin">Admin Panel</span>'
)
c = c.replace(
    '<div class="brand-sub">High Performance Combat Sports</div>',
    '<div class="brand-sub" data-i18n="brand_sub">High Performance Combat Sports</div>'
)
print('OK 1: data-i18n ditambahkan ke sidebar')

# FIX 2: Tambah tombol language switcher di sidebar footer
old_footer = '<span class="user-name">{{ request.user.username }}</span>'
new_footer = '''<span class="user-name">{{ request.user.username }}</span>
      <div class="lang-switcher" style="display:flex;gap:4px;margin-top:6px;">
        <button onclick="setLang(\'id\')" id="btn_id"
          style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);
                 color:#9ca3af;border-radius:4px;padding:2px 7px;font-size:10px;
                 cursor:pointer;font-weight:600;transition:all 0.15s;">
          &#127470;&#127465; ID
        </button>
        <button onclick="setLang(\'en\')" id="btn_en"
          style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
                 color:#9ca3af;border-radius:4px;padding:2px 7px;font-size:10px;
                 cursor:pointer;font-weight:600;transition:all 0.15s;">
          &#127468;&#127463; EN
        </button>
      </div>'''
if old_footer in c:
    c = c.replace(old_footer, new_footer)
    print('OK 2: tombol bahasa ditambahkan')

# FIX 3: Tambah script i18n sebelum </body>
I18N_SCRIPT = '''
<script>
var TRANSLATIONS = {
  id: {
    nav_dashboard:  'Dashboard',
    nav_boxing:     'Divisi Boxing',
    nav_assessment: 'Asesmen',
    nav_l1:         'L1 \u2014 Koreksi',
    nav_l2:         'L2 \u2014 Kekuatan',
    nav_l3:         'L3 \u2014 Power',
    nav_l4:         'L4 \u2014 Kecepatan & Kelincahan',
    nav_system:     'Sistem',
    nav_admin:      'Panel Admin',
    nav_report:     'Pusat Laporan',
    nav_coach:      'Manajemen Coach',
    brand_sub:      'Olahraga Tempur Performa Tinggi',
    logout:         'Keluar'
  },
  en: {
    nav_dashboard:  'Dashboard',
    nav_boxing:     'Boxing Division',
    nav_assessment: 'Assessment',
    nav_l1:         'L1 \u2014 Correction',
    nav_l2:         'L2 \u2014 Strength',
    nav_l3:         'L3 \u2014 Power',
    nav_l4:         'L4 \u2014 Speed & Agility',
    nav_system:     'System',
    nav_admin:      'Admin Panel',
    nav_report:     'Report Center',
    nav_coach:      'Coach Management',
    brand_sub:      'High Performance Combat Sports',
    logout:         'Logout'
  }
};

function applyLang(lang) {
  var t = TRANSLATIONS[lang] || TRANSLATIONS['id'];
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });
  // Update tombol aktif
  var btnId = document.getElementById('btn_id');
  var btnEn = document.getElementById('btn_en');
  if (btnId && btnEn) {
    var activeStyle = 'background:rgba(239,68,68,0.3);border:1px solid rgba(239,68,68,0.6);color:#fff;border-radius:4px;padding:2px 7px;font-size:10px;cursor:pointer;font-weight:700;';
    var inactiveStyle = 'background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#9ca3af;border-radius:4px;padding:2px 7px;font-size:10px;cursor:pointer;font-weight:600;';
    btnId.style.cssText = lang === 'id' ? activeStyle : inactiveStyle;
    btnEn.style.cssText = lang === 'en' ? activeStyle : inactiveStyle;
  }
  document.documentElement.lang = lang;
}

function setLang(lang) {
  localStorage.setItem('hpcs_lang', lang);
  applyLang(lang);
}

// Auto apply saat halaman load
window.addEventListener('DOMContentLoaded', function() {
  var saved = localStorage.getItem('hpcs_lang') || 'id';
  applyLang(saved);
});
</script>'''

if 'TRANSLATIONS' not in c:
    c = c.replace('</body>', I18N_SCRIPT + '\n</body>')
    print('OK 3: script i18n ditambahkan')
else:
    print('SKIP 3: sudah ada')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
