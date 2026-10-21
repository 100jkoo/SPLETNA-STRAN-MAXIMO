# Maximo Tekstil – spletna stran

Statična spletna stran podjetja Maximo Tekstil (delovne in zaščitne tkanine): domača stran, o nas, kontakt, šivanje, izdelava, Repreve, Sorona, vodič po tkanjih, blog in zaloga tkanin.

## Struktura

| Pot | Vsebina |
| --- | --- |
| `index.html` | Domača stran |
| `about.html`, `contact.html`, `sewing.html`, `manufacturing.html` | Glavne strani |
| `repreve.html`, `sorona.html`, `multinorm-fr-proban.html`, `weave-guide.html` | Strani o materialih in standardih |
| `blog/` | Članki (15) |
| `on-stock/` | Zaloga, s posameznimi tkaninami v `on-stock/fabrics/` |
| `assets/` | CSS, JS, pisave, slike in PDF |
| `privacy.html`, `terms.html`, `404.html` | Pravne strani in stran za napake |
| `sitemap.xml`, `robots.txt` | SEO |
| `maximo-tekstil-site.zip` | Pripravljen paket za objavo |

## Ogled lokalno

```bash
python3 -m http.server 8000
```

Nato odpri http://localhost:8000.

## Objava na Wix

1. Odpri https://www.wix.com/headless/drop?utm_campaign=mcp
2. Povleci `maximo-tekstil-site.zip`.
3. Stran se objavi na naslovu `*.wix-site-host.com`.

Po vsaki spremembi strani je treba zip ponovno narediti, da je v njem zadnja različica.

## Stanje

Delo v teku: domača stran še ni dokončana.
