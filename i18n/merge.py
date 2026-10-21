"""Merge chunks/*.json (index -> [sl,hr,hu,it,de]) into translations/<lang>.json, validating markup."""
import json, glob, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import LANGS
todo = json.load(open('todo.json'))
strings = json.load(open('strings.json'))
colours = json.load(open('colours.json'))
pat = re.compile(r'^(.+?) \{N\}( · \{F\}|, \{F\})?$')
os.makedirs('translations', exist_ok=True)
out = {l: {} for l in LANGS}
errors = 0
def sig(s): return sorted(re.findall(r'</?\d+/?>|\{[FN]\}', s))
for f in sorted(glob.glob('chunks/*.json')):
    for i, vals in json.load(open(f)).items():
        key = todo[int(i)]
        if len(vals) != len(LANGS): print('BAD LEN', f, i); errors += 1; continue
        for l, v in zip(LANGS, vals):
            if not v.strip() or sig(v) != sig(key):
                print('MISMATCH', f, i, l, repr(key[:60]), '->', repr(v[:60])); errors += 1; continue
            out[l][key] = v
# derive colour variants
for k in strings:
    m = pat.match(k)
    if m and m.group(1) in colours:
        for l in LANGS:
            base = out[l].get(m.group(1))
            if base: out[l][k] = base + k[len(m.group(1)):]
for l in LANGS:
    json.dump(out[l], open(f'translations/{l}.json', 'w'), ensure_ascii=False, indent=0)
done = len({k for k in out['sl']})
missing = [k for k in strings if k not in out['sl']]
print('translated', done, 'of', len(strings), 'missing', len(missing), 'errors', errors)
