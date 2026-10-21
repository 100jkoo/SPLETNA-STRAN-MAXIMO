"""Build a slimmer copy of the site in dist/ for hosts with a size limit (Wix drop: 20 MB).
The big, repeated header/menu/drawer and footer are moved into one small script per language
(assets/inc/*.js) that writes them into every page while it loads.
Run after build.py:  python3 i18n/slim.py   ->  dist/ and maximo-tekstil-site.zip"""
import os, re, sys, json, shutil, glob, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
ALL = ['en'] + LANGS
OUT = os.path.join(ROOT, 'dist')
SKIP_ROOT = {'.git', '.claude', '.agents', 'i18n', 'dist'}
SKIP_FILES = {'README.md', 'skills-lock.json', 'maximo-tekstil-site.zip'}
URL = re.compile(r'\b(href|src|action|poster)="([^"]*)"')
ABS = ('#', 'http:', 'https:', 'mailto:', 'tel:', 'data:', 'javascript:', '//')

ACC = '<div class="mx-acc"><button type="button" aria-expanded="'

def open_index(block):
    parts = block.split(ACC)[1:]
    for i, x in enumerate(parts):
        if x.startswith('true'): return i
    return -1

TAG = re.compile(r'<(?:a|button)\b[^>]*>')

def current_marks(block):
    """Ordinals (among a/button tags outside the language lists) that carry aria-current."""
    b = re.sub(r'<ul class="mx-lang-m">.*?</ul>', '', block, flags=re.S)
    b = re.sub(r'(<nav class="mx-flang"[^>]*>).*?</nav>', r'\1</nav>', b, flags=re.S)
    out = []
    for i, m in enumerate(TAG.finditer(b)):
        c = re.search(r' aria-current="([^"]*)"', m.group(0))
        if c: out.append(f'{i}:{c.group(1)}')
    return ','.join(out)

def tokenise(block, p, q):
    def f(m):
        v = m.group(2)
        if not v or v.startswith(ABS) or v.startswith('/'): return m.group(0)
        if p == q: return f'{m.group(1)}="§P§{v[len(p):] if v.startswith(p) else v}"'
        if p and v.startswith(p): return f'{m.group(1)}="§P§{v[len(p):]}"'
        if q and v.startswith(q): v = v[len(q):]
        return f'{m.group(1)}="§Q§{v}"'
    block = URL.sub(f, block)
    block = re.sub(r'<ul class="mx-lang-m">.*?</ul>', '<ul class="mx-lang-m">§LANGLIST§</ul>', block, flags=re.S)
    block = re.sub(r'(<nav class="mx-flang"[^>]*>).*?</nav>', r'\1§FLANG§</nav>', block, flags=re.S)
    block = re.sub(r'<button type="button" class="mx-lang-b"([^>]*)><span>[A-Z]{2}</span>', r'<button type="button" class="mx-lang-b"\1><span>§CODE§</span>', block)
    block = re.sub(r' aria-current="(?:page|true)"', '', block)
    block = block.replace(ACC + 'true"', ACC + 'false"')
    return block

