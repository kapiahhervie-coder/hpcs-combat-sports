path = r'combat\views.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = 'class L2StrengthView(LoginRequiredMixin, View):\n    template_name'
new = 'class L2StrengthView(LoginRequiredMixin, View):\n    template_name'

# Cari def post di L2
idx = c.find('class L2StrengthView')
post_idx = c.find('def post(self, request):', idx)
old2 = c[post_idx:post_idx+50]
new2 = 'def post(self, request):\n        print("L2 POST:", dict(request.POST))\n        '
c = c.replace(old2, new2 + old2[25:])
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
