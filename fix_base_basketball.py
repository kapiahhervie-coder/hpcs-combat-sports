with open("templates/base.html", encoding="utf-8") as f:
    content = f.read()

# Ganti sidebar untuk basketball
content = content.replace(
    "      <a href=\"{% url 'combat:tambah_atlet' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'tambah_atlet' %}active{% endif %}\">",
    "      <a href=\"{% url 'basketball:daftar_atlet' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'daftar_atlet' %}active{% endif %}\">"
)
content = content.replace(
    "      <a href=\"{% url 'combat:dashboard_boxing' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#127946;</span> <span class=\"nav-link-text\" data-i18n=\"nav_boxing\">Boxing Division</span>",
    "      <a href=\"{% url 'basketball:dashboard' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'dashboard' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#127936;</span> <span class=\"nav-link-text\">Basketball Division</span>"
)
content = content.replace(
    "      <a href=\"{% url 'combat:l1_correction' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'l1_correction' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#128308;</span> <span class=\"nav-link-text\" data-i18n=\"nav_l1\">L1 — Correction</span><span class=\"nav-badge\">MOB</span>",
    "      <a href=\"{% url 'basketball:l1_correction' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'l1_correction' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#128308;</span> <span class=\"nav-link-text\">L1 — Correction</span><span class=\"nav-badge\">MOB</span>"
)
content = content.replace(
    "      <a href=\"{% url 'combat:l2_strength' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'l2_strength' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#128309;</span> <span class=\"nav-link-text\" data-i18n=\"nav_l2\">L2 — Strength</span><span class=\"nav-badge\">STR</span>",
    "      <a href=\"{% url 'basketball:l2_strength' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'l2_strength' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#128309;</span> <span class=\"nav-link-text\">L2 — Strength</span><span class=\"nav-badge\">STR</span>"
)
content = content.replace(
    "      <a href=\"{% url 'combat:l3_power' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'l3_power' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#128992;</span> <span class=\"nav-link-text\" data-i18n=\"nav_l3\">L3 — Power</span><span class=\"nav-badge\">PWR</span>",
    "      <a href=\"{% url 'basketball:l3_power' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'l3_power' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#128992;</span> <span class=\"nav-link-text\">L3 — Power</span><span class=\"nav-badge\">PWR</span>"
)
content = content.replace(
    "      <a href=\"{% url 'combat:l4_speed_agility' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'l4_speed_agility' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#128993;</span> <span class=\"nav-link-text\" data-i18n=\"nav_l4\">L4 — Speed & Agility</span><span class=\"nav-badge\">SPD</span>",
    "      <a href=\"{% url 'basketball:l4_specific' %}\" class=\"nav-link {% if request.resolver_match.url_name == 'l4_specific' %}active{% endif %}\">\n        <span class=\"nav-icon\">&#128993;</span> <span class=\"nav-link-text\">L4 — Specific</span><span class=\"nav-badge\">BSK</span>"
)

# Ganti warna sidebar merah -> orange basketball
content = content.replace(
    "background:linear-gradient(180deg,#0f0f0f 0%,#1a0a00 100%);border-right:1px solid rgba(239,68,68,0.15)",
    "background:linear-gradient(180deg,#0f0f0f 0%,#1a0500 100%);border-right:1px solid rgba(249,115,22,0.15)"
)
content = content.replace("rgba(239,68,68,0.15);background:rgba(239,68,68,0.05)", "rgba(249,115,22,0.15);background:rgba(249,115,22,0.05)")
content = content.replace("rgba(239,68,68,0.08);color:#f9fafb;border-left-color:rgba(239,68,68,0.4)", "rgba(249,115,22,0.08);color:#f9fafb;border-left-color:rgba(249,115,22,0.4)")
content = content.replace("rgba(239,68,68,0.12);color:#fff;border-left-color:#ef4444", "rgba(249,115,22,0.12);color:#fff;border-left-color:#f97316")
content = content.replace("background:rgba(239,68,68,0.2);color:#ef4444", "background:rgba(249,115,22,0.2);color:#f97316")
content = content.replace("border-top:1px solid rgba(239,68,68,0.1)", "border-top:1px solid rgba(249,115,22,0.1)")
content = content.replace("background:#ef4444;border-radius:50%", "background:#f97316;border-radius:50%")
content = content.replace("color:#ef4444;font-size:11px", "color:#f97316;font-size:11px")
content = content.replace(
    "<div class=\"brand-sub\" data-i18n=\"brand_sub\">High Performance Combat Sports</div>",
    "<div class=\"brand-sub\">Basketball Division</div>"
)

with open("basketball/templates/basketball/base_basketball.html", "w", encoding="utf-8") as f:
    f.write(content)
print("OK: base_basketball.html berhasil dibuat!")
