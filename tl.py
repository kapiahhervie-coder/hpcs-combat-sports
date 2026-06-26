path = r'combat\templates\combat\l1_correction.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
links = {
    'Seated Rotation Test': 'https://www.youtube.com/watch?v=Xh25uxFkU-k',
    'Lumbar Extension Test': 'https://www.youtube.com/watch?v=2OyQGH9vzok',
    'Single Leg Balance': 'https://www.youtube.com/watch?v=Y0jR3GZDVnk',
    'Knee-to-Wall Test': 'https://www.youtube.com/watch?v=Clutk_VsgUY',
    'Pola Istirahat': 'https://www.youtube.com/watch?v=0Ua9bOsZTYg',
    'Saat Tekanan': 'https://www.youtube.com/watch?v=0Ua9bOsZTYg',
}
s='color:inherit;text-decoration:underline dotted;cursor:pointer;opacity:0.9;'
for nama,url in links.items():
    old=f'>{nama}<'
    new=f'><a href="{url}" target="_blank" style="{s}">{nama} <span style="font-size:9px;opacity:0.6;">&#9654;</span></a><'
    if old in c:
        c=c.replace(old,new,1); print(f'OK: {nama}')
    else:
        print(f'SKIP: {nama}')
with open(path,'w',encoding='utf-8') as f:
    f.write(c)
print('DONE')
