#!/usr/bin/env python3
"""Static site generator for plglegal.com.

Usage: python3 build.py   ->  writes the finished site to dist/
Content lives in content/ (Markdown + YAML frontmatter). Assets live in public/.
Requires: markdown, pyyaml, jinja2 (pip install markdown pyyaml jinja2).
"""
import json, re, shutil, pathlib, datetime
import yaml, markdown
from jinja2 import Environment, FileSystemLoader

ROOT = pathlib.Path(__file__).parent
CONTENT, PUBLIC, DIST = ROOT / 'content', ROOT / 'public', ROOT / 'dist'
SITE = 'https://plglegal.com'
GA_ID = ''           # Google Analytics 4 ID, e.g. 'G-XXXXXXX' (leave blank until created)
ADS_ID = ''          # Google Ads tag ID, e.g. 'AW-123456789'

FIRM = {
    'name': 'Prospect Law Group, PC',
    'short': 'Prospect Law Group',
    'phone': '323-452-5222', 'tel': '+13234525222',
    'sms': '+18183956464', 'sms_display': '818-395-6464',
    'email': 'contact@plglegal.com',
    'street': '600 W. Broadway, Ste. 320', 'city': 'Glendale', 'region': 'CA', 'zip': '91204',
    'maps': 'https://www.google.com/maps/search/?api=1&query=Prospect+Law+Group+600+W+Broadway+Suite+320+Glendale+CA+91204',
    'social': {'Instagram': 'https://instagram.com/plglegal'},
}

REMOVED = {  # old URLs that no longer exist -> where they go now
    '/results/': '/#reviews', '/testimonials/': '/#reviews',
    '/hy/results/': '/hy/', '/hy/testimonials/': '/hy/',
}

# ---------- text helpers ----------
STRINGS = {
    'en': dict(call='Call', text='Text Us', review='Free Case Review', consult='Free Consultation', nofee='No fee unless we win',
               form_title='Get Your Free Case Review', form_sub='Tell us what happened. We respond quickly.',
               name='Full name', phone='Phone', email='Email (optional)', case='Type of case', msg='What happened?',
               consent='I agree to be contacted about my inquiry. Submitting this form does not create an attorney-client relationship.',
               send='Send', sending='Sending...', ok='Thank you. We received your message and will contact you shortly.',
               err='Something went wrong. Please call or text us at', choose='Choose one',
               cases=['Car accident', 'Uber or Lyft accident', 'Truck accident', 'Motorcycle accident', 'Lemon law (defective car)', 'Slip and fall or premises', 'Other injury'],
               stars='5.0 on Google', armenian='We speak Armenian', office='Office', follow='Follow us',
               ad='This website is attorney advertising. The information on this site is general information, not legal advice. Contacting us does not create an attorney-client relationship.',
               home='Home', skip='Skip to content', menu='Menu', call_now='Call Now'),
    'hy': dict(call='Զանգահարել', text='Գրել SMS', review='Անվճար գնահատում', consult='Անվճար խորհրդատվություն', nofee='Վճար միայն հաղթանակի դեպքում',
               form_title='Անվճար գործի գնահատում', form_sub='Պատմեք, թե ինչ է պատահել։ Մենք արագ կպատասխանենք։',
               name='Անուն ազգանուն', phone='Հեռախոս', email='Էլ. փոստ (ըստ ցանկության)', case='Գործի տեսակ', msg='Ի՞նչ է պատահել',
               consent='Համաձայն եմ, որ ինձ հետ կապվեն։ Այս ձևը ուղարկելը չի ստեղծում փաստաբան-հաճախորդ հարաբերություն։',
               send='Ուղարկել', sending='Ուղարկվում է...', ok='Շնորհակալություն։ Մենք ստացել ենք Ձեր հաղորդագրությունը և շուտով կկապվենք Ձեզ հետ։',
               err='Սխալ տեղի ունեցավ։ Խնդրում ենք զանգահարել կամ գրել', choose='Ընտրեք',
               cases=['Ավտովթար', 'Uber կամ Lyft վթար', 'Բեռնատարի վթար', 'Մոտոցիկլի վթար', 'Lemon Law (թերի մեքենա)', 'Սայթաքում և ընկնում', 'Այլ վնասվածք'],
               stars='5.0 Google-ում', armenian='Խոսում ենք հայերեն', office='Գրասենյակ', follow='Հետևեք մեզ',
               ad='Այս կայքը փաստաբանական գովազդ է։ Տեղեկատվությունը իրավաբանական խորհուրդ չէ։ Մեզ հետ կապվելը չի ստեղծում փաստաբան-հաճախորդ հարաբերություն։',
               home='Գլխավոր', skip='Անցնել բովանդակությանը', menu='Մենյու', call_now='Զանգահարել'),
    'es': dict(call='Llame', text='Envíenos un texto', review='Evaluación gratis', consult='Consulta gratis', nofee='No cobramos si no ganamos',
               form_title='Evaluación Gratis de Su Caso', form_sub='Cuéntenos qué pasó. Respondemos rápido.',
               name='Nombre completo', phone='Teléfono', email='Correo electrónico (opcional)', case='Tipo de caso', msg='¿Qué pasó?',
               consent='Acepto que me contacten sobre mi consulta. Enviar este formulario no crea una relación abogado-cliente.',
               send='Enviar', sending='Enviando...', ok='Gracias. Recibimos su mensaje y nos comunicaremos pronto.',
               err='Algo salió mal. Por favor llame o envíe un texto al', choose='Elija uno',
               cases=['Accidente de auto', 'Accidente de Uber o Lyft', 'Accidente de camión', 'Accidente de motocicleta', 'Lemon Law (auto defectuoso)', 'Resbalón y caída', 'Otra lesión'],
               stars='5.0 en Google', armenian='Hablamos armenio', office='Oficina', follow='Síganos',
               ad='Este sitio web es publicidad de abogados. La información es general y no es asesoría legal. Contactarnos no crea una relación abogado-cliente.',
               home='Inicio', skip='Ir al contenido', menu='Menú', call_now='Llamar'),
}

