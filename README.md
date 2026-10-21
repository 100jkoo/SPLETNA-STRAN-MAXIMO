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

## Jeziki

Stran je v šestih jezikih. Angleščina je glavna različica v korenu repozitorija, prevodi so v mapah:

| Jezik | Mapa |
| --- | --- |
| English | `/` (koren) |
| Slovenščina | `sl/` |
| Hrvatski | `hr/` |
| Magyar | `hu/` |
| Italiano | `it/` |
| Deutsch (Avstrija) | `de/` |

Mape `sl/ hr/ hu/ it/ de/` in datoteke `assets/site.<jezik>.js` ter `sitemap.xml` so **ustvarjene samodejno**, zato jih ne urejaj ročno.

### Kako spremeniš besedilo

1. Spremeni angleško stran v korenu (npr. `index.html`).
2. Če si dodal ali spremenil besedilo, zaženi `python3 i18n/extract.py` in `python3 i18n/todo.py`. Novi angleški nizi se dodajo na konec `i18n/todo.json`.
3. Prevode dodaj v `i18n/chunks/NNN.json` (po vrsti: sl, hr, hu, it, de) in zaženi `python3 i18n/merge.py`.
4. Zaženi `python3 i18n/build.py` in prevedene strani se znova ustvarijo.

Neprevedeno besedilo ostane v angleščini. Pravni besedili (`terms.html`, `privacy.html`) naj pregleda odvetnik.

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
