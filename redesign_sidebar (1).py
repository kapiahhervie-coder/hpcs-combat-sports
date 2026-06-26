path = r'templates\base.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# ── 1. Ganti CSS sidebar ──────────────────────────────────────
OLD_CSS = '''    /* â"€â"€ Sidebar â"€â"€ */
    .sidebar {
      position: fixed;
      top: 0; left: 0;
      width: 220px;
      height: 100vh;
      background: #111827;
      display: flex;
      flex-direction: column;
      z-index: 100;
    }

    .sidebar-brand {
      padding: 20px 20px 16px;
      border-bottom: 0.5px solid rgba(255,255,255,.1);
    }
    .sidebar-brand .brand-name {
      font-size: 15px;
      font-weight: 600;
      color: #fff;
      letter-spacing: .3px;
    }
    .sidebar-brand .brand-sub {
      font-size: 10px;
      color: #9ca3af;
      text-transform: uppercase;
      letter-spacing: .8px;
      margin-top: 2px;
    }

    .sidebar-nav {
      flex: 1;
      padding: 12px 0;
      overflow-y: auto;
    }

    .nav-section {
      padding: 8px 16px 4px;
      font-size: 10px;
      font-weight: 500;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: .8px;
    }

    .nav-link {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 9px 20px;
      color: #d1d5db;
      text-decoration: none;
      font-size: 13px;
      font-weight: 400;
      transition: background .15s, color .15s;
      border-left: 3px solid transparent;
    }
    .nav-link:hover {
      background: rgba(255,255,255,.06);
      color: #fff;
    }
    .nav-link.active {
      background: rgba(255,255,255,.08);
      color: #fff;
      border-left-color: #3b82f6;
      font-weight: 500;
    }
    .nav-link .nav-icon {
      font-size: 16px;
      width: 18px;
      text-align: center;
      opacity: .8;
    }'''

NEW_CSS = '''    /* ── Sidebar Redesign — Combat Sports Theme ── */
    .sidebar {
      position: fixed;
      top: 0; left: 0;
      width: 230px;
      height: 100vh;
      background: linear-gradient(180deg, #0f0f0f 0%, #1a0a00 100%);
      border-right: 1px solid rgba(239,68,68,0.15);
      display: flex;
      flex-direction: column;
      z-index: 100;
    }

    .sidebar-brand {
      padding: 18px 20px 16px;
      border-bottom: 1px solid rgba(239,68,68,0.15);
      background: rgba(239,68,68,0.05);
    }
    .sidebar-brand .brand-name {
      font-size: 17px;
      font-weight: 800;
      color: #fff;
      letter-spacing: 2px;
      text-transform: uppercase;
    }
    .sidebar-brand .brand-name span {
      color: #ef4444;
    }
    .sidebar-brand .brand-sub {
      font-size: 9px;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 2px;
      margin-top: 3px;
    }

    .sidebar-nav {
      flex: 1;
      padding: 10px 0;
      overflow-y: auto;
    }
    .sidebar-nav::-webkit-scrollbar { width: 3px; }
    .sidebar-nav::-webkit-scrollbar-track { background: transparent; }
    .sidebar-nav::-webkit-scrollbar-thumb { background: rgba(239,68,68,0.3); border-radius: 2px; }

    .nav-section {
      padding: 12px 16px 4px;
      font-size: 9px;
      font-weight: 700;
      color: #4b5563;
      text-transform: uppercase;
      letter-spacing: 1.5px;
    }

    .nav-link {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 9px 18px;
      color: #9ca3af;
      text-decoration: none;
      font-size: 12.5px;
      font-weight: 500;
      transition: all .15s;
      border-left: 3px solid transparent;
      position: relative;
    }
    .nav-link:hover {
      background: rgba(239,68,68,0.08);
      color: #f9fafb;
      border-left-color: rgba(239,68,68,0.4);
    }
    .nav-link.active {
      background: rgba(239,68,68,0.12);
      color: #fff;
      border-left-color: #ef4444;
      font-weight: 600;
    }
    .nav-link .nav-icon {
      font-size: 15px;
      width: 20px;
      text-align: center;
      flex-shrink: 0;
    }
    .nav-link .nav-badge {
      margin-left: auto;
      font-size: 9px;
      padding: 1px 6px;
      border-radius: 10px;
      background: rgba(239,68,68,0.2);
      color: #ef4444;
      font-weight: 700;
      letter-spacing: .5px;
    }
    .nav-divider {
      height: 1px;
      background: rgba(255,255,255,0.05);
      margin: 8px 16px;
    }'''