NAV = {
    'en': [
        ('Injury Cases', '/practice-areas/', [
            ('Car Accidents', '/practice-areas/car-accidents/'), ('Uber and Lyft Accidents', '/practice-areas/rideshare-accidents/'),
            ('Truck Accidents', '/practice-areas/truck-accidents/'), ('Motorcycle Accidents', '/practice-areas/motorcycle-accidents/'),
            ('Bicycle Accidents', '/practice-areas/bicycle-accidents/'), ('Bus Accidents', '/practice-areas/bus-accidents/'),
            ('Slip and Fall', '/practice-areas/slip-and-fall/'), ('Premises Liability', '/practice-areas/premises-liability/'),
            ('Dog Bites', '/practice-areas/dog-bite-injury/'), ('Wrongful Death', '/practice-areas/wrongful-death/')]),
        ('Lemon Law', '/practice-areas/lemon-law/', [
            ('California Lemon Law', '/practice-areas/lemon-law/'), ('Mercedes-Benz Lemon Law', '/lemon-law/mercedes-benz/'), ('Lemon Law by Brand', '/lemon-law/#brands'),
            ('Buyback Calculation', '/lemon-law/buyback-calculation/'), ('Used Cars', '/lemon-law/used-cars/'),
            ('Lemon Law FAQ', '/lemon-law/faq/')]),
        ('Areas We Serve', '/car-accident-lawyer/los-angeles-county/', [
            ('Los Angeles County', '/car-accident-lawyer/los-angeles-county/'), ('Los Angeles', '/car-accident-lawyer/los-angeles/'), ('Long Beach', '/car-accident-lawyer/long-beach/'), ('Santa Clarita', '/car-accident-lawyer/santa-clarita/'), ('Torrance', '/car-accident-lawyer/torrance/'), ('Glendale', '/car-accident-lawyer/glendale/'),
            ('Burbank', '/car-accident-lawyer/burbank/'), ('Pasadena', '/car-accident-lawyer/pasadena/'),
            ('Eagle Rock', '/service-areas/eagle-rock/'), ('Los Feliz', '/service-areas/los-feliz/'),
            ('North Hollywood', '/service-areas/north-hollywood/'), ('La Crescenta', '/service-areas/la-crescenta/')]),
        ('Guides', '/guides/', [
            ('After a Car Accident', '/guides/what-to-do-after-car-accident-california/'), ('Adjuster Tactics', '/guides/insurance-adjuster-tactics/'),
            ('What Is My Case Worth?', '/guides/car-accident-case-value-california/'), ('The Claim Process', '/guides/car-accident-claim-process/'),
            ('Blog', '/blog/')]),
        ('About', '/about/', []),
        ('Contact', '/contact/', []),
    ],
    'hy': [
        ('Ծառայություններ', '/hy/practice-areas/', [
            ('Ավտովթարներ', '/hy/practice-areas/car-accidents/'), ('Uber և Lyft', '/hy/practice-areas/rideshare-accidents/'),
            ('Բեռնատարներ', '/hy/practice-areas/truck-accidents/'), ('Մոտոցիկլներ', '/hy/practice-areas/motorcycle-accidents/'),
            ('Lemon Law', '/hy/practice-areas/lemon-law/')]),
        ('Գլենդեյլ', '/hy/car-accident-lawyer/glendale/', []),
        ('Մեր մասին', '/hy/about/', []),
        ('Կապ', '/hy/contact/', []),
    ],
    'es': [
        ('Accidentes de Auto', '/es/abogado-accidentes-de-auto/', []),
        ('Lemon Law', '/es/lemon-law/', []),
        ('Contacto', '/es/contacto/', []),
    ],
}

