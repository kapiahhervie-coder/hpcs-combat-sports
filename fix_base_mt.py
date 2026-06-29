content = open("templates/base.html", encoding="utf-8").read()

# Ganti warna sidebar: merah Boxing -> biru/cyan Muay Thai
content = content.replace(
    "background:linear-gradient(180deg,#0f0f0f 0%,#1a0a00 100%);border-right:1px solid rgba(239,68,68,0.15)",
    "background:linear-gradient(180deg,#0a0f1a 0%,#001a2e 100%);border-right:1px solid rgba(56,189,248,0.15)"
)
content = content.replace("rgba(239,68,68,0.15);background:rgba(239,68,68,0.05)", "rgba(56,189,248,0.15);background:rgba(56,189,248,0.05)")
content = content.replace("rgba(239,68,68,0.08);color:#f9fafb;border-left-color:rgba(239,68,68,0.4)", "rgba(56,189,248,0.08);color:#f9fafb;border-left-color:rgba(56,189,248,0.4)")
content = content.replace("rgba(239,68,68,0.12);color:#fff;border-left-color:#ef4444", "rgba(56,189,248,0.12);color:#fff;border-left-color:#38bdf8")
content = content.replace("background:rgba(239,68,68,0.2);color:#ef4444", "background:rgba(56,189,248,0.2);color:#38bdf8")
content = content.replace("border-top:1px solid rgba(239,68,68,0.1)", "border-top:1px solid rgba(56,189,248,0.1)")
content = content.replace("background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3)", "background:rgba(56,189,248,0.15);border:1px solid rgba(56,189,248,0.3)")
content = content.replace("background:#ef4444;border-radius:50%", "background:#38bdf8;border-radius:50%")
content = content.replace("border:2px solid #0f0f0f", "border:2px solid #0a0f1a")
content = content.replace("color:#ef4444;font-size:11px", "color:#38bdf8;font-size:11px")

# Ganti sidebar navigation - Boxing -> Muay Thai
old_nav = """      <a href="{% url 'combat:dashboard_boxing' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}">
        <span class="nav-icon">&#127946;</span> <span class="nav-link-text" data-i18n="nav_boxing">Boxing Division</span>
      </a>
      <a href="{% url 'combat:tambah_atlet' %}" class="nav-link {% if request.resolver_match.url_name == 'tambah_atlet' %}active{% endif %}">
        <span class="nav-icon">&#43;</span> <span class="nav-link-text">Tambah Atlet</span>
      </a>
      <div class="nav-divider"></div>
      <div class="nav-section" data-i18n="nav_assessment">Assessment</div>
      <a href="{% url 'combat:l1_correction' %}" class="nav-link {% if request.resolver_match.url_name == 'l1_correction' %}active{% endif %}">
        <span class="nav-icon">&#128308;</span> <span class="nav-link-text" data-i18n="nav_l1">L1 — Correction</span><span class="nav-badge">MOB</span>
      </a>
      <a href="{% url 'combat:l2_strength' %}" class="nav-link {% if request.resolver_match.url_name == 'l2_strength' %}active{% endif %}">
        <span class="nav-icon">&#128309;</span> <span class="nav-link-text" data-i18n="nav_l2">L2 — Strength</span><span class="nav-badge">STR</span>
      </a>
      <a href="{% url 'combat:l3_power' %}" class="nav-link {% if request.resolver_match.url_name == 'l3_power' %}active{% endif %}">
        <span class="nav-icon">&#128992;</span> <span class="nav-link-text" data-i18n="nav_l3">L3 — Power</span><span class="nav-badge">PWR</span>
      </a>
      <a href="{% url 'combat:l4_speed_agility' %}" class="nav-link {% if request.resolver_match.url_name == 'l4_speed_agility' %}active{% endif %}">
        <span class="nav-icon">&#128993;</span> <span class="nav-link-text" data-i18n="nav_l4">L4 — Speed & Agility</span><span class="nav-badge">SPD</span>
      </a>"""

new_nav = """      <a href="{% url 'muaythai:dashboard' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}">
        <span class="nav-icon">&#127981;</span> <span class="nav-link-text">Muay Thai Division</span>
      </a>
      <a href="{% url 'combat:tambah_atlet' %}" class="nav-link {% if request.resolver_match.url_name == 'tambah_atlet' %}active{% endif %}">
        <span class="nav-icon">&#43;</span> <span class="nav-link-text">Tambah Atlet</span>
      </a>
      <div class="nav-divider"></div>
      <div class="nav-section">Assessment Muay Thai</div>
      <a href="{% url 'muaythai:l1_correction' %}" class="nav-link {% if request.resolver_match.url_name == 'l1_correction' %}active{% endif %}">
        <span class="nav-icon">&#128308;</span> <span class="nav-link-text">L1 — Correction</span><span class="nav-badge">MOB</span>
      </a>
      <a href="{% url 'muaythai:l2_strength' %}" class="nav-link {% if request.resolver_match.url_name == 'l2_strength' %}active{% endif %}">
        <span class="nav-icon">&#128309;</span> <span class="nav-link-text">L2 — Strength</span><span class="nav-badge">STR</span>
      </a>
      <a href="{% url 'muaythai:l3_power' %}" class="nav-link {% if request.resolver_match.url_name == 'l3_power' %}active{% endif %}">
        <span class="nav-icon">&#128992;</span> <span class="nav-link-text">L3 — Power</span><span class="nav-badge">PWR</span>
      </a>
      <a href="{% url 'muaythai:l4_speed_agility' %}" class="nav-link {% if request.resolver_match.url_name == 'l4_speed_agility' %}active{% endif %}">
        <span class="nav-icon">&#128993;</span> <span class="nav-link-text">L4 — Speed & Agility</span><span class="nav-badge">SPD</span>
      </a>"""

content = content.replace(old_nav, new_nav)

# Ganti brand sub
content = content.replace(
    '<div class="brand-sub" data-i18n="brand_sub">High Performance Combat Sports</div>',
    '<div class="brand-sub">Muay Thai Division</div>'
)

# Ganti title default
content = content.replace(
    "{% block title %}HPCS Combat Sports{% endblock %}",
    "{% block title %}HPCS Muay Thai{% endblock %}"
)

# Ganti warna logout
content = content.replace(
    "background:none;border:none;color:#ef4444;font-size:11px",
    "background:none;border:none;color:#38bdf8;font-size:11px"
)

open("templates/base_muaythai.html", "w", encoding="utf-8").write(content)
print("OK: templates/base_muaythai.html dibuat!")