if '/* â"€â"€ Sidebar â"€â"€ */' in c or '.sidebar {' in c:
    # Cari blok CSS sidebar
    start = c.find('/* â"€â"€ Sidebar â"€â"€ */')
    if start == -1:
        start = c.find('/* ── Sidebar ──')
    if start == -1:
        start = c.find('.sidebar {')
        start = c.rfind('\n', 0, start) + 1
    
    end = c.find('.nav-link .nav-icon {', start)
    end = c.find('}', end) + 1
    
    old_block = c[start:end]
    c = c.replace(old_block, NEW_CSS)
    print('OK 1: CSS sidebar diganti')
else:
    print('SKIP 1: CSS sidebar tidak ditemukan')

# ── 2. Ganti HTML sidebar ─────────────────────────────────────
OLD_HTML = '''  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-name">âš" HPCS</div>
      <div class="brand-sub">Combat Sports</div>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section">Dashboard</div>
      <a href="{% url 'combat:dashboard_combat' %}"
         class="nav-link {% if request.resolver_match.url_name == 'dashboard_combat' %}active{% endif %}">
        <span class="nav-icon">â—ˆ</span> Sport Combat
      </a>
      <a href="{% url 'combat:dashboard_boxing' %}"
         class="nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}">
        <span class="nav-icon">â—‰</span> Boxing
      </a>
      <div class="nav-section" style="margin-top:8px;">Manajemen</div>
      <a href="#" class="nav-link">
        <span class="nav-icon">â—·</span> Atlet
      </a>
      <a href="#" class="nav-link">
        <span class="nav-icon">â—'</span> Audit
      </a>
      <a href="#" class="nav-link">
        <span class="nav-icon">â—PS D:\LIBRERY\Phyton\HPCS Combat Sports>'''

# Cari HTML sidebar dari <aside sampai </aside>
aside_start = c.find('<aside class="sidebar">')
aside_end = c.find('</aside>', aside_start) + 8

if aside_start > 0:
    NEW_HTML = '''  <aside class="sidebar">

    <!-- Brand -->
    <div class="sidebar-brand">
      <div class="brand-name">&#9889; <span>HPCS</span></div>
      <div class="brand-sub">High Performance Combat Sports</div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">

      <!-- Dashboard -->
      <div class="nav-section">Dashboard</div>
      <a href="{% url 'combat:dashboard_boxing' %}"
         class="nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}">
        <span class="nav-icon">&#127946;</span> Boxing Division
      </a>

      <div class="nav-divider"></div>

      <!-- Assessment Levels -->
      <div class="nav-section">Assessment</div>
      <a href="{% url 'combat:l1_correction' %}"
         class="nav-link {% if request.resolver_match.url_name == 'l1_correction' %}active{% endif %}">
        <span class="nav-icon">&#128308;</span> L1 — Correction
        <span class="nav-badge">MOB</span>
      </a>
      <a href="{% url 'combat:l2_strength' %}"
         class="nav-link {% if request.resolver_match.url_name == 'l2_strength' %}active{% endif %}">
        <span class="nav-icon">&#128309;</span> L2 — Strength
        <span class="nav-badge">STR</span>
      </a>
      <a href="{% url 'combat:l3_power' %}"
         class="nav-link {% if request.resolver_match.url_name == 'l3_power' %}active{% endif %}">
        <span class="nav-icon">&#128992;</span> L3 — Power
        <span class="nav-badge">PWR</span>
      </a>
      <a href="{% url 'combat:l4_speed_agility' %}"
         class="nav-link {% if request.resolver_match.url_name == 'l4_speed_agility' %}active{% endif %}">
        <span class="nav-icon">&#128993;</span> L4 — Speed & Agility
        <span class="nav-badge">SPD</span>
      </a>

      <div class="nav-divider"></div>

      <!-- Laporan -->
      <div class="nav-section">Laporan</div>
      <a href="{% url 'combat:report_center' %}"
         class="nav-link {% if request.resolver_match.url_name == 'report_center' %}active{% endif %}">
        <span class="nav-icon">&#128203;</span> Report Center
      </a>

      <div class="nav-divider"></div>

      <!-- Sistem -->
      <div class="nav-section">Sistem</div>
      <a href="{% url 'admin:index' %}" class="nav-link">
        <span class="nav-icon">&#9881;</span> Admin Panel
      </a>

    </nav>

    <!-- Footer user info -->
    <div class="sidebar-footer">
      <div class="user-name">{{ request.user.username }}</div>
      <a href="{% url 'logout' %}" style="color:#ef4444;font-size:11px;text-decoration:none;">
        &#9747; Logout
      </a>
    </div>

  </aside>'''

    c = c[:aside_start] + NEW_HTML + c[aside_end:]
    print('OK 2: HTML sidebar diganti')
else:
    print('SKIP 2: aside tidak ditemukan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
