"""Collect translatable English strings into strings.json (key -> pages)."""
import re, glob, json, os, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

SKIP = {'weave-guide.html'}
ATTR_RE = re.compile(r'\b(alt|title|placeholder|aria-label|data-n)="([^"]*)"')
META_RE = re.compile(r'(<meta\b[^>]*\b(?:name="description"|property="og:(?:title|description)")[^>]*\bcontent=")([^"]*)(")')
TITLE_RE = re.compile(r'(<title>)(.*?)(</title>)', re.S)

def source_pages():
    for f in sorted(glob.glob(os.path.join(ROOT, '**/*.html'), recursive=True)):
        rel = os.path.relpath(f, ROOT)
        if rel.split('/')[0] in LANGS or rel in SKIP: continue
        yield rel, f

def collect(s):
    keys = []
    for a, b in units(s):
        keys.append(encode(s[a:b])[0])
    for m in ATTR_RE.finditer(s):
        if has_text(m.group(2)): keys.append(encode(html.escape(html.unescape(m.group(2))))[0])
    for m in META_RE.finditer(s): keys.append(encode(m.group(2))[0])
    m = TITLE_RE.search(s)
    if m: keys.append(encode(m.group(2))[0])
    return keys

if __name__ == '__main__':
    seen = {}
    for rel, f in source_pages():
        for k in collect(open(f, encoding='utf-8').read()):
            if k: seen.setdefault(k, set()).add(rel)
    json.dump({k: sorted(v) for k, v in sorted(seen.items())}, open(os.path.join(ROOT, 'i18n/strings.json'), 'w'), ensure_ascii=False, indent=0)
    print(len(seen), sum(len(k) for k in seen))