def lang_of(url):
    return 'hy' if url.startswith('/hy/') else 'es' if url.startswith('/es/') else 'en'

def sanitize(s):
    s = re.sub(r'\s*—\s*', ', ', s)
    s = re.sub(r'(\d)\s*–\s*(\d)', r'\1 to \2', s)
    s = re.sub(r'\s*–\s*', ', ', s)
    s = re.sub(r'[ \t]+,', ',', s)
    return s

def read(path):
    raw = path.read_text()
    m = re.match(r'^---\n(.*?)\n---\n?(.*)$', raw, re.S)
    fm, body = (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, raw)
    return fm, body

CTA_RE = re.compile(r'\[([^\]\n]+)\](?!\()')

def cta_html(label, s):
    l = label.lower()
    if re.search(r'\d{3}-\d{3}-\d{4}', label) or l.startswith(('call', 'llame', 'զանգ')):
        return f'<a class="btn btn-gold" href="tel:{FIRM["tel"]}">{label}</a>'
    if l.startswith(('text', 'envíe', 'gr')) and 'review' not in l:
        return f'<a class="btn btn-ghost" href="sms:{FIRM["sms"]}">{label}</a>'
    return f'<a class="btn btn-outline" href="#case-review">{label}</a>'

def render_md(body, s):
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    def line_ctas(m):
        line = m.group(0)
        if re.fullmatch(r'\s*(\*\*.*?\*\*\s*)?(\[[^\]\n]+\](?!\()\s*)+', line):
            lead = re.match(r'\s*(\*\*.*?\*\*)?', line).group(1) or ''
            btns = ''.join(cta_html(x, s) for x in CTA_RE.findall(line[len(lead):] if lead else line))
            lead_html = f'<p class="cta-lead">{markdown.markdown(lead)[3:-4]}</p>' if lead else ''
            return f'\n<div class="cta-row">{lead_html}<div class="cta-btns">{btns}</div></div>\n'
        return line
    body = re.sub(r'(?m)^.*\[[^\]\n]+\](?!\().*$', line_ctas, body)
    html = markdown.markdown(body, extensions=['extra', 'sane_lists', 'attr_list'])
    html = re.sub(r'<p>\s*(<a class="btn[^<]*</a>)\s*</p>', r'<div class="cta-btns">\1</div>', html)
    return html

def hero_image_for(url, fm):
    if fm.get('hero_image'):
        return fm['hero_image'].replace('.png', '.jpg')
    rules = [('lemon', '/images/practice-areas/lemon-law.jpg'), ('rideshare', '/images/practice-areas/rideshare-accidents.webp'),
             ('truck', '/images/practice-areas/truck-accidents.jpg'), ('motorcycle', '/images/practice-areas/motorcycle-accidents.jpg'),
             ('glendale', '/images/locations/glendale.jpg'), ('burbank', '/images/locations/burbank.jpg'), ('pasadena', '/images/locations/pasadena.jpg'),
             ('guides', '/images/courtroom.jpg'), ('car-accident', '/images/practice-areas/car-accidents.jpg'),
             ('abogado-accidentes', '/images/practice-areas/car-accidents.jpg'), ('contact', '/images/legal-office.jpg')]
    for k, v in rules:
        if k in url: return v
    return '/images/hero/glendale-poster.jpg'

