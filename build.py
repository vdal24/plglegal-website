#!/usr/bin/env python3
"""Static site generator for plglegal.com.

Usage: python3 build.py   ->  writes the finished site to dist/
Content lives in content/ (Markdown + YAML frontmatter). Assets live in public/.
Requires: markdown, pyyaml, jinja2 (pip install markdown pyyaml jinja2). Optional: pillow (smaller image copies).
"""
import json, re, shutil, pathlib, datetime
import yaml, markdown
from jinja2 import Environment, FileSystemLoader

ROOT = pathlib.Path(__file__).parent
CONTENT, PUBLIC, DIST = ROOT / 'content', ROOT / 'public', ROOT / 'dist'
SITE = 'https://plglegal.com'
GA_ID = ''           # Google Analytics 4 ID, e.g. 'G-XXXXXXX' (leave blank until created)
ADS_ID = 'AW-18436695999'  # Google Ads tag (conversion labels live in public/js/site.js)

FIRM = {
    'name': 'Prospect Law Group, PC',
    'short': 'Prospect Law Group',
    'phone': '323-452-5222', 'tel': '+13234525222',
    'sms': '+13234525222', 'sms_display': '323-452-5222',
    'email': 'contact@plglegal.com',
    'street': '600 W. Broadway, Ste. 320', 'city': 'Glendale', 'region': 'CA', 'zip': '91204',
    'maps': 'https://www.google.com/maps/search/?api=1&query=Prospect+Law+Group+600+W+Broadway+Suite+320+Glendale+CA+91204',
    'social': {'Instagram': 'https://instagram.com/plglegal'},
    'attorney': 'Vardan Daldumyan',
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
               send='Get My Free Case Review', sending='Sending...', ok='Thank you. We received your message and will contact you shortly.',
               err='Something went wrong. Please call or text us at', choose='Choose one',
               cases=['Car accident', 'Uber or Lyft accident', 'Truck or commercial vehicle accident', 'Motorcycle accident', 'Serious injury or wrongful death', 'Lemon law (defective car)', 'Slip and fall or premises', 'Other injury'],
               stars='5.0 on Google', armenian='We speak Armenian', office='Office', follow='Follow us',
               ad='This website is attorney advertising. The information on this site is general information, not legal advice. Contacting us does not create an attorney-client relationship.',
               home='Home', skip='Skip to content', menu='Menu', call_now='Call Now',
               form_note='Free and confidential. No obligation.', atty_name='Vardan Daldumyan, Esq.',
               atty_role='Former insurance company trial attorney',
               cta_h='Talk to an Attorney Today',
               cta_p='Free, confidential consultation by phone, video, or in person. If we take your case, you pay nothing unless we recover.',
               reviews_h='What Our Clients Say', google_review='Google review', reviews_link='Read all reviews on Google',
               reviews_note='Testimonials reflect individual client experiences. Every case is different, and past results do not guarantee or predict a similar outcome.',
               trust_langs='We speak Armenian · Español', direct='You work directly with your attorney',
               remote='Phone, video, or in-person meetings', about=('About the attorney', '/about/'),
               resources='Resources', legal='Legal', areas='Areas We Serve'),
    'hy': dict(call='Զանգահարել', text='Գրել SMS', review='Անվճար գնահատում', consult='Անվճար խորհրդատվություն', nofee='Վճար միայն հաղթանակի դեպքում',
               form_title='Անվճար գործի գնահատում', form_sub='Պատմեք, թե ինչ է պատահել։ Մենք արագ կպատասխանենք։',
               name='Անուն ազգանուն', phone='Հեռախոս', email='Էլ. փոստ (ըստ ցանկության)', case='Գործի տեսակ', msg='Ի՞նչ է պատահել',
               consent='Համաձայն եմ, որ ինձ հետ կապվեն։ Այս ձևը ուղարկելը չի ստեղծում փաստաբան-հաճախորդ հարաբերություն։',
               send='Ուղարկել անվճար գնահատման', sending='Ուղարկվում է...', ok='Շնորհակալություն։ Մենք ստացել ենք Ձեր հաղորդագրությունը և շուտով կկապվենք Ձեզ հետ։',
               err='Սխալ տեղի ունեցավ։ Խնդրում ենք զանգահարել կամ գրել', choose='Ընտրեք',
               cases=['Ավտովթար', 'Uber կամ Lyft վթար', 'Բեռնատարի վթար', 'Մոտոցիկլի վթար', 'Lemon Law (թերի մեքենա)', 'Սայթաքում և ընկնում', 'Այլ վնասվածք'],
               stars='5.0 Google-ում', armenian='Խոսում ենք հայերեն', office='Գրասենյակ', follow='Հետևեք մեզ',
               ad='Այս կայքը փաստաբանական գովազդ է։ Տեղեկատվությունը իրավաբանական խորհուրդ չէ։ Մեզ հետ կապվելը չի ստեղծում փաստաբան-հաճախորդ հարաբերություն։',
               home='Գլխավոր', skip='Անցնել բովանդակությանը', menu='Մենյու', call_now='Զանգահարել',
               form_note='Անվճար և գաղտնի։ Առանց պարտավորության։', atty_name='Վարդան Դալդումյան, փաստաբան',
               atty_role='Ապահովագրական ընկերության նախկին դատական փաստաբան',
               cta_h='Խոսեք փաստաբանի հետ այսօր',
               cta_p='Անվճար և գաղտնի խորհրդատվություն հեռախոսով, տեսազանգով կամ անձամբ։ Եթե ստանձնենք Ձեր գործը, Դուք ոչինչ չեք վճարում, քանի դեռ փոխհատուցում չենք ստացել։',
               reviews_h='Մեր հաճախորդների կարծիքները', google_review='Google կարծիք', reviews_link='Տեսնել բոլոր կարծիքները Google-ում',
               reviews_note='Կարծիքներն արտացոլում են առանձին հաճախորդների փորձը (անգլերենով)։ Յուրաքանչյուր գործ տարբեր է, և նախկին արդյունքները չեն երաշխավորում նմանատիպ արդյունք։',
               trust_langs='Խոսում ենք հայերեն · Español', direct='Դուք անմիջապես աշխատում եք Ձեր փաստաբանի հետ',
               remote='Հանդիպում հեռախոսով, տեսազանգով կամ անձամբ', about=('Փաստաբանի մասին', '/hy/about/'),
               resources='Օգտակար', legal='Իրավական', areas='Տարածքներ'),
    'es': dict(call='Llame', text='Envíenos un texto', review='Evaluación gratis', consult='Consulta gratis', nofee='No cobramos si no ganamos',
               form_title='Evaluación Gratis de Su Caso', form_sub='Cuéntenos qué pasó. Respondemos rápido.',
               name='Nombre completo', phone='Teléfono', email='Correo electrónico (opcional)', case='Tipo de caso', msg='¿Qué pasó?',
               consent='Acepto que me contacten sobre mi consulta. Enviar este formulario no crea una relación abogado-cliente.',
               send='Solicitar evaluación gratis', sending='Enviando...', ok='Gracias. Recibimos su mensaje y nos comunicaremos pronto.',
               err='Algo salió mal. Por favor llame o envíe un texto al', choose='Elija uno',
               cases=['Accidente de auto', 'Accidente de Uber o Lyft', 'Accidente de camión', 'Accidente de motocicleta', 'Lemon Law (auto defectuoso)', 'Resbalón y caída', 'Otra lesión'],
               stars='5.0 en Google', armenian='Atención en español', office='Oficina', follow='Síganos',
               ad='Este sitio web es publicidad de abogados. La información es general y no es asesoría legal. Contactarnos no crea una relación abogado-cliente.',
               home='Inicio', skip='Ir al contenido', menu='Menú', call_now='Llamar',
               form_note='Gratis y confidencial. Sin compromiso.', atty_name='Vardan Daldumyan, Esq.',
               atty_role='Ex abogado litigante de una compañía de seguros',
               cta_h='Hable con un abogado hoy',
               cta_p='Consulta gratis y confidencial por teléfono, video o en persona. Si tomamos su caso, no paga nada a menos que obtengamos una compensación.',
               reviews_h='Lo que dicen nuestros clientes', google_review='Reseña de Google', reviews_link='Ver todas las reseñas en Google',
               reviews_note='Los testimonios reflejan experiencias individuales de clientes (reseñas en inglés). Cada caso es diferente y los resultados anteriores no garantizan un resultado similar.',
               trust_langs='Atención en español · Հայերեն', direct='Trato directo con su abogado',
               remote='Citas por teléfono, video o en persona', about=None,
               resources='Recursos', legal='Legal', areas='Áreas de servicio'),
}

