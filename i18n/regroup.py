"""One-off: move FLORJAN 285 and FR-10 360 from '100% Cotton' to their own 'Flame retardant (Proban®)' group (English sources)."""
import re, glob, os
NAME = 'Flame retardant (Proban®)'
SLUGS = ('florjan-285.html', 'fr-10-360.html')
n = 0
for f in sorted(glob.glob('**/*.html', recursive=True)):
    if f.split('/')[0] in ('sl', 'hr', 'hu', 'it', 'de', 'dist', 'i18n'): continue
    s = open(f, encoding='utf-8').read(); o = s
    if 'g=fr"' in s and 'mx-fcol' in s and NAME in s and f != 'on-stock/index.html' and 'data-group="fr"' not in s:
        pass
    # 1. mega menu group
    m = re.search(r'<div class="mx-grp"><a class="mx-gh" href="([^"]*)#g=cotton">100% Cotton<i>8</i></a><ul class="mx-ul">(.*?)</ul></div>', s, re.S)
    if m:
        lis = re.findall(r'<li>.*?</li>', m.group(2), re.S)
        mv = [x for x in lis if any(sl in x for sl in SLUGS)]; keep = [x for x in lis if x not in mv]
        new = (f'<div class="mx-grp"><a class="mx-gh" href="{m.group(1)}#g=cotton">100% Cotton<i>{len(keep)}</i></a><ul class="mx-ul">{"".join(keep)}</ul></div>'
               f'<div class="mx-grp"><a class="mx-gh" href="{m.group(1)}#g=fr">{NAME}<i>{len(mv)}</i></a><ul class="mx-ul">{"".join(mv)}</ul></div>')
        s = s.replace(m.group(0), new)
    # 2. drawer chips
    m = re.search(r'<a class="mx-gh" href="([^"]*)#g=cotton">100% Cotton<i>8</i></a><div class="mx-chips">(.*?)</div>', s, re.S)
    if m:
        chips = re.findall(r'<a href="[^"]*">.*?</a>', m.group(2), re.S)
        mv = [x for x in chips if any(sl in x for sl in SLUGS)]; keep = [x for x in chips if x not in mv]
        new = (f'<a class="mx-gh" href="{m.group(1)}#g=cotton">100% Cotton<i>{len(keep)}</i></a><div class="mx-chips">{"".join(keep)}</div>'
               f'<a class="mx-gh" href="{m.group(1)}#g=fr">{NAME}<i>{len(mv)}</i></a><div class="mx-chips">{"".join(mv)}</div>')
        s = s.replace(m.group(0), new)
    # 3. footer link
    s = re.sub(r'(<a href="([^"]*)#g=cotton">100% Cotton</a>)', lambda mm: mm.group(1) + f'<a href="{mm.group(2)}#g=fr">{NAME}</a>', s, count=1)
    if s != o: open(f, 'w', encoding='utf-8').write(s); n += 1
print('menu/footer updated in', n, 'files')
