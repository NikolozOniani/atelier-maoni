#!/usr/bin/env python3
"""Optional editing tool. Publishes plain HTML; never runs on the hosting server.

Edit _studio/data, run python3 _studio/render.py, commit the resulting HTML.
The default runtime uses Python's standard library only.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / '_studio/data' / name).read_text())


SITE = read('site.json')
COPY = read('translations.json')
PROJECTS = read('portfolio.json')
IMAGES = {row['id']: row for row in read('photo-inventory.json')}
BASE = SITE['siteUrl'].rstrip('/')
if BASE and (urlparse(BASE).scheme != 'https' or not urlparse(BASE).netloc or urlparse(BASE).query or urlparse(BASE).fragment):
    raise ValueError('siteUrl must be the confirmed HTTPS website root, without query or fragment.')


def e(value):
    return escape(str(value), quote=True)


def route(lang, page):
    return f'{lang}/' + (f'{page}/' if page != 'home' else '')


def picture(n, prefix, alt, hero=False, sizes='(max-width: 540px) 45vw, 28vw'):
    r = IMAGES[n]
    variants = r['variants']
    default = variants[min(1, len(variants) - 1)]
    srcset = ', '.join(f"{prefix}assets/images/{v['file']} {v['width']}w" for v in variants)
    priority = 'fetchpriority="high" loading="eager"' if hero else 'loading="lazy"'
    return f'<img src="{prefix}assets/images/{default["file"]}" srcset="{srcset}" sizes="{sizes}" width="{default["width"]}" height="{default["height"]}" alt="{e(alt)}" {priority} decoding="async">'


def brand(prefix, lang):
    return f'''<a class="brand" href="{prefix}{lang}/">
    <img src="{prefix}assets/images/logo-13-96.webp" width="58" height="58" alt="">
    <span class="brand-copy"><span class="brand-name">MAONI</span> <span class="brand-label">ATELIER · TBILISI</span></span></a>'''


def arrow():
    return '<svg class="arrow" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg>'


def header(prefix, lang, page, c):
    links = ''.join(f'<a href="{prefix}{route(lang, target)}"{(" aria-current=\"page\"" if target == page else "")}>{c["nav"][i]}</a>' for i, target in enumerate(['home', 'work', 'contact']))
    switches = ' <span aria-hidden="true">/</span> '.join(f'<a href="{prefix}{route(l, page)}" lang="{l}" hreflang="{l}" aria-label="{l.upper()} — {("ქართული" if l == "ka" else "English")}"{(" aria-current=\"true\"" if l == lang else "")}>{l.upper()}</a>' for l in ['ka', 'en'])
    return f'''<a class="skip-link" href="#main">{c['skip']}</a><header class="site-header"><div class="wrap header-inner">
    {brand(prefix,lang)}<div class="header-right"><nav class="main-nav" id="navigation" aria-label="{e(c['menu'])}">{links}</nav>
    <div class="language-switch">{switches}</div>
    <button class="menu-toggle" aria-expanded="false" aria-controls="navigation" data-open-label="{e(c['menu'])}" data-close-label="{e(c['closeMenu'])}"><span class="menu-text">{c['menu']}</span><span class="menu-lines" aria-hidden="true"></span></button>
    </div></div></header>'''


def footer(prefix, lang, c):
    links = ''.join(f'<a href="{prefix}{route(lang, page)}">{c["nav"][i]}</a>' for i, page in enumerate(['home', 'work', 'contact']))
    return f'''<footer class="site-footer"><div class="wrap"><div class="footer-top">
    <div class="footer-brand">{brand(prefix,lang)}<p>{c['footerText']}</p></div>
    <div class="footer-contact"><a href="tel:{SITE['telephone']}">{SITE['phone']}</a><address>{e(SITE['address'])}</address></div>
    <nav class="footer-nav" aria-label="{e(c['menu'])}">{links}</nav></div>
    <div class="footer-bottom"><span>© {c['footerRights']}</span><span>{c['location']}</span></div></div></footer>'''


def cta(prefix, lang, c):
    return f'''<section class="contact-cta"><div class="wrap"><p class="eyebrow">{c['contactKicker']}</p><h2 class="section-title">{c['ctaTitle']}</h2><p>{c['ctaText']}</p>
    <div class="button-row"><a class="button" href="tel:{SITE['telephone']}">{c['call']}{arrow()}</a><a class="text-link" href="{prefix}{lang}/contact/">{c['contactUs']}{arrow()}</a></div></div></section>'''


def card(p, prefix, lang, c, number, home=False):
    n = p['images'][0]
    big = IMAGES[n]['variants'][-1]['file']
    destination = f'{prefix}{lang}/work/#{p["id"]}' if home else f'{prefix}assets/images/{big}'
    enhancement = '' if home else f' data-view-project="{p["id"]}"'
    alts = p['alt'][lang]
    image_links = ''.join(f'<li><a href="{prefix}assets/images/{IMAGES[n]["variants"][-1]["file"]}" data-view-project="{p["id"]}" data-image-index="{i}" data-alt="{e(alts[i])}">{c["image"]} {i+1}</a></li>' for i, n in enumerate(p['images']))
    return f'''<article class="project-card" id="{p['id']}" data-category="{p['category']}">
    <a class="project-image" href="{destination}"{enhancement} aria-label="{e(c['viewProject'] + ': ' + p['title'][lang])}">{picture(n,prefix,alts[0])}<span class="project-open" aria-hidden="true">+</span></a>
    <div class="project-caption"><div><h3>{e(p['title'][lang])}</h3><p class="project-category">{c['categories'][p['category']]}</p></div><span class="project-number">{number:02}</span></div>
    <p class="project-description">{e(p['description'][lang])}</p>{'' if home else f'<ul class="project-gallery" aria-label="{e(p["title"][lang])}">{image_links}</ul>'}</article>'''


def home(prefix, lang, c):
    selected = ''.join(card(p, prefix, lang, c, i+1, True) for i,p in enumerate(p for p in PROJECTS if p['featured']))
    services = ''.join(f'<li><span class="number">0{i+1}</span><div><h3>{title}</h3><p>{text}</p></div></li>' for i,(title,text) in enumerate(c['services']))
    return f'''<main id="main"><section class="hero wrap" aria-labelledby="hero-title">
    <div class="hero-copy"><p class="eyebrow">{c['heroKicker']}</p><p class="hero-wordmark" lang="en"><span>ATELIER</span>MAONI</p>
    <h1 id="hero-title">{c['heroTitle']}</h1><p class="hero-text">{c['heroText']}</p><div class="button-row"><a class="button solid" href="{prefix}{lang}/work/">{c['viewWork']}{arrow()}</a><a class="text-link" href="{prefix}{lang}/contact/">{c['contactUs']}{arrow()}</a></div><p class="hero-note">{c['craft']}</p></div>
    <figure class="hero-photo"><a href="{prefix}{lang}/work/#silver" aria-label="{e(c['viewProject']+': '+PROJECTS[0]['title'][lang])}">{picture(4,prefix,PROJECTS[0]['alt'][lang][0],True,'(max-width: 540px) 85vw, 43vw')}</a><span class="photo-tag" aria-hidden="true">ATELIER / 01</span><figcaption><span>{c['heroCaption']}</span><span>01 / MAONI</span></figcaption></figure></section>
    <section class="selected wrap" aria-labelledby="selected-title"><div class="section-topline"><p class="eyebrow">{c['selectedKicker']}</p><span class="section-index">01 — 06</span></div>
    <div class="section-heading"><div><h2 class="section-title" id="selected-title">{c['selectedTitle']}</h2><p>{c['selectedText']}</p></div><a class="text-link" href="{prefix}{lang}/work/">{c['allWork']}{arrow()}</a></div>
    <div class="project-grid">{selected}</div><div class="selected-bottom"><a class="text-link" href="{prefix}{lang}/work/">{c['allWork']}{arrow()}</a></div></section>
    <section class="services" aria-labelledby="services-title"><div class="wrap"><div class="section-topline"><p class="eyebrow">{c['servicesKicker']}</p><span class="section-index">MAONI / ATELIER</span></div><div class="services-content"><h2 class="section-title" id="services-title">{c['servicesTitle']}</h2><ol class="services-list">{services}</ol></div></div></section>
    <section class="about wrap" aria-labelledby="about-title"><figure class="about-photo">{picture(25,prefix,c['aboutCaption'],False,'(max-width: 540px) 75vw, 36vw')}<figcaption>{c['aboutCaption']}</figcaption></figure>
    <div class="about-copy"><p class="eyebrow">{c['aboutKicker']}</p><h2 class="section-title" id="about-title">{c['aboutTitle']}</h2><p>{c['aboutText']}</p><p>{c['aboutSecond']}</p><a class="text-link" href="{prefix}{lang}/contact/">{c['contactUs']}{arrow()}</a></div></section>
    {cta(prefix,lang,c)}</main>'''


def work(prefix, lang, c):
    buttons = ''.join(f'<button type="button" class="filter" data-filter="{cat}" aria-pressed="{str(cat == "all").lower()}">{e(label)}</button>' for cat,label in [('all',c['all']),*c['categories'].items()])
    cards = ''.join(card(p,prefix,lang,c,i+1) for i,p in enumerate(PROJECTS))
    return f'''<main id="main"><div class="wrap"><header class="page-intro"><p class="eyebrow">{c['workKicker']}</p><h1>{c['workTitle']}</h1><p>{c['workText']}</p></header>
    <section class="portfolio" aria-label="{e(c['workKicker'])}"><h2 class="sr-only">{c['workKicker']}</h2><div class="portfolio-toolbar"><div class="filters" role="group" aria-label="{e(c['filterLabel'])}" hidden>{buttons}</div><p class="results-count" data-results data-label="{e(c['projectCount'])}" role="status">{len(PROJECTS)} {c['projectCount']}</p></div><div class="project-grid">{cards}</div></section></div>{cta(prefix,lang,c)}</main>
    <dialog class="viewer" aria-labelledby="viewer-title" aria-describedby="viewer-caption" data-image-label="{c['image']}" data-of-label="{c['of']}"><div class="viewer-layout"><div class="viewer-top"><p class="viewer-label" aria-live="polite"></p><button class="viewer-close" aria-label="{e(c['closeViewer'])}">×</button></div><img class="viewer-image" alt=""><div class="viewer-bottom"><div><h2 class="viewer-title" id="viewer-title"></h2><p class="viewer-caption" id="viewer-caption"></p></div><div class="viewer-controls"><button data-previous aria-label="{e(c['previous'])}"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true"><path d="m12 5-7 7 7 7M5 12h14"/></svg></button><span class="viewer-counter"></span><button data-next aria-label="{e(c['next'])}"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true"><path d="m12 5 7 7-7 7M19 12H5"/></svg></button></div></div></div></dialog>'''


def contact(prefix, lang, c):
    return f'''<main id="main" class="wrap"><header class="page-intro"><p class="eyebrow">{c['contactUs']}</p><h1>{c['contactTitle']}</h1><p>{c['contactIntro']}</p></header>
    <div class="contact-layout"><section class="contact-details" aria-label="{e(c['visit'])}">
    <div class="contact-detail"><h2>{c['addressLabel']}</h2><address><strong>Atelier MAONI</strong><br>{e(SITE['address'])}</address></div>
    <div class="contact-detail"><h2>{c['phoneLabel']}</h2><a class="phone" href="tel:{SITE['telephone']}">{SITE['phone']}</a></div>
    <div class="contact-detail"><h2>{c['socialLabel']}</h2><div class="button-row"><a class="text-link" href="{e(SITE['facebook'])}" rel="noopener noreferrer" target="_blank" lang="en">Facebook{arrow()}</a><a class="text-link" href="{e(SITE['whatsapp'])}" rel="noopener noreferrer" target="_blank" lang="en">WhatsApp{arrow()}</a></div></div>
    <p class="hours">{c['hours']}</p><div class="button-row"><a class="button solid" href="tel:{SITE['telephone']}">{c['call']}{arrow()}</a></div></section>
    <section class="location-panel" aria-labelledby="location-title"><p class="eyebrow">{c['location']}</p><div><h2 id="location-title">{c['mapTitle']}</h2><p>{c['mapText']}</p><a class="text-link" href="{e(SITE['directions'])}" rel="noopener noreferrer" target="_blank">{c['directions']}{arrow()}</a></div><p class="privacy">{c['mapPrivacy']}</p></section></div></main>'''


def metadata(prefix, lang, page, c):
    canonical = f'{BASE}/{route(lang,page)}' if BASE else ''
    alternates = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{e(BASE + "/" if BASE else prefix)}{route(l,page)}">' for l in ['ka','en'])
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{e(BASE + "/" if BASE else prefix)}{route("ka",page)}">'
    structured = {'@context':'https://schema.org','@type':'LocalBusiness','name':SITE['name'],'alternateName':SITE['georgianName'],'description':COPY['en']['homeDescription'],'telephone':SITE['telephone'],'address':{'@type':'PostalAddress','streetAddress':SITE['street'],'addressLocality':SITE['city'],'postalCode':SITE['postalCode'],'addressCountry':SITE['country']},'hasMap':SITE['directions'],'sameAs':[SITE['facebook']],'knowsLanguage':['ka','en'],'hasOfferCatalog':{'@type':'OfferCatalog','name':'Custom clothing','itemListElement':[{'@type':'Offer','itemOffered':{'@type':'Service','name':name}} for name in ['Custom dressmaking','Evening dresses','Everyday clothing','Children’s clothing','Bridal designs','Traditional garments']]}}
    ogimage = IMAGES[4]['variants'][-1]['file']
    urls = f'<link rel="canonical" href="{e(canonical)}"><meta property="og:url" content="{e(canonical)}"><meta property="og:image" content="{e(BASE)}/assets/images/{ogimage}"><meta property="og:image:alt" content="{e(PROJECTS[0]["alt"][lang][0])}">' if BASE else '<!-- Set siteUrl in _studio/data/site.json to emit absolute canonical, social-image and sitemap URLs. -->'
    if BASE: structured.update(url=BASE+'/',image=f'{BASE}/assets/images/{ogimage}')
    return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(c['titles'][page])}</title><meta name="description" content="{e(c[page+'Description'])}">
    {urls}{alternates}<meta property="og:type" content="website"><meta property="og:site_name" content="Atelier MAONI"><meta property="og:title" content="{e(c['titles'][page])}"><meta property="og:description" content="{e(c[page+'Description'])}"><meta property="og:locale" content="{'ka_GE' if lang == 'ka' else 'en_GB'}"><meta property="og:locale:alternate" content="{'en_GB' if lang == 'ka' else 'ka_GE'}"><meta name="theme-color" content="#f8f6f2">
    <link rel="icon" type="image/webp" href="{prefix}assets/images/logo-13-96.webp"><link rel="stylesheet" href="{prefix}assets/css/styles.css"><link rel="preload" href="{prefix}assets/fonts/{'noto-serif-georgian' if lang == 'ka' else 'cormorant'}.woff2" as="font" type="font/woff2" crossorigin>
    <script type="application/ld+json">{json.dumps(structured,ensure_ascii=False).replace('<','\\u003c')}</script><script src="{prefix}assets/js/main.js" defer></script>{f'<script src="{prefix}assets/js/portfolio.js" defer></script>' if page == 'work' else ''}'''


def render():
    for lang,c in COPY.items():
        for page in ['home','work','contact']:
            target = ROOT/route(lang,page)/'index.html'
            target.parent.mkdir(parents=True,exist_ok=True)
            prefix = '../' if page == 'home' else '../../'
            content = {'home':home,'work':work,'contact':contact}[page](prefix,lang,c)
            target.write_text(f'<!doctype html>\n<html lang="{lang}"><head>{metadata(prefix,lang,page,c)}</head><body>{header(prefix,lang,page,c)}{content}{footer(prefix,lang,c)}</body></html>\n')
    (ROOT/'index.html').write_text('''<!doctype html>
<html lang="ka"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0;url=ka/"><title>ატელიე მაონი | Atelier MAONI</title><meta name="description" content="ატელიე მაონი — ინდივიდუალური კერვის ატელიე თბილისში."><link rel="stylesheet" href="assets/css/styles.css"></head><body><main class="wrap page-intro"><p class="eyebrow">ATELIER MAONI · TBILISI</p><h1>ატელიე მაონი</h1><p><a class="text-link" href="ka/" lang="ka">ქართული →</a></p><p><a class="text-link" href="en/" lang="en">English →</a></p></main></body></html>
''')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    if BASE:
        for lang in ['ka','en']:
            for page in ['home','work','contact']:
                sitemap += f'  <url><loc>{e(BASE)}/{route(lang,page)}</loc></url>\n'
    else: sitemap += '  <!-- Publication prerequisite: set the confirmed siteUrl and rerun _studio/render.py. -->\n'
    (ROOT/'sitemap.xml').write_text(sitemap+'</urlset>\n')
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n'+(f'Sitemap: {BASE}/sitemap.xml\n' if BASE else '# Set siteUrl and refresh this file before publication.\n'))
    print('Wrote six localized pages, the Georgian entry point, sitemap.xml and robots.txt.')


if __name__ == '__main__':
    render()
