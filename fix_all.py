content = open("combat/urls.py", "r", encoding="utf-8").read()

# Fix duplikat URL - cari semua kemunculan
import re
pattern = r"    path\('tambah-atlet/', views\.TambahAtletView\.as_view\(\), name='tambah_atlet'\),\r?\n"
matches = re.findall(pattern, content)
print(f"URL tambah_atlet ditemukan: {len(matches)} kali")
if len(matches) > 1:
    # Hapus semua lalu tambah satu
    content = re.sub(pattern, "", content)
    content = content.replace(
        "    path('admin-coach/assign/', views.AssignAtletCoachView.as_view(), name='assign_atlet_coach'),",
        "    path('admin-coach/assign/', views.AssignAtletCoachView.as_view(), name='assign_atlet_coach'),\n    path('tambah-atlet/', views.TambahAtletView.as_view(), name='tambah_atlet'),"
    )
    open("combat/urls.py", "w", encoding="utf-8").write(content)
    print("Duplikat URL diperbaiki!")

# Fix sidebar
content2 = open("templates/base.html", "r", encoding="utf-8").read()
old = """      <a href="{% url 'combat:dashboard_boxing' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}">
        <span class="nav-icon">&#127946;</span> <span class="nav-link-text" data-i18n="nav_boxing">Boxing Division</span>
      </a>"""

new = """      <a href="{% url 'combat:dashboard_boxing' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard_boxing' %}active{% endif %}">
        <span class="nav-icon">&#127946;</span> <span class="nav-link-text" data-i18n="nav_boxing">Boxing Division</span>
      </a>
      <a href="{% url 'combat:tambah_atlet' %}" class="nav-link {% if request.resolver_match.url_name == 'tambah_atlet' %}active{% endif %}">
        <span class="nav-icon">&#43;</span> <span class="nav-link-text">Tambah Atlet</span>
      </a>"""

if old in content2:
    content2 = content2.replace(old, new)
    open("templates/base.html", "w", encoding="utf-8").write(content2)
    print("Sidebar berhasil!")
else:
    print("Sidebar tidak ditemukan")