NAV = {
    'en': [
        ('Injury Cases', '/practice-areas/', [
            ('Car Accidents', '/practice-areas/car-accidents/'), ('Uber and Lyft Accidents', '/practice-areas/rideshare-accidents/'),
            ('Truck Accidents', '/practice-areas/truck-accidents/'), ('Commercial Vehicle Accidents', '/practice-areas/commercial-vehicle-accidents/'),
            ('Catastrophic Injuries', '/practice-areas/catastrophic-injury/'), ('Wrongful Death', '/practice-areas/wrongful-death/'),
            ('Uninsured Motorist Claims', '/practice-areas/uninsured-motorist-claims/'), ('Motorcycle Accidents', '/practice-areas/motorcycle-accidents/'),
            ('Bicycle Accidents', '/practice-areas/bicycle-accidents/'), ('Bus Accidents', '/practice-areas/bus-accidents/'),
            ('Slip and Fall', '/practice-areas/slip-and-fall/'), ('Premises Liability', '/practice-areas/premises-liability/'),
            ('Dog Bites', '/practice-areas/dog-bite-injury/'), ('All Practice Areas', '/practice-areas/')]),
        ('Lemon Law', '/practice-areas/lemon-law/', [
            ('Mercedes-Benz Lemon Law', '/lemon-law/mercedes-benz/'), ('California Lemon Law', '/practice-areas/lemon-law/'), ('Lemon Law by Brand', '/lemon-law/#brands'),
            ('Buyback Calculation', '/lemon-law/buyback-calculation/'), ('Used Cars', '/lemon-law/used-cars/'),
            ('Lemon Law FAQ', '/lemon-law/faq/')]),
        ('Areas We Serve', '/car-accident-lawyer/los-angeles-county/', [
            ('Los Angeles County', '/car-accident-lawyer/los-angeles-county/'), ('Los Angeles', '/car-accident-lawyer/los-angeles/'), ('Long Beach', '/car-accident-lawyer/long-beach/'), ('Santa Clarita', '/car-accident-lawyer/santa-clarita/'), ('Torrance', '/car-accident-lawyer/torrance/'), ('Inland Empire', '/car-accident-lawyer/inland-empire/'), ('Glendale', '/car-accident-lawyer/glendale/'),
            ('Burbank', '/car-accident-lawyer/burbank/'), ('Pasadena', '/car-accident-lawyer/pasadena/'),
            ('Eagle Rock', '/service-areas/eagle-rock/'), ('Los Feliz', '/service-areas/los-feliz/'),
            ('North Hollywood', '/service-areas/north-hollywood/'), ('La Crescenta', '/service-areas/la-crescenta/')]),
        ('Guides', '/guides/', [
            ('After a Car Accident', '/guides/what-to-do-after-car-accident-california/'), ('Adjuster Tactics', '/guides/insurance-adjuster-tactics/'),
            ('What Is My Case Worth?', '/guides/car-accident-case-value-california/'), ('The Claim Process', '/guides/car-accident-claim-process/'),
            ('Lowball Insurance Offer?', '/guides/lowball-insurance-offer/'), ('Switching Lawyers', '/guides/switching-lawyers/'),
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
    if l.startswith(('text', 'envíe', 'gr', 'գր', 'sms')) and 'review' not in l:
        return f'<a class="btn btn-ghost" href="sms:{FIRM["sms"]}">{label}</a>'
    return f'<a class="btn btn-outline" href="#case-review">{label}</a>'

def render_md(body, s):
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    def line_ctas(m):
        # A line made only of [Button] labels becomes a button row. [Label](/url/) on such a line becomes a link button.
        line = m.group(0)
        tok = r'\[[^\]\n]+\](?:\([^)\s]+\))?'
        if re.fullmatch(r'\s*(\*\*.*?\*\*\s*)?(' + tok + r'\s*)+', line) and re.search(r'\[[^\]\n]+\](?!\()', line):
            lead = re.match(r'\s*(\*\*.*?\*\*)?', line).group(1) or ''
            btns = ''
            for label, href in re.findall(r'\[([^\]\n]+)\](?:\(([^)\s]+)\))?', line[len(lead):] if lead else line):
                btns += f'<a class="btn btn-outline" href="{href}">{label}</a>' if href else cta_html(label, s)
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
    rules = [('catastrophic', '/images/hero/mri-image.jpg'), ('commercial-vehicle', '/images/practice-areas/truck-accidents.jpg'), ('uninsured', '/images/practice-areas/car-accidents.jpg'), ('lowball', '/images/legal-office.jpg'), ('switching', '/images/office.jpg'), ('lemon', '/images/practice-areas/lemon-law.jpg'), ('rideshare', '/images/practice-areas/rideshare-accidents.webp'),
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

FAQ_H2 = r'<h2[^>]*>(?:Frequently Asked Questions|Preguntas frecuentes|Հաճախ տրվող հարցեր)</h2>'

def faq_from_body(html):
    """Pull Q&A pairs (h3 followed by p) under a 'Frequently Asked Questions' h2."""
    m = re.search('(' + FAQ_H2 + r')(.*?)(?=<h2|$)', html, re.S)
    if not m: return []
    return [(re.sub('<[^>]+>', '', q), re.sub('<[^>]+>', '', a)) for q, a in re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>', m.group(2), re.S)]

def faq_accordion(html):
    """Turn the FAQ section (h3 question + answer blocks) into tap-to-open rows. Content stays in the page for search engines."""
    m = re.search('(' + FAQ_H2 + r')(.*?)(?=<h2|$)', html, re.S)
    if not m or '<h3' not in m.group(2): return html
    sec = m.group(2)
    pre, *items = re.split(r'(?=<h3)', sec)
    out, tail = [], ''
    for i, it in enumerate(items):
        q = re.match(r'<h3[^>]*>(.*?)</h3>', it, re.S)
        if not q: out.append(it); continue
        ans = it[q.end():]
        if i == len(items) - 1:  # keep closing notes (related links, disclaimers, buttons) outside the last answer
            cut = re.search(r'<p>\s*<small|<small|<div class="cta|<hr|<p>(?:Related|Local pages|More|See also|Relacionado|Ver también)\b[^<]{0,40}:', ans)
            if cut: ans, tail = ans[:cut.start()], ans[cut.start():]
        out.append(f'<details class="faq"><summary><h3>{q.group(1)}</h3></summary><div class="faq-a">{ans.strip()}</div></details>')
    return html[:m.start(2)] + pre + '<div class="faqs">' + ''.join(out) + '</div>' + tail + html[m.end(2):]

def mark_steps(html):
    """An ordered list under an h2 marked {: .sec-steps} becomes a numbered step layout."""
    return re.sub(r'(<h2[^>]*class="[^"]*sec-steps[^"]*"[^>]*>.*?</h2>(?:(?!<h2).)*?)<ol>', r'\1<ol class="steps">', html, flags=re.S)

def jsonld(url, fm, h1, html, crumbs, desc=''):
    lang = lang_of(url)
    person = {
        '@type': 'Person', '@id': SITE + '/about/#attorney', 'name': FIRM['attorney'], 'jobTitle': 'Attorney',
        'honorificSuffix': 'Esq.', 'url': SITE + '/about/',
        'knowsLanguage': ['en', 'hy'], 'worksFor': {'@id': SITE + '/#firm'},
        'description': 'Founder of Prospect Law Group, PC. Former in-house trial attorney for an insurance company.',
    }
    org = {
        '@context': 'https://schema.org', '@type': ['LegalService', 'Attorney'], '@id': SITE + '/#firm', 'name': FIRM['name'],
        'url': SITE + '/', 'telephone': FIRM['tel'], 'email': FIRM['email'],
        'image': SITE + '/images/logo/prospect-law-group-full.png', 'logo': SITE + '/images/logo/prospect-law-group-full.png',
        'address': {'@type': 'PostalAddress', 'streetAddress': FIRM['street'], 'addressLocality': FIRM['city'],
                    'addressRegion': FIRM['region'], 'postalCode': FIRM['zip'], 'addressCountry': 'US'},
        'hasMap': FIRM['maps'],
        'areaServed': [{'@type': 'AdministrativeArea', 'name': n} for n in
                       ['Los Angeles County', 'Orange County', 'Ventura County', 'Riverside County', 'San Bernardino County', 'California']],
        'knowsLanguage': ['en', 'hy', 'es'], 'availableLanguage': ['English', 'Armenian', 'Spanish'], 'priceRange': 'Free consultation',
        'knowsAbout': ['Personal injury law', 'Car accident claims', 'Truck accident claims', 'Rideshare accident claims',
                       'Wrongful death claims', 'Uninsured motorist claims', 'California lemon law', 'Song-Beverly Consumer Warranty Act'],
        'founder': person if url in ('/', '/about/') else {'@type': 'Person', '@id': SITE + '/about/#attorney', 'name': FIRM['attorney'], 'jobTitle': 'Attorney'},
        'sameAs': list(FIRM['social'].values()),
    }
    out = [org]
    if url == '/':
        out.append({'@context': 'https://schema.org', '@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/',
                    'name': FIRM['short'], 'publisher': {'@id': SITE + '/#firm'}, 'inLanguage': ['en-US', 'hy', 'es']})
    if url.startswith('/guides/') and url != '/guides/' or url.startswith('/blog/') and url != '/blog/':
        out.append({'@context': 'https://schema.org', '@type': 'Article', 'headline': h1, 'description': desc,
                    'mainEntityOfPage': SITE + url, 'inLanguage': 'en-US',
                    'author': {'@type': 'Person', '@id': SITE + '/about/#attorney', 'name': FIRM['attorney'], 'url': SITE + '/about/'},
                    'publisher': {'@id': SITE + '/#firm'}})
    if url not in ('/', '/hy/', '/es/'):
        out.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(crumbs)]})
    faqs = [(f['q'], f['a']) for f in fm.get('faq', [])] or faq_from_body(html)
    if faqs:
        out.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]})
    return [json.dumps(o, ensure_ascii=False) for o in out]

