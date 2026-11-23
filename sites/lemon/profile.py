# Lemon law website settings. Loaded by build.py when run as: python3 build.py --site lemon
# Same firm, same phone and email; lemon law only.

REMOVED = {'/es/lemon-law/': '/es/', '/practice-areas/lemon-law/': '/california-lemon-law/'}

for _l in STRINGS:
    STRINGS[_l] = dict(STRINGS[_l])

STRINGS['en'].update(
    cases=['Car keeps going back to the dealer', 'Leased vehicle with repeat problems', 'Engine or transmission', 'Electrical or infotainment', 'EV battery or charging', 'Used car under warranty', 'Other lemon law question'],
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
        ('Lemon Law', '/california-lemon-law/', [
            ('California Lemon Law', '/california-lemon-law/'), ('How Buybacks Are Calculated', '/lemon-law/buyback-calculation/'),
            ('Used Cars', '/lemon-law/used-cars/'), ('Lemon Law FAQ', '/lemon-law/faq/')]),
        ('Brands', '/lemon-law/#brands', [
            ('Tesla', '/lemon-law/tesla/'), ('Ford', '/lemon-law/ford/'), ('Chevrolet and GM', '/lemon-law/chevrolet-gm/'),
            ('Jeep and Stellantis', '/lemon-law/jeep-stellantis/'), ('Land Rover', '/lemon-law/land-rover/'), ('Mercedes-Benz', '/lemon-law/mercedes-benz/'),
            ('Toyota and Lexus', '/lemon-law/toyota/'), ('Hyundai', '/lemon-law/hyundai/'), ('Kia', '/lemon-law/kia/'), ('Honda', '/lemon-law/honda/'), ('Nissan', '/lemon-law/nissan/'),
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

def _lead_mix(items):
    # Display order: one result per manufacturer first (largest of each, no single brand leading the list), then the rest by amount.
    val = lambda r: float(r['amount'].strip('$').replace(',', '')) if r['amount'] else 0
    best = {}
    for r in sorted(items, key=val, reverse=True):
        best.setdefault(r['make'], r)
    lead = sorted(best.values(), key=val, reverse=True)
    if len(lead) > 1 and lead[0]['make'] == 'Mercedes-Benz':
        lead[0], lead[1] = lead[1], lead[0]
    rest = [r for r in sorted(items, key=val, reverse=True) if r not in lead]
    return lead + rest
_RES = _lead_mix(_RES)

KNOWS_ABOUT = ['California lemon law', 'Song-Beverly Consumer Warranty Act', 'Vehicle repurchase and replacement claims',
               'Electric vehicle and hybrid battery defects', 'Vehicle warranty disputes']

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

def _field(name, label, hint='', money=True, ph=''):
    attrs = 'inputmode="decimal" data-money' if money else 'inputmode="numeric"'
    pre = '<span class="bb-pre">$</span>' if money else ''
    hint = f'<small>{hint}</small>' if hint else ''
    return (f'<label class="bb-f"><span class="bb-l">{label}</span>'
            f'<span class="bb-in">{pre}<input name="{name}" type="text" autocomplete="off" {attrs} placeholder="{ph}"></span>{hint}</label>')

_CALC = (
    '<form id="bb-calc" class="bb-calc" novalidate>'
    '<div class="bb-inputs">'
    '<fieldset><legend>What you paid</legend>'
    + _field('price', 'Vehicle price', 'The cash price on your contract, before tax.', ph='48,000')
    + _field('fees', 'Sales tax, registration and fees', ph='5,200')
    + _field('finance', 'Finance charges paid so far', 'Optional. Interest you have already paid.', ph='0')
    + _field('incidentals', 'Towing, rentals and other costs', 'Optional. Costs caused by the defect.', ph='0')
    + '</fieldset><fieldset><legend>Mileage</legend>'
    + _field('miles_start', 'Miles when you got the car', money=False, ph='12')
    + _field('miles_repair', 'Miles at the first repair visit for the problem', 'Look at your first repair order for this defect.', money=False, ph='6,000')
    + '</fieldset><fieldset><legend>Your loan</legend>'
    + _field('owed', 'Loan balance today', 'Optional. Shows how much goes to your lender and how much to you.', ph='0')
    + '</fieldset></div>'
    '<div class="bb-result" aria-live="polite">'
    '<span class="bb-kicker">Estimated buyback</span>'
    '<strong class="bb-total" data-out="total">$0</strong>'
    '<dl><div><dt>Total you paid</dt><dd data-out="paid">$0</dd></div>'
    '<div><dt>Mileage offset</dt><dd data-out="offset">$0</dd></div>'
    '<div class="bb-loan"><dt>Paid to your lender</dt><dd data-out="lender">$0</dd></div>'
    '<div class="bb-loan"><dt>Refunded to you</dt><dd data-out="you">$0</dd></div></dl>'
    '<p class="bb-fees">Attorney fees are paid by the manufacturer on top of this, not taken out of it.</p>'
    '<a class="btn btn-gold bb-cta" href="#case-review">Get my free buyback review</a>'
    '<small class="bb-disc">Estimate only, not legal advice. The offset uses the standard California formula: miles before the first repair visit, divided by 120,000, times the vehicle price. Your actual buyback depends on your contract, repair history, and the facts of your case. Leases are calculated differently. Results vary.</small>'
    '</div></form>'
    '<script src="/js/calc.js?v=2" defer></script>'
)

def PAGE_HOOK(html, url):
    html = re.sub(r'<p>\s*%%CALC%%\s*</p>', lambda m: _CALC, html)
    html = html.replace('%%TOTAL%%', _total())
    html = re.sub(r'<p>\s*%%HERO_RESULTS%%\s*</p>', lambda m: _hero_results(), html)
    html = re.sub(r'<p>\s*%%RESULTS%%\s*</p>', lambda m: _cards(_RES), html)
    html = re.sub(r'<p>\s*%%RESULTS3%%\s*</p>', lambda m: _cards(_RES[:3]), html)
    return html

NOTFOUND_LINKS = '<p><a href="/">Home</a> · <a href="/california-lemon-law/">California Lemon Law</a> · <a href="/lemon-law/#brands">Lemon Law by Brand</a> · <a href="/results/">Results</a> · <a href="/contact/">Contact</a></p>'
DEFAULT_HERO = '/images/practice-areas/lemon-law.jpg'
