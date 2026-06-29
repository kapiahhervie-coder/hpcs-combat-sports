import os
files = [
    "muaythai/templates/muaythai/l1_correction.html",
    "muaythai/templates/muaythai/l2_strength.html",
    "muaythai/templates/muaythai/l3_power.html",
    "muaythai/templates/muaythai/l4_speed_agility.html",
    "muaythai/templates/muaythai/report_card.html",
]
for f in files:
    if not os.path.exists(f):
        print("SKIP:", f)
        continue
    with open(f, encoding="utf-8") as fh:
        t = fh.read()
    before = t
    t = t.replace('{% extends "base.html" %}', '{% extends "base_muaythai.html" %}')
    t = t.replace("{% extends 'base.html' %}", "{% extends 'base_muaythai.html' %}")
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(t)
    status = "FIXED" if t != before else "no change"
    print(status + ":", f)
print("Done!")