# ---------- images ----------
_VARIANTS = {}
def variant(src, width, q=78):
    """Smaller JPEG copy of a photo for cards and thumbnails. Returns (url, w, h); falls back to the original file."""
    key = (src, width)
    if key in _VARIANTS: return _VARIANTS[key]
    res = (src, None, None)
    try:
        from PIL import Image
        im = Image.open(PUBLIC / src.lstrip('/'))
        w, h = im.size
        if w > width:
            im = im.convert('RGB').resize((width, round(h * width / w)), Image.LANCZOS)
        else:
            im = im.convert('RGB')
        name = src.lstrip('/').replace('images/', '', 1).rsplit('.', 1)[0].replace('/', '-') + '.jpg'
        dest = DIST / 'images' / f'w{width}' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, 'JPEG', quality=q, optimize=True, progressive=True)
        res = (f'/images/w{width}/{name}', im.size[0], im.size[1])
    except Exception:
        pass
    _VARIANTS[key] = res
    return res

def img_tag(src, width, alt='', cls='', lazy=True):
    u, w, h = variant(src, width)
    dims = f' width="{w}" height="{h}"' if w else ''
    return f'<img src="{u}" alt="{alt}"{dims}{" class=" + chr(34) + cls + chr(34) if cls else ""}{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""} decoding="async">'

