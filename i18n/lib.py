"""Shared parsing helpers for the translation tooling (extract + build)."""
import re, html, os, glob
from html.parser import HTMLParser

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
LANGS = ['sl', 'hr', 'hu', 'it', 'de']
INLINE = {'a', 'b', 'strong', 'i', 'em', 'span', 'small', 'sup', 'sub', 'br', 'abbr', 'code', 'mark', 'u', 'wbr', 'bdi', 'cite', 'time'}
VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'wbr', 'source', 'area', 'col', 'base', 'embed', 'track', 'param'}
OPAQUE = {'script', 'style', 'svg', 'noscript', 'textarea'}

FABRICS = sorted({os.path.basename(f)[:-5].upper().replace('-', ' ')
                  for f in glob.glob(os.path.join(ROOT, 'on-stock/fabrics/*.html'))}, key=lambda x: -len(x))
FAB_RE = re.compile(r'\b(' + '|'.join(re.escape(n) for n in FABRICS) + r')\b')
NUM_RE = re.compile(r'\b\d{4,}\b')


class Node:
    __slots__ = ('tag', 'start', 'cs', 'ce', 'end', 'kids', 'parent')
    def __init__(self, tag, start, cs, parent):
        self.tag, self.start, self.cs, self.ce, self.end = tag, start, cs, None, None
        self.kids, self.parent = [], parent


class Tree(HTMLParser):
    def __init__(self, s):
        super().__init__(convert_charrefs=False)
        self.s = s
        self.lines = [0]
        for m in re.finditer('\n', s): self.lines.append(m.end())
        self.root = Node('#root', 0, 0, None)
        self.root.ce = self.root.end = len(s)
        self.cur = self.root
        self.opaque = 0
        self.feed(s); self.close()

    def off(self):
        l, c = self.getpos(); return self.lines[l - 1] + c

    def handle_starttag(self, tag, attrs):
        o = self.off(); raw = self.get_starttag_text()
        if self.opaque:
            if tag in OPAQUE: self.opaque += 1
            return
        n = Node(tag, o, o + len(raw), self.cur)
        self.cur.kids.append(n)
        if tag in VOID or raw.endswith('/>') and tag not in OPAQUE:
            n.ce = n.cs; n.end = n.cs; return
        self.cur = n
        if tag in OPAQUE: self.opaque = 1

    def handle_startendtag(self, tag, attrs):
        if self.opaque: return
        o = self.off(); raw = self.get_starttag_text()
        n = Node(tag, o, o + len(raw), self.cur); n.ce = n.cs; n.end = n.cs
        self.cur.kids.append(n)

    def handle_endtag(self, tag):
        o = self.off()
        if self.opaque:
            if tag in OPAQUE:
                self.opaque -= 1
                if self.opaque == 0 and self.cur.tag == tag: self._close(o)
            return
        n = self.cur
        while n is not self.root and n.tag != tag: n = n.parent
        if n is self.root: return
        self.cur = n; self._close(o)

    def _close(self, o):
        n = self.cur; n.ce = o
        n.end = self.s.find('>', o) + 1
        self.cur = n.parent


def text_of(s):
    return html.unescape(re.sub(r'<[^>]*>', '', s))

CAPS_OK = {'CERTIFIED & LICENSED', 'FABRIC BY JOB', 'FIBRES · COMPOSITION', 'FINAL CERTIFICATION IS DONE ON THE FINISHED GARMENT · TEST REPORTS AND DATA SHEETS ON REQUEST',
           'HOW TO READ THE TABLE', 'MADE TO ORDER', 'PROTECTION · FINISH · DYEING', 'RECOMMENDED', 'THE COLLECTION', 'VAT ID', 'WEAVE · WEIGHT · WIDTH', 'STRETCH'}

def has_text(t):
    t = ' '.join(t.split())
    if t in CAPS_OK: return True
    if not re.search(r'[a-z]{2}', t): return False
    if re.fullmatch(r'[\w.+-]+@[\w.-]+', t) or re.search(r'https?://|\{\{|\}\}', t): return False
    return True

def inline_only(n):
    return all(k.tag in INLINE and inline_only(k) for k in n.kids if k.tag not in OPAQUE) and \
           not any(k.tag in OPAQUE for k in n.kids)

