"""One-off: add language-switcher / hreflang markers to the English master pages (idempotent)."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract import source_pages
for rel, f in source_pages():
    s = open(f, encoding='utf-8').read()
    if '<!--mx-lang-->' in s: continue
    s = s.replace('</head>', '<!--mx-hl--><!--/mx-hl-->\n</head>', 1)
    s = re.sub(r'(<div class="mx-act">)(<a class="mx-cta")', r'\1<!--mx-lang--><!--/mx-lang-->\2', s, 1)
    s = re.sub(r'(<nav aria-label="Legal">.*?</nav>)', r'\1<!--mx-flang--><!--/mx-flang-->', s, 1, flags=re.S)
    open(f, 'w', encoding='utf-8').write(s)