CRUMB_MAP = {  # folder levels that are not pages themselves
    '/car-accident-lawyer/': ('Car Accidents', '/practice-areas/car-accidents/'),
    '/rideshare-accident-lawyer/': ('Uber and Lyft Accidents', '/practice-areas/rideshare-accidents/'),
    '/truck-accident-lawyer/': ('Truck Accidents', '/practice-areas/truck-accidents/'),
    '/motorcycle-accident-lawyer/': ('Motorcycle Accidents', '/practice-areas/motorcycle-accidents/'),
    '/service-areas/': ('Areas We Serve', '/car-accident-lawyer/los-angeles-county/'),
    '/lemon-law/defects/': ('Defects', '/lemon-law/'),
    '/practice-areas/': ('Practice Areas', '/practice-areas/'),
    '/lemon-law/': ('Lemon Law', '/lemon-law/'),
    '/guides/': ('Guides', '/guides/'),
    '/blog/': ('Blog', '/blog/'),
    '/hy/practice-areas/': ('Ծառայություններ', '/hy/practice-areas/'),
    '/hy/service-areas/': ('Ծառայության տարածքներ', '/hy/practice-areas/'),
    '/hy/car-accident-lawyer/': ('Ավտովթարներ', '/hy/practice-areas/car-accidents/'),
    '/hy/blog/': ('Բլոգ', '/hy/blog/'),
}

def breadcrumbs(url, fm, h1, s):
    parts = [p for p in url.strip('/').split('/') if p]
    crumbs = [(s['home'], '/hy/' if lang_of(url) == 'hy' else '/es/' if lang_of(url) == 'es' else '/')]
    acc = ''
    for i, p in enumerate(parts[:-1]):
        acc += '/' + p
        if acc in ('/hy', '/es'): continue
        if acc + '/' in CRUMB_MAP:
            crumbs.append(CRUMB_MAP[acc + '/'])
    if url not in ('/', '/hy/', '/es/'):
        crumbs.append((h1, url))
    return crumbs

def faq_from_body(html):
    """Pull Q&A pairs (h3 followed by p) under a 'Frequently Asked Questions' h2."""
    m = re.search(r'<h2[^>]*>(Frequently Asked Questions|Preguntas frecuentes|Հաճախ տրվող հարցեր)</h2>(.*?)(?=<h2|$)', html, re.S)
    if not m: return []
    return [(re.sub('<[^>]+>', '', q), re.sub('<[^>]+>', '', a)) for q, a in re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>', m.group(2), re.S)]

def jsonld(url, fm, h1, html, crumbs):
    org = {
        '@context': 'https://schema.org', '@type': 'LegalService', '@id': SITE + '/#firm', 'name': FIRM['name'],
        'url': SITE + '/', 'telephone': FIRM['tel'], 'email': FIRM['email'],
        'image': SITE + '/images/logo/prospect-law-group-full.png', 'logo': SITE + '/images/logo/prospect-law-group-full.png',
        'address': {'@type': 'PostalAddress', 'streetAddress': FIRM['street'], 'addressLocality': FIRM['city'],
                    'addressRegion': FIRM['region'], 'postalCode': FIRM['zip'], 'addressCountry': 'US'},
        'areaServed': [{'@type': 'AdministrativeArea', 'name': n} for n in
                       ['Los Angeles County', 'Orange County', 'Ventura County', 'Riverside County', 'San Bernardino County', 'California']],
        'knowsLanguage': ['en', 'hy'], 'priceRange': 'Free consultation',
        'founder': {'@type': 'Person', 'name': 'Vardan Daldumyan', 'jobTitle': 'Attorney'},
        'sameAs': list(FIRM['social'].values()),
    }
    out = [org]
    if url not in ('/', '/hy/', '/es/'):
        out.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(crumbs)]})
    faqs = [(f['q'], f['a']) for f in fm.get('faq', [])] or faq_from_body(html)
    if faqs:
        out.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]})
    return [json.dumps(o, ensure_ascii=False) for o in out]

