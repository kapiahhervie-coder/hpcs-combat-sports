content = open("combat/templates/combat/tambah_atlet.html", "r", encoding="utf-8").read()

idx = 0
i = 0
while True:
    idx = content.find('name="tahap_ltad"', idx)
    if idx == -1:
        break
    i += 1
    print(f"=== Kemunculan {i} (pos {idx}) ===")
    print(repr(content[max(0,idx-150):idx+100]))
    print()
    idx += 1
