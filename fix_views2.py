path = r'combat\views.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = """                score_rotation      = float(request.POST.get('score_rotation', 0)),
                score_extension     = float(request.POST.get('score_extension', 0)),
                score_stability     = float(request.POST.get('score_stability', 0)),
                score_posture       = float(request.POST.get('score_posture', 0)),
                score_breathing     = float(request.POST.get('score_breathing', 0)),"""

new = """                score_rotation      = round((float(request.POST.get('score_rotation', 0) or 0) + float(request.POST.get('score_rotation_r', 0) or 0)) / 2, 2),
                score_extension     = float(request.POST.get('score_extension', 0) or 0),
                score_stability     = round((float(request.POST.get('score_stability', 0) or 0) + float(request.POST.get('score_stability_r', 0) or 0)) / 2, 2),
                score_posture       = float(request.POST.get('score_posture', 0) or 0),
                score_breathing     = float(request.POST.get('score_breathing', 0) or 0),"""

if old in c:
    c = c.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('DONE - views.py berhasil diperbaiki')
else:
    print('TIDAK DITEMUKAN - paste isi views.py baris 174-178')
