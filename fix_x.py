path = r'templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# FIX 1: Sembunyikan teks Logout saat collapsed, ganti icon
old_logout = '      <a href="{% url \'logout\' %}" style="color:#ef4444;font-size:11px;text-decoration:none;">&#9747; Logout</a>'
new_logout = '      <a href="{% url \'logout\' %}" style="color:#ef4444;font-size:11px;text-decoration:none;" title="Logout"><span class="nav-link-text logout-link">&#9747; Logout</span><span class="logout-icon" style="font-size:14px;">&#9747;</span></a>'

if old_logout in c:
    c = c.replace(old_logout, new_logout)
    print('OK 1: logout diupdate')

# Sembunyikan icon saat tidak collapsed, tampilkan teks saat normal
LOGOUT_CSS = '''
    .logout-icon { display: none; }
    .sidebar.collapsed .logout-link { display: none !important; }
    .sidebar.collapsed .logout-icon { display: inline !important; }
    .sidebar.collapsed .user-name { display: none !important; }
'''
c = c.replace('</style>', LOGOUT_CSS + '\n</style>', 1)
print('OK 2: CSS logout ditambahkan')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE base.html')
