"""Build translated copies of the site: python3 i18n/build.py
English pages at the repository root are the master; translated copies go to sl/ hr/ hu/ it/ de/.
Also syncs the language switcher + hreflang/canonical blocks into the English pages."""
import re, os, sys, json, glob, html, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from extract import source_pages, ATTR_RE, META_RE, TITLE_RE

SITE = 'https://www.maximo-tekstil.com'
ALL = ['en'] + LANGS
NAMES = {'en': 'English', 'sl': 'Slovenščina', 'hr': 'Hrvatski', 'hu': 'Magyar', 'it': 'Italiano', 'de': 'Deutsch'}
OGLOC = {'en': 'en_GB', 'sl': 'sl_SI', 'hr': 'hr_HR', 'hu': 'hu_HU', 'it': 'it_IT', 'de': 'de_AT'}
HTMLLANG = {'en': 'en', 'sl': 'sl', 'hr': 'hr', 'hu': 'hu', 'it': 'it', 'de': 'de-AT'}
CHEV = '<svg class="mx-chev" viewBox="0 0 10 10" aria-hidden="true"><path d="M1.5 3.5 5 7l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def load(l):
    p = os.path.join(ROOT, 'i18n/translations', l + '.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}

def rel_to(page, cur, target):
    d = page.count('/')
    up = '../' * (d + (0 if cur == 'en' else 1))
    return up + ('' if target == 'en' else target + '/') + page

def abs_url(page, lang):
    p = '' if page == 'index.html' else page
    return SITE + '/' + ('' if lang == 'en' else lang + '/') + p

def switcher(page, cur):
    items = ''.join(f'<li><a href="{rel_to(page, cur, t)}" hreflang="{HTMLLANG[t]}" lang="{HTMLLANG[t]}"{" aria-current=\"true\"" if t == cur else ""}>{NAMES[t]}</a></li>' for t in ALL)
    head = (f'<div class="mx-lang"><button type="button" class="mx-lang-b" aria-expanded="false" aria-haspopup="true" aria-label="Language">'
            f'<span>{cur.upper()}</span>{CHEV}</button><ul class="mx-lang-m">{items}</ul></div>')
    foot = '<nav class="mx-flang" aria-label="Language">' + ''.join(
        f'<a href="{rel_to(page, cur, t)}" hreflang="{HTMLLANG[t]}" lang="{HTMLLANG[t]}"{" aria-current=\"true\"" if t == cur else ""}>{NAMES[t]}</a>' for t in ALL) + '</nav>'
    return head, foot

def head_block(page, cur):
    out = [f'<link rel="canonical" href="{abs_url(page, cur)}">']
    for t in ALL:
        out.append(f'<link rel="alternate" hreflang="{HTMLLANG[t].lower() if t != "de" else "de-at"}" href="{abs_url(page, t)}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{abs_url(page, "en")}">')
    out.append(f'<meta property="og:locale" content="{OGLOC[cur]}">')
    return '\n'.join(out)

def sub_marker(s, name, content):
    pat = re.compile(r'<!--mx-%s-->.*?<!--/mx-%s-->' % (name, name), re.S)
    return pat.sub(lambda m: f'<!--mx-{name}-->{content}<!--/mx-{name}-->', s)

def sync_markers(s, page, cur):
    head, foot = switcher(page, cur)
    s = sub_marker(s, 'lang', head); s = sub_marker(s, 'flang', foot)
    s = re.sub(r'<link rel="canonical"[^>]*>\s*', '', s)
    s = re.sub(r'<meta property="og:locale"[^>]*>\s*', '', s)
    s = sub_marker(s, 'hl', '\n' + head_block(page, cur) + '\n')
    return s

# ---------- translation ----------
def tr_inner(inner, tr, miss):
    key, tags, lead, trail, vals = encode(inner)
    if not key: return inner
    if key in tr: return decode(tr[key], tags, lead, trail, vals, key)
    miss.add(key); return inner

def tr_plain(val, tr, miss):
    key, tags, lead, trail, vals = encode(esc(html.unescape(val)))
    if not key: return val
    if key in tr:
        return decode(tr[key], tags, lead, trail, vals, key).strip().replace('"', '&quot;')
    miss.add(key); return val

FIBRES = {
    'sl': {'cotton': 'bombaž', 'polyester': 'poliester', 'nylon': 'najlon', 'viscose': 'viskoza', 'anti-static': 'antistatik', 'antistatic': 'antistatik', 'meta aramid': 'meta-aramid', 'para aramid': 'para-aramid'},
    'hr': {'cotton': 'pamuk', 'polyester': 'poliester', 'nylon': 'najlon', 'viscose': 'viskoza', 'anti-static': 'antistatik', 'antistatic': 'antistatik', 'meta aramid': 'meta-aramid', 'para aramid': 'para-aramid'},
    'hu': {'cotton': 'pamut', 'polyester': 'poliészter', 'nylon': 'nejlon', 'viscose': 'viszkóz', 'anti-static': 'antisztatikus szál', 'antistatic': 'antisztatikus szál', 'meta aramid': 'meta-aramid', 'para aramid': 'para-aramid'},
    'it': {'cotton': 'cotone', 'polyester': 'poliestere', 'nylon': 'nylon', 'viscose': 'viscosa', 'anti-static': 'antistatico', 'antistatic': 'antistatico', 'meta aramid': 'meta-aramidico', 'para aramid': 'para-aramidico'},
    'de': {'cotton': 'Baumwolle', 'polyester': 'Polyester', 'nylon': 'Nylon', 'viscose': 'Viskose', 'anti-static': 'Antistatik', 'antistatic': 'Antistatik', 'meta aramid': 'Meta-Aramid', 'para aramid': 'Para-Aramid'},
}
FIB_RE = re.compile(r'\b(cotton|polyester|nylon|viscose|anti-static|antistatic|meta aramid|para aramid)\b', re.I)
COMP_RE = re.compile(r'^\d+(?:\.\d+)?%\s')

def tr_comp(t, lang):
    """'75% Cotton / 25% Polyester' -> same composition with fibre names in the target language."""
    m = FIBRES.get(lang)
    if not m or not COMP_RE.match(t) or '<' in t: return t
    def r(mm):
        w = mm.group(1); v = m[w.lower()]
        return v[:1].upper() + v[1:] if w[:1].isupper() else v
    return FIB_RE.sub(r, t)

PLURAL = {
    'sl': "function mxPlural(n){var a=n%100;return a==1?' artikel':a==2?' artikla':(a==3||a==4)?' artikli':' artiklov'}",
    'hr': "function mxPlural(n){var a=n%10,b=n%100;return a==1&&b!=11?' artikl':(a>=2&&a<=4&&(b<12||b>14))?' artikla':' artikala'}",
    'hu': "function mxPlural(n){return ' cikk'}",
    'it': "function mxPlural(n){return n==1?' articolo':' articoli'}",
    'de': "function mxPlural(n){return ' Artikel'}",
}
OLD_ST = ("?(filtered?nCol+' colour'+(nCol===1?'':'s')+' in '+nFab+' fabric'+(nFab===1?'':'s'):'Showing all '+nFab+' fabrics')\n"
          "      :(filtered?shownRows+' colour'+(shownRows===1?'':'s')+' shown':'All colours across all fabrics');")
STATUS = {
 'sl': ("function mxC(n){var a=n%100;return a==1?' barva':a==2?' barvi':(a==3||a==4)?' barve':' barv'}",
        "?(filtered?nCol+mxC(nCol)+' v '+nFab+(nFab===1?' tkanini':' tkaninah'):'Prikazane vse tkanine ('+nFab+')')\n      :(filtered?'Prikazano: '+shownRows+mxC(shownRows):'Vse barve vseh tkanin');"),
 'hr': ("function mxC(n){var a=n%10,b=n%100;return (a==1&&b!=11)?' boja':(a>=2&&a<=4&&(b<12||b>14))?' boje':' boja'}",
        "?(filtered?nCol+mxC(nCol)+' u '+nFab+(nFab===1?' tkanini':(nFab%10>=2&&nFab%10<=4&&(nFab%100<12||nFab%100>14))?' tkanine':' tkanina'):'Prikazane sve tkanine ('+nFab+')')\n      :(filtered?'Prikazano: '+shownRows+mxC(shownRows):'Sve boje svih tkanina');"),
 'hu': ("function mxC(n){return ' szín'}",
        "?(filtered?nCol+' szín, '+nFab+' anyagban':'Mind a(z) '+nFab+' anyag megjelenítve')\n      :(filtered?shownRows+' szín megjelenítve':'Minden szín minden anyagból');"),
 'it': ("function mxC(n){return n==1?' colore':' colori'}",
        "?(filtered?nCol+mxC(nCol)+' in '+nFab+(nFab===1?' tessuto':' tessuti'):'Tutti i '+nFab+' tessuti mostrati')\n      :(filtered?shownRows+mxC(shownRows)+' mostrati':'Tutti i colori di tutti i tessuti');"),
 'de': ("function mxC(n){return n==1?' Farbe':' Farben'}",
        "?(filtered?nCol+mxC(nCol)+' in '+nFab+(nFab===1?' Stoff':' Stoffen'):'Alle '+nFab+' Stoffe angezeigt')\n      :(filtered?shownRows+mxC(shownRows)+' angezeigt':'Alle Farben aller Stoffe');"),
}
OLD_PL = "(rows.length===1?' article':' articles')"

JSLIT = re.compile(r'"((?:[^"\\\n])+)"|\'((?:[^\'\\\n])+)\'')
def tr_js(code, tr, skip=(), lang=None):
    def f(m):
        q = '"' if m.group(1) is not None else "'"
        t = m.group(1) if m.group(1) is not None else m.group(2)
        if '<' in t and '>' in t:                       # markup string: translate its text nodes
            def inner(mm):
                x = ' '.join(html.unescape(mm.group(1)).split())
                if x in tr and x not in skip:
                    v = tr[x].replace('\\', '\\\\').replace(q, '\\' + q)
                    return '>' + v + '<'
                return mm.group(0)
            def attr(mm):
                x = ' '.join(html.unescape(mm.group(2)).split())
                return f'{mm.group(1)}="{tr[x].replace(chr(34), "&quot;")}"' if x in tr and x not in skip else mm.group(0)
            out = re.sub(r'>([^<>]+)<', inner, t)
            out = re.sub(r'\b(title|alt|aria-label|placeholder)="([^"]*)"', attr, out)
            return q + out + q
        if t in tr and t not in skip:
            v = tr[t].replace('\\', '\\\\').replace(q, '\\' + q)
            return q + v + q
        if lang and COMP_RE.match(t):
            return q + tr_comp(t, lang).replace(q, '\\' + q) + q
        return m.group(0)
    return JSLIT.sub(f, code)

SCRIPT = re.compile(r'(<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>)(.*?)(</script>)', re.S)
def fix_url(u, lang):
    if not u or u.startswith(('#', 'http:', 'https:', 'mailto:', 'tel:', 'data:', 'javascript:', '//')): return u
    path = re.split(r'[#?]', u)[0]
    page = path.endswith('.html') or path.endswith('/') or path == ''
    if u.startswith('/'): return ('/' + lang + u) if page else u
    return u if page else '../' + u

def localize(s, lang, tr, miss):
    # visible text
    for a, b in reversed(units(s)):
        s = s[:a] + tr_inner(s[a:b], tr, miss) + s[b:]
    s = ATTR_RE.sub(lambda m: f'{m.group(1)}="{tr_plain(m.group(2), tr, miss) if has_text(m.group(2)) else m.group(2)}"', s)
    s = META_RE.sub(lambda m: m.group(1) + tr_plain(m.group(2), tr, miss) + m.group(3), s)
    s = TITLE_RE.sub(lambda m: m.group(1) + tr_plain(m.group(2), tr, miss) + m.group(3), s)
    # scripts: translate literals, point asset paths one level up
    def scr(m):
        code = tr_js(m.group(2), tr, lang=lang)
        if OLD_ST in code:
            fn, expr = STATUS[lang]
            code = code.replace(OLD_ST, expr).replace('(function(){', '(function(){' + fn + ';', 1)
        if OLD_PL in code: code = code.replace(OLD_PL, 'mxPlural(rows.length)').replace('(function(){', '(function(){' + PLURAL[lang] + ';', 1)
        code = re.sub(r'(["\'`(])((?:\.\./)*assets/)', r'\1../\2', code)
        return m.group(1) + code + m.group(3)
    s = SCRIPT.sub(scr, s)
    s = re.sub(r'url\((["\']?)((?:\.\./)*assets/)', r'url(\1../\2', s)
    s = s.replace('assets/site.js', f'assets/site.{lang}.js')
    s = re.sub(r'\b(href|src|poster|data-src|action)="([^"]*)"', lambda m: f'{m.group(1)}="{fix_url(m.group(2), lang)}"', s)
    s = re.sub(r'<html lang="[^"]*"', f'<html lang="{HTMLLANG[lang]}"', s, count=1)
    return s

def write_sitemap(pages):
    sm = os.path.join(ROOT, 'sitemap.xml')
    old = open(sm, encoding='utf-8').read() if os.path.exists(sm) else ''
    lastmod = {}
    for m in re.finditer(r'<loc>https://www\.maximo-tekstil\.com/(?!(?:sl|hr|hu|it|de)/)([^<]*)</loc><lastmod>([^<]*)</lastmod>', old):
        lastmod[m.group(1) or 'index.html'] = m.group(2)
    rows = []
    for rel, _ in pages:
        if rel == '404.html': continue
        lm = lastmod.get(rel, '2026-10-21')
        for lang in ALL:
            alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{HTMLLANG[t].lower() if t != "de" else "de-at"}" href="{abs_url(rel, t)}"/>' for t in ALL)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(rel, "en")}"/>'
            rows.append(f'  <url><loc>{abs_url(rel, lang)}</loc><lastmod>{lm}</lastmod>{alts}</url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')
    open(sm, 'w', encoding='utf-8').write(xml)

def main():
    only = sys.argv[1:] or LANGS
    pages = list(source_pages())
    for rel, f in pages:                       # sync English pages
        s = open(f, encoding='utf-8').read()
        s2 = sync_markers(s, rel, 'en')
        if s2 != s: open(f, 'w', encoding='utf-8').write(s2)
    js = open(os.path.join(ROOT, 'assets/site.js'), encoding='utf-8').read()
    for lang in only:
        tr = load(lang); miss = set(); total = 0
        out = os.path.join(ROOT, lang)
        if os.path.exists(out): shutil.rmtree(out)
        for rel, f in pages:
            s = open(f, encoding='utf-8').read()
            s = localize(s, lang, tr, miss)
            s = sync_markers(s, rel, lang)
            dst = os.path.join(out, rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'w', encoding='utf-8').write(s); total += 1
        open(os.path.join(ROOT, f'assets/site.{lang}.js'), 'w', encoding='utf-8').write(tr_js(js, tr, skip=('yes',)))
        print(lang, total, 'pages, untranslated strings:', len(miss))
        if os.environ.get('SHOW_MISS'):
            json.dump(sorted(miss), open(os.path.join(ROOT, f'i18n/missing_{lang}.json'), 'w'), ensure_ascii=False, indent=0)

if __name__ == '__main__':
    main()
    write_sitemap(list(source_pages()))