def find(node, cls, s):
    for k in node.kids:
        if k.tag == 'div':
            c = re.search(r'class="([^"]*)"', s[k.start:k.cs])
            if c and cls in c.group(1).split(): return k
    return None

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    # copy assets + html tree
    templates = {l: {'top': None, 'foot': None} for l in ALL}
    conflicts = []
    files = []
    for dp, dn, fn in os.walk(ROOT):
        rel_dir = os.path.relpath(dp, ROOT)
        top = rel_dir.split(os.sep)[0]
        if top in SKIP_ROOT: dn[:] = []; continue
        for f in fn:
            if rel_dir == '.' and f in SKIP_FILES: continue
            files.append(os.path.normpath(os.path.join(rel_dir, f)))
    for rel in files:
        src = os.path.join(ROOT, rel); dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not rel.endswith('.html') or os.path.basename(rel) == '404.html':
            shutil.copy2(src, dst); continue
        s = open(src, encoding='utf-8').read()
        parts = rel.split(os.sep)
        lang = parts[0] if parts[0] in LANGS else 'en'
        page = '/'.join(parts[1:] if lang != 'en' else parts)
        p = '../' * (len(parts) - 1)
        t = Tree(s)
        body = [n for n in t.root.kids[0].kids if n.tag == 'body'][0]
        hd = find(body, 'mx-hd', s); dr = find(body, 'mx-drawer', s); ft = find(body, 'mx-ft', s)
        scrim = find(body, 'mx-scrim', s)
        if not (hd and dr and ft and scrim):
            shutil.copy2(src, dst); print('no shared blocks', rel); continue
        top_block = s[hd.start:dr.end]; foot_block = s[ft.start:ft.end]
        q = '../' * (len(parts) - 2) if lang != 'en' else p
        tt = tokenise(top_block, p, q); tf = tokenise(foot_block, p, q)
        for key, val in (('top', tt), ('foot', tf)):
            cur = templates[lang][key]
            if cur is None: templates[lang][key] = val
            elif cur != val: conflicts.append((rel, key))
        tm = current_marks(top_block); fm = current_marks(foot_block)
        attrs = f'data-p="{p}" data-q="{q}" data-page="{page}" data-lang="{lang}" data-open="{open_index(top_block)}"'
        pre = p + 'assets/inc/'
        new = (s[:hd.start] + f'<script src="{pre}top.{lang}.js" {attrs} data-cur="{tm}"></script>' + s[dr.end:ft.start] +
               f'<script src="{pre}foot.{lang}.js" {attrs} data-cur="{fm}"></script>' + s[ft.end:])
        open(dst, 'w', encoding='utf-8').write(new)
    os.makedirs(os.path.join(OUT, 'assets/inc'), exist_ok=True)
    names = {'en': 'English', 'sl': 'Slovenščina', 'hr': 'Hrvatski', 'hu': 'Magyar', 'it': 'Italiano', 'de': 'Deutsch'}
    hl = {'en': 'en', 'sl': 'sl', 'hr': 'hr', 'hu': 'hu', 'it': 'it', 'de': 'de-AT'}
    runtime = '''(function(){var s=document.currentScript,P=s.getAttribute('data-p'),Q=s.getAttribute('data-q'),pg=s.getAttribute('data-page'),L=s.getAttribute('data-lang');
var N=%s,H=%s,ALL=%s;
function href(t){return P+(t==='en'?'':t+'/')+pg}
var list='',fl='';
ALL.forEach(function(t){var cur=t===L?' aria-current="true"':'';var a='<a href="'+href(t)+'" hreflang="'+H[t]+'" lang="'+H[t]+'"'+cur+'>'+N[t]+'</a>';list+='<li>'+a+'</li>';fl+=a});
var cur=(s.getAttribute('data-cur')||'').split(',').filter(Boolean);
if(cur.length){var mp={},i0=0;cur.forEach(function(c){var z=c.split(':');mp[z[0]]=z[1]});
T=T.replace(/<(?:a|button)\\b[^>]*>/g,function(m){var k=i0++;return mp[k]!==undefined?m.replace(/>$/,' aria-current="'+mp[k]+'">'):m})}
var h=T.split('§P§').join(P).split('§Q§').join(Q).split('§LANGLIST§').join(list).split('§FLANG§').join(fl).split('§CODE§').join(L.toUpperCase());
var o=parseInt(s.getAttribute('data-open')||'-1',10);if(o>=0){var A='<div class="mx-acc"><button type="button" aria-expanded="false"',x=h.split(A);if(x.length>o+1){h=x[0];for(var i=1;i<x.length;i++)h+=(i-1===o?A.replace('false','true'):A)+x[i]}}
document.write(h);
var cs=document.currentScript;})();
'''
    for l in ALL:
        for key in ('top', 'foot'):
            t = templates[l][key]
            js = 'var T=' + json.dumps(t, ensure_ascii=False) + ';\n' + runtime % (json.dumps(names, ensure_ascii=False), json.dumps(hl), json.dumps(ALL))
            if key == 'top':
                js += "(function(){var q=document.querySelectorAll('.mx-menu>.mx-item>a.mx-trig');})();\n"
            open(os.path.join(OUT, f'assets/inc/{key}.{l}.js'), 'w', encoding='utf-8').write(js)
    print('conflicts:', len(conflicts), conflicts[:5])
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(OUT) for f in fn)
    print('dist size MB', round(size / 1048576, 1))
    zp = os.path.join(ROOT, 'maximo-tekstil-site.zip')
    if os.path.exists(zp): os.remove(zp)
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for dp, _, fn in os.walk(OUT):
            for f in fn:
                full = os.path.join(dp, f); z.write(full, os.path.relpath(full, OUT))
    print('zip MB', round(os.path.getsize(zp) / 1048576, 1))

if __name__ == '__main__':
    main()
