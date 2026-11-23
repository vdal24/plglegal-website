# Lemon law website settings. Loaded by build.py when run as: python3 build.py --site lemon
# Same firm, same phone and email; lemon law only.

REMOVED = {}

for _l in STRINGS:
    STRINGS[_l] = dict(STRINGS[_l])

STRINGS['en'].update(
    cases=['Car keeps going back to the dealer', 'Engine or transmission', 'Electrical or infotainment', 'EV battery or charging', 'Used car under warranty', 'Other lemon law question'],
    form_title='Free Lemon Law Case Review', form_sub='Tell us about your vehicle. We respond quickly.',
    msg='Year, make, model, and the problem',
    stars='Manufacturer pays attorney fees', atty_role='Lemon law attorney, Prospect Law Group, PC',
    cta_h='Is Your Car a Lemon?',
    cta_p='Free, confidential case review. California law requires the manufacturer to pay your attorney fees when you win, so you pay nothing out of pocket.',
    trust_langs='We speak Armenian · Español', about=('About the attorney', '/about/'), areas='Lemon Law Statewide',
    ad='This website is attorney advertising by Prospect Law Group, PC. The information on this site is general information, not legal advice. Contacting us does not create an attorney-client relationship.',
    nofee='No fees out of pocket',
)
STRINGS['es'].update(
    cases=['Mi auto sigue regresando al taller', 'Motor o transmisión', 'Problemas eléctricos', 'Batería o carga de auto eléctrico', 'Auto usado con garantía', 'Otra pregunta'],
    form_title='Evaluación Gratis de Lemon Law', stars='El fabricante paga los honorarios', nofee='Sin costo de su bolsillo',
    cta_h='¿Su auto es un lemon?', cta_p='Evaluación gratis y confidencial. La ley de California obliga al fabricante a pagar sus honorarios de abogado si gana.',
)
STRINGS['hy'].update(
    cases=['Մեքենան անընդհատ վերանորոգման է', 'Շարժիչ կամ փոխանցման տուփ', 'Էլեկտրական խնդիրներ', 'Էլեկտրական մարտկոց', 'Այլ հարց'],
    form_title='Անվճար Lemon Law գնահատում', stars='Փաստաբանի վճարը տալիս է արտադրողը',
)

NAV = {
    'en': [
        ('Is My Car a Lemon?', '/california-lemon-law/', [
            ('California Lemon Law', '/california-lemon-law/'), ('How Buybacks Are Calculated', '/lemon-law/buyback-calculation/'),
            ('Used Cars', '/lemon-law/used-cars/'), ('Lemon Law FAQ', '/lemon-law/faq/')]),
        ('Brands', '/lemon-law/#brands', [
            ('Mercedes-Benz', '/lemon-law/mercedes-benz/'), ('Tesla', '/lemon-law/tesla/'), ('Ford', '/lemon-law/ford/'),
            ('Chevrolet and GM', '/lemon-law/chevrolet-gm/'), ('Jeep and Stellantis', '/lemon-law/jeep-stellantis/'),
            ('Hyundai', '/lemon-law/hyundai/'), ('Kia', '/lemon-law/kia/'), ('Honda', '/lemon-law/honda/'), ('Nissan', '/lemon-law/nissan/'), ('Toyota and Lexus', '/lemon-law/toyota/'), ('Land Rover', '/lemon-law/land-rover/'),
            ('All Manufacturers', '/lemon-law/#brands')]),
        ('Defects', '/lemon-law/', [
            ('Engine', '/lemon-law/defects/engine/'), ('Transmission', '/lemon-law/defects/transmission/'),
            ('Electrical and Infotainment', '/lemon-law/defects/electrical-infotainment/'), ('EV Battery', '/lemon-law/defects/ev-battery/')]),
        ('Results', '/results/', []),
        ('About', '/about/', []),
        ('Contact', '/contact/', []),
    ],
    'es': [('Lemon Law', '/es/', []), ('Resultados', '/results/', []), ('Contacto', '/contact/', [])],
    'hy': [('Lemon Law', '/hy/', []), ('Արդյունքներ', '/results/', []), ('Կապ', '/contact/', [])],
}

import json as _json
_RES = _json.loads((CONTENT / 'results.json').read_text())

def _cards(items):
    out = []
    for r in items:
        amt = r['amount'] or 'Buyback'
        out.append(f'<div class="res-card"><span class="res-amt">{amt}</span>'
                   f'<strong>{r["vehicle"]}</strong><span class="res-type">{r["type"]}</span>'
                   f'<small class="res-disc">Results vary. Past results do not guarantee a similar outcome.</small></div>')
    return '<div class="res-grid">' + ''.join(out) + '</div>'

def _total():
    return '$' + format(int(sum(float(r['amount'].strip('$').replace(',', '')) for r in _RES if r['amount'])), ',')

def _short(a):
    v = float(a.strip('$').replace(',', ''))
    return f'${round(v / 1000):,}K'

def _hero_results():
    top = [r for r in _RES if r['amount']][:3]
    return '<div class="hero-results">' + ''.join(f'<div><b>{_short(r["amount"])}</b><span>{r["vehicle"].replace("2025 ", "").replace("2023 ", "").replace(" with EQ Technology", "")} buyback</span><small>Results vary</small></div>' for r in top) + '</div>'

def PAGE_HOOK(html, url):
    html = html.replace('%%TOTAL%%', _total())
    html = re.sub(r'<p>\s*%%HERO_RESULTS%%\s*</p>', lambda m: _hero_results(), html)
    html = re.sub(r'<p>\s*%%RESULTS%%\s*</p>', lambda m: _cards(_RES), html)
    html = re.sub(r'<p>\s*%%RESULTS3%%\s*</p>', lambda m: _cards(_RES[:3]), html)
    return html

NOTFOUND_LINKS = '<p><a href="/">Home</a> · <a href="/california-lemon-law/">California Lemon Law</a> · <a href="/lemon-law/#brands">Lemon Law by Brand</a> · <a href="/results/">Results</a> · <a href="/contact/">Contact</a></p>'
DEFAULT_HERO = '/images/practice-areas/lemon-law.jpg'