CARD_IMAGES = [('rideshare', 'uber', 'rideshare-accidents.webp'), ('truck', 'բեռնատար', 'truck-accidents.jpg'),
               ('motorcycle', 'մոտոցիկլ', 'motorcycle-accidents.jpg'), ('lemon', 'lemon', 'lemon-law.jpg'),
               ('car', 'ավտո', 'car-accidents.jpg'), ('injur', 'վնասվ', 'slip-and-fall.jpg'), ('lesion', 'accidente', 'car-accidents.jpg')]

def home_sections(html):
    """Turn the homepage's flat Markdown into designed bands: practice cards, review cards."""
    chunks = re.split(r'(?=<h2)', html)
    out = []
    for i, c in enumerate(chunks):
        if not c.strip(): continue
        head = re.sub('<[^>]+>', '', c.split('</h2>')[0]).lower() if '<h2' in c else ''
        if any(k in head for k in ('practice areas', 'գործունեության', 'casos que')):
            cards = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>', c, re.S)
            items = re.findall(r'<li>(.*?)</li>', c, re.S) if not cards else []
            grid = []
            for title, body in cards or [(re.sub(r'</?strong>', '', it.split(':')[0].split('</strong>')[0]), it) for it in items]:
                t = re.sub('<[^>]+>', '', title).lower()
                img = next((f for a, b, f in CARD_IMAGES if a in t or b in t), 'car-accidents.jpg')
                link = re.search(r'href="([^"]+)"', body + title)
                href = link.group(1) if link else '#case-review'
                text = re.sub(r'\s*<a [^>]*>.*?</a>\.?', '', body)
                grid.append(f'<a class="pcard" href="{href}"><img src="/images/practice-areas/{img}" alt="" loading="lazy">'
                            f'<span class="pcard-body"><strong>{re.sub("<[^>]+>", "", title)}</strong><span>{re.sub("<[^>]+>", "", text) if cards else ""}</span></span></a>')
            rest = re.sub(r'<h3.*?</p>\s*', '', c, flags=re.S) if cards else re.sub(r'<ul>.*?</ul>', '', c, count=1, flags=re.S)
            h2 = re.search(r'<h2.*?</h2>', rest, re.S).group(0)
            rest = rest.replace(h2, '')
            out.append(f'<section class="hsec"><div class="wrap">{h2}<div class="pgrid">{"".join(grid)}</div>{rest}</div></section>')
            continue
        if '<blockquote>' in c:
            def rev(m):
                ps = re.findall(r'<p>(.*?)</p>', m.group(1), re.S)
                return '<div class="rgrid">' + ''.join(f'<figure class="rcard"><div class="stars" aria-label="5 stars">★★★★★</div><blockquote>{p}</blockquote></figure>' for p in ps) + '</div>'
            c = re.sub(r'<blockquote>(.*?)</blockquote>', rev, c, flags=re.S)
            c = re.sub(r'(<h2[^>]*)>', r'\1 id="reviews">', c, count=1)
        cls = 'hsec alt' if len(out) % 2 else 'hsec'
        out.append(f'<section class="{cls}"><div class="wrap narrow prose">{c}</div></section>')
    return ''.join(out)