def shrink_images(html):
    """Content images: serve a web-sized copy, add dimensions and lazy loading."""
    def one(m):
        tag = m.group(0); src = m.group(1)
        if not src.startswith('/images/') or '/logo/' in src: return tag
        u, w, h = variant(src, 720)
        tag = tag.replace(f'src="{src}"', f'src="{u}"')
        if w and 'width=' not in tag: tag = tag.replace('<img ', f'<img width="{w}" height="{h}" ', 1)
        if 'loading=' not in tag: tag = tag.replace('<img ', '<img loading="lazy" decoding="async" ', 1)
        return tag
    return re.sub(r'<img [^>]*?src="([^"]+)"[^>]*>', one, html)

CARD_IMAGES = [(('uber', 'lyft', 'rideshare'), '/images/practice-areas/rideshare-accidents.webp'),
               (('catastrophic', 'catastróf', 'ծանր'), '/images/hero/mri-image.jpg'),
               (('wrongful', 'muerte', 'մահ'), '/images/practice-areas/wrongful-death.webp'),
               (('truck', 'commercial', 'camion', 'camión', 'բեռնատար'), '/images/practice-areas/truck-accidents.jpg'),
               (('motorcycle', 'motocicleta', 'մոտոցիկլ'), '/images/practice-areas/motorcycle-accidents.jpg'),
               (('lemon',), '/images/practice-areas/lemon-law.jpg'),
               (('bicycle',), '/images/practice-areas/bicycle-accidents.jpg'), (('bus ',), '/images/practice-areas/bus-accidents.webp'),
               (('dog',), '/images/practice-areas/dog-bite-injury.jpg'), (('premises',), '/images/practice-areas/premises-liability.jpg'),
               (('slip', 'resbal', 'lesiones', 'վնասվածք', 'սայթաք'), '/images/practice-areas/slip-and-fall.jpg'),
               (('car', 'auto', 'ավտո', 'uninsured'), '/images/practice-areas/car-accidents.jpg')]

