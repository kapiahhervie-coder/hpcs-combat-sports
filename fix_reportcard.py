content = open("combat/templates/combat/dashboard_boxing.html", "r", encoding="utf-8").read()

old = """                <a href="{% url 'combat:report_card' atlet.pk %}"
                   target="_blank" class="btn-report">
                    \U0001f4cb Report Card
                </a>"""

new = """                {% if atlet %}
                <a href="{% url 'combat:report_card' atlet.pk %}"
                   target="_blank" class="btn-report">
                    \U0001f4cb Report Card
                </a>
                {% else %}
                <span class="btn-report" style="opacity:0.4;cursor:not-allowed;">\U0001f4cb Report Card</span>
                {% endif %}"""

if old in content:
    content = content.replace(old, new)
    open("combat/templates/combat/dashboard_boxing.html", "w", encoding="utf-8").write(content)
    print("Berhasil diganti!")
else:
    print("Teks tidak ditemukan - cek whitespace")
