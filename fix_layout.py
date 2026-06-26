path = r'templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('margin-left: 220px;', 'margin-left: 230px;\n      transition: margin-left .25s ease;')
print('OK 1: margin 230px')

old_js = "var mc = document.querySelector('.main-content');\n    sb.classList.toggle('collapsed');\n    if (mc) mc.classList.toggle('expanded');"
new_js = "var mw = document.querySelector('.main-wrapper');\n    sb.classList.toggle('collapsed');\n    if (mw) mw.style.marginLeft = sb.classList.contains('collapsed') ? '54px' : '230px';"

if old_js in c:
    c = c.replace(old_js, new_js)
    print('OK 2: toggle fix')
else:
    import re
    c = re.sub(
        r"var mc = document\.querySelector\('\.main-content'\);\s*sb\.classList\.toggle\('collapsed'\);\s*if \(mc\) mc\.classList\.toggle\('expanded'\);",
        "var mw = document.querySelector('.main-wrapper');\n    sb.classList.toggle('collapsed');\n    if (mw) mw.style.marginLeft = sb.classList.contains('collapsed') ? '54px' : '230px';",
        c
    )
    print('OK 2: toggle fix (regex)')

old_restore = "var mc = document.querySelector('.main-content');\n        if (sb) sb.classList.add('collapsed');\n        if (mc) mc.classList.add('expanded');"
new_restore = "var mw = document.querySelector('.main-wrapper');\n        if (sb) sb.classList.add('collapsed');\n        if (mw) mw.style.marginLeft = '54px';"

if old_restore in c:
    c = c.replace(old_restore, new_restore)
    print('OK 3: restore fix')
else:
    import re
    c = re.sub(
        r"var mc = document\.querySelector\('\.main-content'\);\s*if \(sb\) sb\.classList\.add\('collapsed'\);\s*if \(mc\) mc\.classList\.add\('expanded'\);",
        "var mw = document.querySelector('.main-wrapper');\n        if (sb) sb.classList.add('collapsed');\n        if (mw) mw.style.marginLeft = '54px';",
        c
    )
    print('OK 3: restore fix (regex)')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