def card_grid(c):
    """h3 + paragraph (with a link) pairs -> photo cards."""
    cards = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>', c, re.S)
    grid = []
    for title, body in cards:
        tt = re.sub('<[^>]+>', '', title)
        t = tt.lower() + ' '
        img = next((f for keys, f in CARD_IMAGES if any(k in t for k in keys)), '/images/practice-areas/car-accidents.jpg')
        link = re.search(r'href="([^"]+)"', body + title)
        more = re.search(r'<a [^>]*>(.*?)</a>', body, re.S)
        href = link.group(1) if link else '#case-review'
        text = re.sub('<[^>]+>', '', re.sub(r'\s*<a [^>]*>.*?</a>\.?', '', body))
        more_html = f'<em>{re.sub("<[^>]+>", "", more.group(1))} <i aria-hidden="true">&rarr;</i></em>' if more else ''
        grid.append(f'<a class="pcard" href="{href}">{img_tag(img, 640)}'
                    f'<span class="pcard-body"><strong>{tt}</strong><span>{text}</span>{more_html}</span></a>')
    rest = re.sub(r'<h3.*?</p>\s*', '', c, flags=re.S)
    h2 = re.search(r'<h2.*?</h2>', rest, re.S).group(0)
    return h2, f'<div class="pgrid">{"".join(grid)}</div>', rest.replace(h2, '')