def wrapper_only(s, n):
    """True when n only wraps child elements (no text of its own) and some child has text."""
    if not n.kids: return False
    pos = n.cs
    for k in n.kids:
        if s[pos:k.start].strip(): return False
        pos = k.end if k.end is not None else k.start
    if s[pos:n.ce].strip(): return False
    return any(has_text(text_of(s[k.cs:k.ce])) for k in n.kids)

def units(s):
    """Ranges (a, b) of translatable inner HTML in s."""
    t = Tree(s); out = []
    def walk(n):
        if n.tag in OPAQUE: return
        if n is not t.root and n.tag in ('head',): return
        if n is not t.root and inline_only(n) and not wrapper_only(s, n):
            if has_text(text_of(s[n.cs:n.ce])): out.append((n.cs, n.ce))
            return
        pos = n.cs
        for k in n.kids:
            seg = s[pos:k.start]
            if has_text(text_of(seg)): out.append((pos, k.start))
            walk(k)
            pos = max(pos, k.end if k.end is not None else k.start)
        seg = s[pos:n.ce]
        if has_text(text_of(seg)): out.append((pos, n.ce))
    walk(t.root)
    return out

TAG_RE = re.compile(r'<(/?)([A-Za-z][A-Za-z0-9]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/?)>')

def encode(inner):
    """inner HTML -> (key, tags, values): key uses <1>..</1> markers and {F}/{N} placeholders."""
    tags = []; stack = []; out = []; pos = 0
    for m in TAG_RE.finditer(inner):
        out.append(('t', inner[pos:m.start()]))
        close, name, attrs, selfc = m.groups()
        if close:
            idx = None
            for j in range(len(stack) - 1, -1, -1):
                if stack[j][1] == name.lower(): idx = stack.pop(j)[0]; break
            out.append(('x', f'</{idx}>' if idx else m.group(0)))
        else:
            idx = len(tags) + 1; tags.append(m.group(0))
            if selfc or name.lower() in VOID: out.append(('x', f'<{idx}/>'))
            else: stack.append((idx, name.lower())); out.append(('x', f'<{idx}>'))
        pos = m.end()
    out.append(('t', inner[pos:]))
    parts = []
    for k, v in out:
        parts.append(v if k == 'x' else html.unescape(v))
    key = ''.join(parts)
    lead = re.match(r'\s*', key).group(0); trail = re.search(r'\s*$', key).group(0)
    key = ' '.join(key.split())
    vals = []
    def fab(m): vals.append(('F', m.group(0))); return '{F}'
    key = FAB_RE.sub(fab, key)
    key = NUM_RE.sub(lambda m: (vals.append(('N', m.group(0))), '{N}')[1], key)
    # restore left-to-right order of values
    order = [(m.start(), m.group(0)) for m in re.finditer(r'\{[FN]\}', key)]
    return key, tags, lead, trail, vals

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def decode(trans, tags, lead, trail, vals, orig_key):
    """Rebuild inner HTML from a translated key."""
    # placeholders: values were appended F-first then N; rebuild by original order
    fvals = [v for k, v in vals if k == 'F']; nvals = [v for k, v in vals if k == 'N']
    # collect original order of placeholders in the source key
    seq = re.findall(r'\{[FN]\}', orig_key)
    fi = iter(fvals); ni = iter(nvals)
    src = [next(fi) if p == '{F}' else next(ni) for p in seq]
    # in translation the order may differ; map k-th placeholder of each kind
    fi = iter(fvals); ni = iter(nvals)
    def ph(m):
        try: return next(fi) if m.group(0) == '{F}' else next(ni)
        except StopIteration: return m.group(0)
    pieces = re.split(r'(</?\d+/?>)', trans)
    out = []
    for p in pieces:
        m = re.fullmatch(r'<(/?)(\d+)(/?)>', p)
        if m:
            idx = int(m.group(2)); raw = tags[idx - 1]
            if m.group(1):
                name = re.match(r'<([A-Za-z0-9]+)', raw).group(1); out.append(f'</{name}>')
            else: out.append(raw)
        else:
            out.append(esc(re.sub(r'\{[FN]\}', ph, p)))
    return lead + ''.join(out) + trail