# ---------- build ----------
def main():
    if DIST.exists(): shutil.rmtree(DIST)
    shutil.copytree(PUBLIC, DIST)
    env = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=False)
    tpl = env.get_template('page.html')
    reviews = json.loads((CONTENT / 'google-reviews.json').read_text()) if (CONTENT / 'google-reviews.json').exists() else []

    pages, redirects = [], dict(REMOVED)
    for f in sorted(CONTENT.rglob('*.md')):
        if f.name == 'README.md': continue
        fm, body = read(f)
        if not fm.get('url'): continue
        if fm.get('redirect'):
            redirects[fm['url']] = fm['redirect']; continue
        pages.append((fm, body))
    urls = {fm['url'] for fm, _ in pages}

    # language alternates
    alt = {}
    for fm, _ in pages:
        u = fm['url']; l = lang_of(u)
        en = fm.get('hreflang_en') or (u[3:] if l == 'hy' and u[3:] in urls else u if l == 'en' else None)
        if en: alt.setdefault(en, {})[l] = u
    def alternates(u):
        for en, d in alt.items():
            if u in d.values(): return {'en': en, **d} if en in urls else d
        return {}

    for fm, body in pages:
        url = fm['url']; lang = lang_of(url); s = STRINGS[lang]
        body = sanitize(body)
        html = render_md(body, s)
        is_home = url in ('/', '/hy/', '/es/')
        hero_html = ''
        if is_home and '<!-- /HERO -->' in body:
            hero_md, rest = body.split('<!-- /HERO -->', 1)
            hero_html, html = render_md(hero_md, s), home_sections(render_md(rest, s))
        h1 = sanitize(fm.get('h1') or fm.get('title', ''))
        title = sanitize(fm.get('title') or h1)
        desc = sanitize(fm.get('description', ''))
        crumbs = breadcrumbs(url, fm, h1, s)
        alts = alternates(url)
        out = tpl.render(
            url=url, lang=lang, s=s, firm=FIRM, nav=NAV[lang], title=title, description=desc, h1=h1,
            subtitle=sanitize(fm.get('subtitle', '')), hero_image=hero_image_for(url, fm), content=html, hero_html=hero_html,
            is_home=is_home, crumbs=crumbs, jsonld=jsonld(url, fm, h1, html, crumbs), alternates=alts,
            canonical=SITE + url, review_note=fm.get('review_note'), ga_id=GA_ID, ads_id=ADS_ID, reviews=reviews,
            year=datetime.date.today().year, is_contact=url in ('/contact/', '/hy/contact/', '/es/contacto/'))
        dest = DIST / url.strip('/') / 'index.html' if url != '/' else DIST / 'index.html'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out)

    for old, new in redirects.items():
        d = DIST / old.strip('/') / 'index.html'
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(f'<!doctype html><html><head><meta charset="utf-8"><title>Redirecting</title>'
                     f'<meta name="robots" content="noindex"><link rel="canonical" href="{SITE}{new}">'
                     f'<meta http-equiv="refresh" content="0;url={new}"></head><body><a href="{new}">Continue</a></body></html>')
    (DIST / '_redirects.json').write_text(json.dumps(redirects, indent=1))

    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sorted(urls):
        sm.append(f'<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>')
    sm.append('</urlset>')
    (DIST / 'sitemap.xml').write_text('\n'.join(sm))
    (DIST / 'sitemap-index.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>{SITE}/sitemap.xml</loc></sitemap></sitemapindex>')
    (DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap-index.xml\n')
    fm404 = {'url': '/404/'}
    (DIST / '404.html').write_text(tpl.render(url='/404/', lang='en', s=STRINGS['en'], firm=FIRM, nav=NAV['en'], title='Page Not Found | Prospect Law Group',
        description='', h1='Page Not Found', subtitle='The page you are looking for moved. Try the links below or call us.',
        hero_image='/images/hero/glendale-poster.jpg', content='<p><a href="/">Home</a> · <a href="/practice-areas/car-accidents/">Car Accidents</a> · <a href="/practice-areas/lemon-law/">Lemon Law</a> · <a href="/contact/">Contact</a></p>',
        hero_html='', is_home=False, crumbs=[('Home', '/')], jsonld=[], alternates={}, canonical=SITE + '/404/', review_note=None,
        ga_id=GA_ID, ads_id=ADS_ID, reviews=reviews, year=datetime.date.today().year, is_contact=False, noindex=True))
    print(f'Built {len(pages)} pages, {len(redirects)} redirects -> {DIST}')

def make_preview(base):
    """Copy dist/ to preview/ with every root link prefixed by base (for a GitHub Pages preview) and noindex everywhere."""
    P = ROOT / 'preview'
    if P.exists(): shutil.rmtree(P)
    shutil.copytree(DIST, P)
    for f in P.rglob('*.html'):
        t = f.read_text()
        t = re.sub(r'(href|src|poster|content)="/(?!/)', lambda m: f'{m.group(1)}="{base}/', t)
        t = re.sub(r"url\('/", f"url('{base}/", t)
        t = t.replace('<head>', '<head><meta name="robots" content="noindex, nofollow">', 1)
        f.write_text(t)
    (P / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (P / '.nojekyll').write_text('')
    print('Preview ->', P)

if __name__ == '__main__':
    import sys
    main()
    if '--preview' in sys.argv:
        make_preview(sys.argv[sys.argv.index('--preview') + 1])