def link_grid(c):
    """h3 + paragraph (with a link) pairs -> text cards."""
    cards = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>', c, re.S)
    grid = []
    for title, body in cards:
        link = re.search(r'href="([^"]+)"', body)
        more = re.search(r'<a [^>]*>(.*?)</a>', body, re.S)
        text = re.sub('<[^>]+>', '', re.sub(r'\s*<a [^>]*>.*?</a>\.?', '', body))
        grid.append(f'<a class="lcard" href="{link.group(1) if link else "#case-review"}"><strong>{re.sub("<[^>]+>", "", title)}</strong>'
                    f'<span>{text}</span><em>{re.sub("<[^>]+>", "", more.group(1)) if more else ""} <i aria-hidden="true">&rarr;</i></em></a>')
    rest = re.sub(r'<h3.*?</p>\s*', '', c, flags=re.S)
    h2 = re.search(r'<h2.*?</h2>', rest, re.S).group(0)
    return h2, f'<div class="lgrid">{"".join(grid)}</div>', rest.replace(h2, '')

def review_cards(c):
    def rev(m):
        ps = re.findall(r'<p>(.*?)</p>', m.group(1), re.S)
        return '<div class="rgrid">' + ''.join(f'<figure class="rcard"><div class="stars" role="img" aria-label="5 stars">★★★★★</div><blockquote>{p}</blockquote></figure>' for p in ps) + '</div>'
    c = re.sub(r'<blockquote>(.*?)</blockquote>', rev, c, flags=re.S)
    c = re.sub(r'</div>\s*<div class="rgrid">', '', c)
    return re.sub(r'<h2', '<h2 id="reviews"', c, count=1)

def interior_sections(html):
    """Interior pages: an h2 marked sec-cards or sec-links turns its h3 + paragraph pairs into a card grid."""
    if 'sec-cards' not in html and 'sec-links' not in html: return html
    out = []
    for c in re.split(r'(?=<h2)', html):
        h2tag = re.match(r'<h2[^>]*>', c)
        kind = (re.search(r'sec-(cards|links)', h2tag.group(0)) or [None, ''])[1] if h2tag else ''
        if kind and '<h3' in c:
            h2, grid, rest = (card_grid if kind == 'cards' else link_grid)(c)
            c = h2 + grid + rest
        out.append(c)
    return ''.join(out)

