content = open("templates/base.html", "r", encoding="utf-8").read()

old = """      <a href="{% url 'logout' %}" style="color:#ef4444;font-size:11px;text-decoration:none;" title="Logout"><span class="nav-link-text logout-link">&#9747; Logout</span></a>"""

new = """      <form method="post" action="{% url 'logout' %}" style="display:inline">
        {% csrf_token %}
        <button type="submit" style="background:none;border:none;color:#ef4444;font-size:11px;cursor:pointer;padding:0" title="Logout">
          <span class="nav-link-text logout-link">&#9747; Logout</span>
        </button>
      </form>"""

if old in content:
    content = content.replace(old, new)
    open("templates/base.html", "w", encoding="utf-8").write(content)
    print("Berhasil!")
else:
    print("Tidak ditemukan")
