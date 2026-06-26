path = r'templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

aside_start = c.find('<aside class="sidebar">')
aside_end = c.find('</aside>', aside_start) + 8

NEW_CSS = '''
    .sidebar{position:fixed;top:0;left:0;width:230px;height:100vh;background:linear-gradient(180deg,#0f0f0f 0%,#1a0a00 100%);border-right:1px solid rgba(239,68,68,0.15);display:flex;flex-direction:column;z-index:100;}
    .sidebar-brand{padding:18px 20px 16px;border-bottom:1px solid rgba(239,68,68,0.15);background:rgba(239,68,68,0.05);}
    .sidebar-brand .brand-name{font-size:17px;font-weight:800;color:#fff;letter-spacing:2px;text-transform:uppercase;}
    .sidebar-brand .brand-name span{color:#ef4444;}
    .sidebar-brand .brand-sub{font-size:9px;color:#6b7280;text-transform:uppercase;letter-spacing:2px;margin-top:3px;}
    .sidebar-nav{flex:1;padding:10px 0;overflow-y:auto;}
    .nav-section{padding:12px 16px 4px;font-size:9px;font-weight:700;color:#4b5563;text-transform:uppercase;letter-spacing:1.5px;}
    .nav-link{display:flex;align-items:center;gap:10px;padding:9px 18px;color:#9ca3af;text-decoration:none;font-size:12.5px;font-weight:500;transition:all .15s;border-left:3px solid transparent;}
    .nav-link:hover{background:rgba(239,68,68,0.08);color:#f9fafb;border-left-color:rgba(239,68,68,0.4);}
    .nav-link.active{background:rgba(239,68,68,0.12);color:#fff;border-left-color:#ef4444;font-weight:600;}
    .nav-link .nav-icon{font-size:15px;width:20px;text-align:center;flex-shrink:0;}
    .nav-link .nav-badge{margin-left:auto;font-size:9px;padding:1px 6px;border-radius:10px;background:rgba(239,68,68,0.2);color:#ef4444;font-weight:700;}
    .nav-divider{height:1px;background:rgba(255,255,255,0.05);margin:8px 16px;}
    .sidebar-footer{padding:14px 20px;border-top:1px solid rgba(239,68,68,0.1);font-size:12px;color:#6b7280;display:flex;justify-content:space-between;align-items:center;}
    .sidebar-footer .user-name{font-weight:600;color:#9ca3af;}
'''

NEW_HTML = '''  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-name">&#9889; <span>HPCS</span></div>
      <div class="brand-sub">High Performance Combat Sports</div>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section">Dashboard</div>
      <a href="{% url 'combat:dashboard_boxing' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}">
        <span class="nav-icon">&#127946;</span> Boxing Division
      </a>
      <div class="nav-divider"></div>
      <div class="nav-section">Assessment</div>
      <a href="{% url 'combat:l1_correction' %}" class="nav-link {% if request.resolver_match.url_name == 'l1_correction' %}active{% endif %}">
        <span class="nav-icon">&#128308;</span> L1 — Correction<span class="nav-badge">MOB</span>
      </a>
      <a href="{% url 'combat:l2_strength' %}" class="nav-link {% if request.resolver_match.url_name == 'l2_strength' %}active{% endif %}">
        <span class="nav-icon">&#128309;</span> L2 — Strength<span class="nav-badge">STR</span>
      </a>
      <a href="{% url 'combat:l3_power' %}" class="nav-link {% if request.resolver_match.url_name == 'l3_power' %}active{% endif %}">
        <span class="nav-icon">&#128992;</span> L3 — Power<span class="nav-badge">PWR</span>
      </a>
      <a href="{% url 'combat:l4_speed_agility' %}" class="nav-link {% if request.resolver_match.url_name == 'l4_speed_agility' %}active{% endif %}">
        <span class="nav-icon">&#128993;</span> L4 — Speed & Agility<span class="nav-badge">SPD</span>
      </a>
      <div class="nav-divider"></div>
      <div class="nav-section">Laporan</div>
      <a href="{% url 'combat:report_center' %}" class="nav-link {% if request.resolver_match.url_name == 'report_center' %}active{% endif %}">
        <span class="nav-icon">&#128203;</span> Report Center
      </a>
      <div class="nav-divider"></div>
      <div class="nav-section">Sistem</div>
      <a href="{% url 'admin:index' %}" class="nav-link">
        <span class="nav-icon">&#9881;</span> Admin Panel
      </a>
    </nav>
    <div class="sidebar-footer">
      <span class="user-name">{{ request.user.username }}</span>
      <a href="{% url 'logout' %}" style="color:#ef4444;font-size:11px;text-decoration:none;">&#9747; Logout</a>
    </div>
  </aside>'''

if aside_start > 0:
    c = c[:aside_start] + NEW_HTML + c[aside_end:]
    print('OK HTML')
else:
    print('SKIP HTML')

# Tambah CSS baru sebelum </style> pertama
c = c.replace('</style>', NEW_CSS + '\n</style>', 1)
print('OK CSS')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
