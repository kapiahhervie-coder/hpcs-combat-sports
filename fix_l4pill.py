path = r'combat\templates\combat\report_card.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Fix level-scores grid dan pill sizing
c = c.replace(
    '.level-scores { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 16px; }',
    '.level-scores { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 16px; }'
)
c = c.replace(
    '.level-pill { padding: 10px 6px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.06); }',
    '.level-pill { padding: 8px 4px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }'
)
c = c.replace(
    '.lp-score { font-size: 17px; font-weight: 800; font-family: "DM Mono", monospace; line-height: 1; display: block; }',
    '.lp-score { font-size: 15px; font-weight: 800; font-family: "DM Mono", monospace; line-height: 1; display: block; }'
)
c = c.replace(
    '.lp-pred { font-size: 6px; font-weight: 700; letter-spacing: 0.5px; display: block; margin-top: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }',
    '.lp-pred { font-size: 6px; font-weight: 700; letter-spacing: 0; display: block; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 100%; }'
)
# Juga fix card-premium width agar tidak overflow
c = c.replace(
    '<div class="card-premium" style="padding:24px;display:flex;flex-direction:column;justify-content:space-between;">',
    '<div class="card-premium" style="padding:24px;display:flex;flex-direction:column;justify-content:space-between;min-width:0;overflow:hidden;">'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE')