def home_sections(html, s):
    """Turn the homepage's flat Markdown into designed bands. A section's look is chosen by a class on its h2,
    e.g. '## Title {: .sec-cards }'. Kinds: sec-cards, sec-links, sec-about, sec-steps, sec-dark. Reviews are detected by blockquotes."""
    chunks = re.split(r'(?=<h2)', html)
    out, flip = [], False
    for c in chunks:
        if not c.strip(): continue
        h2tag = re.match(r'<h2[^>]*>', c)
        kind = (re.search(r'sec-(\w+)', h2tag.group(0)) or [None, ''])[1] if h2tag else ''
        head = re.sub('<[^>]+>', '', c.split('</h2>')[0]).lower() if h2tag else ''
        if not kind and any(k in head for k in ('practice areas', 'գործունեության', 'casos que')) and '<h3' in c: kind = 'cards'
        c = faq_accordion(mark_steps(c))
        if kind == 'dark':
            out.append(f'<section class="hsec dark"><div class="wrap narrow prose">{c}</div></section>'); flip = False
            continue
        cls = 'hsec alt' if flip else 'hsec'
        flip = not flip
        if kind in ('cards', 'links') and '<h3' in c:
            h2, grid, rest = (card_grid if kind == 'cards' else link_grid)(c)
            out.append(f'<section class="{cls}"><div class="wrap">{h2}{grid}{rest}</div></section>')
        elif kind == 'about' and '<img' in c:
            img = re.search(r'<p>\s*(<img [^>]*>)\s*</p>', c, re.S)
            src = re.search(r'src="([^"]+)"', img.group(1)).group(1)
            alt = (re.search(r'alt="([^"]*)"', img.group(1)) or [None, ''])[1]
            c = c.replace(img.group(0), '')
            cap = f'<figcaption><strong>{s["atty_name"]}</strong><span>{s["atty_role"]}</span><span>{s["bar"]}</span></figcaption>'
            out.append(f'<section class="{cls}"><div class="wrap about-band"><figure class="about-photo">{img_tag(src, 720, alt)}{cap}</figure><div class="prose">{c}</div></div></section>')
        elif '<blockquote>' in c:
            out.append(f'<section class="{cls}"><div class="wrap prose wide">{review_cards(c)}</div></section>')
        elif kind == 'steps':
            out.append(f'<section class="{cls}"><div class="wrap prose wide">{c}</div></section>')
        else:
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
        h1 = sanitize(fm.get('h1') or fm.get('title', ''))
        title = sanitize(fm.get('title') or h1)
        desc = sanitize(fm.get('description', ''))
        crumbs = breadcrumbs(url, fm, h1, s)
        alts = alternates(url)
        ld = jsonld(url, fm, h1, html, crumbs, desc)   # schema is read from the plain HTML, before layout changes
        if is_home and '<!-- /HERO -->' in body:
            hero_md, rest = body.split('<!-- /HERO -->', 1)
            hero_html, html = render_md(hero_md, s), home_sections(render_md(rest, s), s)
        else:
            html = shrink_images(faq_accordion(mark_steps(interior_sections(html))))
        side_reviews = [r for r in reviews if len(r['text']) < 260][:3]
        headshot = ''
        out = tpl.render(
            url=url, lang=lang, s=s, firm=FIRM, nav=NAV[lang], title=title, description=desc, h1=h1,
            subtitle=sanitize(fm.get('subtitle', '')), hero_image=hero_image_for(url, fm), hero_bg=variant(hero_image_for(url, fm), 1280, 60)[0],   # page-top photo sits under a dark overlay, so a lighter file is fine
             content=html, hero_html=hero_html,
            is_home=is_home, crumbs=crumbs, jsonld=ld, alternates=alts, side_reviews=side_reviews, headshot=headshot,
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
        hero_image='/images/hero/glendale-poster.jpg', hero_bg='/images/hero/glendale-poster.jpg', content='<p><a href="/">Home</a> · <a href="/practice-areas/">Practice Areas</a> · <a href="/practice-areas/car-accidents/">Car Accidents</a> · <a href="/practice-areas/lemon-law/">Lemon Law</a> · <a href="/lemon-law/mercedes-benz/">Mercedes-Benz Lemon Law</a> · <a href="/guides/">Guides</a> · <a href="/contact/">Contact</a></p>',
        hero_html='', is_home=False, crumbs=[('Home', '/')], jsonld=[], alternates={}, canonical=SITE + '/404/', review_note=None,
        ga_id=GA_ID, ads_id=ADS_ID, reviews=reviews, year=datetime.date.today().year, is_contact=False, noindex=True,
        side_reviews=[r for r in reviews if len(r['text']) < 260][:3], headshot=''))
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
