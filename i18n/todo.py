"""Build the ordered list of keys that need manual translation (todo.json) and show a chunk."""
import json, re, sys, os
d = json.load(open('strings.json'))
pat = re.compile(r'^(.+?) \{N\}( · \{F\}|, \{F\})?$')
names = {pat.match(k).group(1) for k in d if pat.match(k)}
names = {n for n in names if n in d}          # real colour names exist as standalone strings
derived = {k for k in d if pat.match(k) and pat.match(k).group(1) in names}
keys = [k for k in d if k not in derived]
def rank(k):
    pages = d[k]
    return (-len(pages), pages[0], k)
keys.sort(key=rank)
if os.path.exists('todo.json'):                     # keep existing indices stable, append new keys
    old = json.load(open('todo.json'))
    keys = old + [k for k in keys if k not in set(old)]
extra = json.load(open('js_strings.json')) if os.path.exists('js_strings.json') else []
for e in extra:
    if e not in d and e not in keys: keys.append(e)
json.dump(keys, open('todo.json', 'w'), ensure_ascii=False)
json.dump(sorted(names), open('colours.json', 'w'), ensure_ascii=False)
print(len(keys), sum(len(k) for k in keys), len(names))
