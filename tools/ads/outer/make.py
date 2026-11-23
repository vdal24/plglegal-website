import csv
C = 'PLG | Injury Search | Outer LA'
L = 'PLG | Injury Search | LA County'


def w(f, h, rows):
    wr = csv.writer(open(f, 'w', newline=''))
    wr.writerow(h)
    wr.writerows(rows)


w('1-campaign.csv', ['Campaign', 'Campaign type', 'Networks', 'Budget', 'Budget type', 'Bid strategy type', 'Campaign status', 'EU political ads'],
  [[C, 'Search', 'Google search', 25, 'Daily', 'Manual CPC', 'Paused', 'No']])

groups = {
    'Car Accident - Near Me': (30, 'https://plglegal.com/practice-areas/car-accidents/', 'Car-Accident', 'Lawyer',
        ['car accident lawyer near me', 'car accident attorney near me', 'auto accident lawyer near me', 'auto accident attorney', 'car accident lawyer', 'car crash lawyer', 'personal injury lawyer near me', 'rear ended accident lawyer']),
    'Car Accident - Antelope Valley': (25, 'https://plglegal.com/car-accident-lawyer/antelope-valley/', 'Car-Accident', 'Lancaster',
        ['car accident lawyer lancaster', 'car accident attorney lancaster', 'car accident lawyer palmdale', 'car accident attorney palmdale', 'personal injury lawyer lancaster', 'personal injury lawyer palmdale', 'accident lawyer antelope valley', 'truck accident lawyer lancaster']),
    'Car Accident - Santa Clarita': (25, 'https://plglegal.com/car-accident-lawyer/santa-clarita/', 'Car-Accident', 'Santa-Clarita',
        ['car accident lawyer santa clarita', 'car accident attorney santa clarita', 'personal injury lawyer santa clarita', 'car accident lawyer valencia', 'accident attorney santa clarita', 'truck accident lawyer santa clarita']),
    'Car Accident - San Gabriel Valley': (25, 'https://plglegal.com/car-accident-lawyer/san-gabriel-valley/', 'Car-Accident', 'SGV',
        ['car accident lawyer pasadena', 'car accident attorney pasadena', 'car accident lawyer west covina', 'car accident lawyer el monte', 'car accident lawyer pomona', 'car accident attorney pomona', 'personal injury lawyer west covina', 'car accident lawyer arcadia', 'car accident lawyer alhambra', 'car accident lawyer covina']),
    'Car Accident - Long Beach South Bay': (25, 'https://plglegal.com/car-accident-lawyer/long-beach/', 'Car-Accident', 'Long-Beach',
        ['car accident lawyer long beach', 'car accident attorney long beach', 'personal injury lawyer long beach', 'car accident lawyer torrance', 'car accident attorney torrance', 'car accident lawyer carson', 'truck accident lawyer long beach']),
    'Car Accident - Ventura County': (25, 'https://plglegal.com/car-accident-lawyer/ventura-county/', 'Car-Accident', 'Ventura',
        ['car accident lawyer oxnard', 'car accident attorney oxnard', 'car accident lawyer ventura', 'car accident attorney ventura', 'personal injury lawyer oxnard', 'car accident lawyer thousand oaks', 'car accident lawyer simi valley', 'car accident lawyer camarillo']),
    'Spanish': (20, 'https://plglegal.com/es/abogado-accidentes-de-auto/', 'Accidentes', 'Auto',
        ['abogado de accidentes', 'abogado de accidentes de carro', 'abogado de accidentes de auto', 'abogados de accidentes cerca de mi', 'abogado de accidentes oxnard', 'abogado de accidentes lancaster', 'abogado de accidentes palmdale', 'abogado de accidentes pomona', 'abogado de accidentes long beach', 'abogado de accidentes ventura']),
}
area = {
    'Car Accident - Near Me': ('Car Accident Lawyer Near You', 'Serving Southern California', 'car, truck, or rideshare crash'),
    'Car Accident - Antelope Valley': ('Antelope Valley Injury Lawyer', 'Lancaster and Palmdale', 'crash in Lancaster or Palmdale'),
    'Car Accident - Santa Clarita': ('Santa Clarita Accident Lawyer', 'Serving Santa Clarita', 'crash in Santa Clarita'),
    'Car Accident - San Gabriel Valley': ('SGV Car Accident Lawyer', 'Serving San Gabriel Valley', 'crash in the San Gabriel Valley'),
    'Car Accident - Long Beach South Bay': ('Long Beach Accident Lawyer', 'Long Beach and South Bay', 'crash in Long Beach or South Bay'),
    'Car Accident - Ventura County': ('Ventura County Injury Lawyer', 'Oxnard and Ventura', 'crash in Ventura County'),
}
ag = [[C, g, v[0], 'Enabled'] for g, v in groups.items()]
kw = []
ads = []
for g, (b, u, p1, p2, ks) in groups.items():
    for k in ks:
        kw += [[C, g, k, 'Phrase'], [C, g, k, 'Exact']]
    if g == 'Spanish':
        H = ['Abogado de Accidentes de Auto', 'Consulta Gratis', 'No Cobramos Si No Ganamos', 'Ex Abogado de Aseguradora', 'Llame o Envíe un Texto Hoy', 'Accidentes de Uber y Lyft', 'Accidentes de Camión', 'Hable con un Abogado Hoy', '¿Lesionado en un Accidente?', 'Prospect Law Group', 'Hablamos Español', 'Oxnard, Lancaster, Pomona', '¿Oferta Baja del Seguro?', 'Atención Directa del Abogado', 'Le Atendemos por Teléfono']
        D = ['Antes defendía a las aseguradoras. Ahora peleo contra ellas por usted. Consulta gratis.', 'No cobramos a menos que obtengamos una compensación. Llame o envíe un texto hoy.', 'Accidentes de auto, camión, motocicleta, Uber y Lyft en el sur de California.', 'Hable directamente con su abogado. Le atendemos por teléfono, texto o video.']
    else:
        a1, a2, a3 = area[g]
        H = [a1, 'Car Accident Attorney', 'Auto Accident Lawyer', 'Former Insurance Co. Attorney', 'Now I Work for You', 'Free Consultation', 'No Fee Unless We Win', 'Call or Text Us Today', a2, 'Talk to an Attorney Today', 'Hurt in a Crash? Call Us', 'Prospect Law Group', 'Insurance Lowball Offer?', 'Truck Accident Lawyer', 'Se Habla Español']
        D = ['I used to defend insurance companies. Now I use that experience to fight for you.', 'Free consultation. No fee unless we recover. Call or text us today.', f'Hurt in a {a3}? Get a free case review today.', 'Talk directly with your attorney. We handle cases by phone, text, and video.']
    for h in H:
        assert len(h) <= 30, (h, len(h))
    for d in D:
        assert len(d) <= 90, (d, len(d))
    ads.append([C, g, 'Responsive search ad', u, p1, p2] + H + D)
