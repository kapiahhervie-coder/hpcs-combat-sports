content = open("templates/base.html", "r", encoding="utf-8").read()

old = """      <a href="{% url 'admin:index' %}" class="nav-link">
        <span class="nav-icon">&#9881;</span> <span class="nav-link-text">Admin Panel</span>
      </a>
    </nav>"""

new = """      <a href="{% url 'admin:index' %}" class="nav-link">
        <span class="nav-icon">&#9881;</span> <span class="nav-link-text">Admin Panel</span>
      </a>
      {% if request.user.is_superuser or request.user.is_staff %}
      <a href="{% url 'combat:admin_coach' %}" class="nav-link {% if request.resolver_match.url_name == 'admin_coach' %}active{% endif %}">
        <span class="nav-icon">&#128101;</span> <span class="nav-link-text">Manajemen Coach</span>
      </a>
      {% endif %}
    </nav>"""

if old in content:
    content = content.replace(old, new)
    open("templates/base.html", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
