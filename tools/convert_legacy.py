"""One-time: convert legacy plglegal.com pages (from backup) into Markdown content files."""
import sys, re, pathlib, yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md

SRC = pathlib.Path(sys.argv[1])      # backup/site
OUT = pathlib.Path(sys.argv[2])      # content/legacy
SKIP = {'/', '/hy/', '/results/', '/testimonials/', '/hy/results/', '/hy/testimonials/',
        '/practice-areas/car-accidents/', '/practice-areas/rideshare-accidents/', '/practice-areas/lemon-law/',
        '/hy/practice-areas/lemon-law/', '/contact/', '/hy/contact/'}
BANNED = [r'We Fight\.?\s*You Win\.?', r'Millions Recovered', r'Proven Track Record']

def clean_text(s):
    s = s.replace('—', ', ').replace('–', ' to ')
    return s

urls = re.findall(r'<loc>https://plglegal.com(.*?)</loc>', (SRC/'sitemap-0.xml').read_text())
for u in urls:
    if u in SKIP: continue
    f = SRC / u.strip('/') / 'index.html' if u != '/' else SRC/'index.html'
    raw = f.read_text()
    soup = BeautifulSoup(raw, 'html.parser')
    ref = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if ref:
        target = ref['content'].split('url=')[1]
        dest = OUT / (u.strip('/').replace('/', '__') + '.md')
        dest.write_text('---\n' + yaml.safe_dump({'url': u, 'redirect': target}, sort_keys=False) + '---\n')
        print(u, 'redirect', target); continue
    title = soup.title.get_text(strip=True) if soup.title else ''
    desc = (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', '')
    main = soup.find('main') or soup.find(id='main-content') or soup.body
    for t in main(['script', 'style', 'svg', 'astro-island', 'form', 'noscript', 'button']): t.decompose()
    sections = main.find_all(['section','article'], recursive=False) or [main]
    hero = sections[0]
    h1 = hero.find('h1')
    h1t = h1.get_text(' ', strip=True) if h1 else title
    sub = h1.find_next('p') if h1 else None
    subt = sub.get_text(' ', strip=True) if sub and sub in hero.descendants else ''
    img = hero.find('img')
    hero_img = img.get('src') if img else None
    body = []
    rest = sections[1:] if h1 else sections
    for sec in rest:
        txt = sec.get_text(' ', strip=True)
        if re.search(r'Free Consultation\s*$', txt) and sec.find('a', class_=re.compile('btn')) and len(txt) < 400:
            continue  # closing CTA band
        for a in sec.find_all('aside'): a.decompose()
        for d in sec.find_all('details'):
            q = d.find('summary'); qt = q.get_text(' ', strip=True) if q else ''
            if q: q.decompose()
            new = soup.new_tag('div'); h = soup.new_tag('h3'); h.string = qt; new.append(h)
            p = soup.new_tag('p'); p.string = d.get_text(' ', strip=True); new.append(p)
            d.replace_with(new)
        for chip in sec.find_all(class_=re.compile('injury-chip')):
            chip.name = 'li'
        for a in sec.find_all('a'):
            a.attrs = {'href': a.get('href', '')}
        for im in sec.find_all('img'): im.decompose()
        m = md(str(sec), heading_style='ATX', strip=['div', 'section', 'span'])
        m = re.sub(r'\n{3,}', '\n\n', m).strip()
        body.append(m)
    text = clean_text('\n\n'.join(body))
    for b in BANNED: text = re.sub(b, '', text, flags=re.I)
    text = re.sub(r'Learn More →', '', text)
    lang = 'hy' if u.startswith('/hy/') else 'en'
    fm = {'url': u, 'lang': lang, 'title': clean_text(title), 'description': clean_text(desc), 'h1': clean_text(h1t)}
    if subt: fm['subtitle'] = clean_text(subt)
    if hero_img: fm['hero_image'] = hero_img
    fm['legacy'] = True
    dest = OUT / (u.strip('/').replace('/', '__') + '.md')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text('---\n' + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + '---\n\n' + text + '\n')
    print(u, len(text))