hdr = ['Campaign', 'Ad group', 'Ad type', 'Final URL', 'Path 1', 'Path 2'] + [f'Headline {i}' for i in range(1, 16)] + [f'Description {i}' for i in range(1, 5)]
w('2-adgroups.csv', ['Campaign', 'Ad group', 'Max CPC', 'Ad group status'], ag)
w('3-keywords.csv', ['Campaign', 'Ad group', 'Keyword', 'Criterion Type'], kw)
w('4-ads.csv', hdr, ads)

lines = open('../v2/negatives.txt').read().split('\n')
camps = ['PLG | Injury Search | LA County', 'PLG | Injury Search | Inland Empire', 'PLG | Lemon Law | California', 'PLG | Brand']
sec = None
neg = []
for l in lines:
    s = l.strip()
    if s in camps:
        sec = s
        continue
    if sec == L and s:
        neg.append(s)
old = [x['Keyword'] for x in csv.DictReader(open('../5-negatives.csv')) if 'LA County' in x['Campaign']]
rows = []
seen = set()


def add(k, t):
    if k.lower() in seen:
        return
    seen.add(k.lower())
    rows.append([C, k, t])


for s in neg:
    if s.startswith('"'):
        add(s.strip('"'), 'Campaign Negative Phrase')
    elif s.startswith('['):
        add(s.strip('[]'), 'Campaign Negative Exact')
    else:
        add(s, 'Campaign Negative Broad')
for k in old:
    add(k, 'Campaign Negative Phrase')
for k in ['block law', 'c&b law', 'c and b law', 'thon beck', 'vanni callahan', 'amigo lawyer', 'megerdichyan', 'megeredchian', 'bakersfield', 'glendale']:
    add(k, 'Campaign Negative Phrase')
w('5-negatives.csv', ['Campaign', 'Keyword', 'Criterion Type'], rows)

la = [[L, 'Car Accident - LA County', 28, 'Paused'], [L, 'Car Accident - Burbank', 25, 'Paused'], [L, 'Car Accident - Pasadena', 25, 'Paused'], [L, 'Spanish', 20, 'Paused'],
      [L, 'Truck', 60, 'Enabled'], [L, 'Commercial Vehicle', 55, 'Enabled'], [L, 'Serious Injury', 55, 'Enabled'], [L, 'Wrongful Death', 55, 'Enabled'], [L, 'Rideshare', 50, 'Enabled']]
w('6-la-changes.csv', ['Campaign', 'Ad group', 'Max CPC', 'Ad group status'], la)
w('7-budgets.csv', ['Campaign', 'Budget', 'Budget type'], [[L, 20, 'Daily']])
print(len(ag), len(kw), len(ads), len(rows))
