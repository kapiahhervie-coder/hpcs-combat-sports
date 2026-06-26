content = open("templates/base.html", "r", encoding="utf-8").read()

old = """      <a href="{% url 'combat:dashboard_boxing' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}">
        <span class="nav-icon">&#127946;</span> <span class="nav-link-text">Boxing Division</span>
      </a>"""

new = """      <a href="{% url 'combat:dashboard_boxing' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}">
        <span class="nav-icon">&#127946;</span> <span class="nav-link-text">Boxing Division</span>
      </a>
      <a href="{% url 'combat:tambah_atlet' %}" class="nav-link {% if request.resolver_match.url_name == 'tambah_atlet' %}active{% endif %}">
        <span class="nav-icon">&#43;</span> <span class="nav-link-text">Tambah Atlet</span>
      </a>"""

if old in content:
    content = content.replace(old, new)
    open("templates/base.html", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
