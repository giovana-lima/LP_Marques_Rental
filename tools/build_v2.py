"""Gera a nova landing page (PT e EN) do Jardins do Marquês.
Uso: python3 tools/build_v2.py   (reescreve public/rent-porto-pt.html e public/rent-porto-en.html)
"""
import re, html, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(ROOT, '..', 'public')
OLD = PUB + '/'   # head (Cookiebot, GTM, SEO) e rodapé são lidos das páginas atuais


def between(s, a, b, incl_b=True):
    i = s.index(a)
    j = s.index(b, i) + (len(b) if incl_b else 0)
    return s[i:j]


def old_parts(lang):
    s = open(OLD + ('rent-porto-pt.html' if lang == 'pt' else 'rent-porto-en.html')).read()
    head_top = between(s, '    <!-- Cookiebot', '    <link rel="apple-touch-icon"', incl_b=False)
    head_top += between(s, '    <link rel="apple-touch-icon"', '\n')
    seo = between(s, '    <link rel="canonical"', '</script>\n')
    gtm_ns = between(s, '    <!-- Google Tag Manager (noscript) -->', '<!-- End Google Tag Manager (noscript) -->\n')
    footer = between(s, '    <footer class="sitefoot">', '</footer>\n')
    footer = re.sub(r'\n\s*<nav class="sf-(nav|social)".*?</nav>', '', footer, flags=re.S)
    title = ' '.join(re.search(r'<title>(.*?)</title>', s, re.S).group(1).split())
    desc = ' '.join(re.search(r'name="description"\s+content="(.*?)"', s, re.S).group(1).split())
    return head_top, seo, gtm_ns, footer, title, desc


IMG = 'assets/img/v2/'

T = {
 'pt': dict(
  lang='pt-PT', other_url='https://rent-marques.youropapt.com/', other_label='EN', other_hreflang='en', other_name='English',
  thanks='obrigado-pt.html', origin='LP Marques Rental PT', gal_label='Galeria', sending='A enviar…',
  nav=[('concept', 'O conceito'), ('location', 'Localização'), ('apartments', 'Apartamentos'), ('gallery', 'Galeria')],
  cta='Saiba mais', menu='Menu', close='Fechar',
  hero_eyebrow='Jardins do Marquês · Rua do Bonjardim, Porto',
  hero_h1='O Porto começa à sua porta.',
  hero_sub='Apartamentos novos para arrendar, do T0 ao T2 Duplex, junto ao metro do Marquês. Todos com varanda e lugar de garagem. Desde €900/mês.',
  hero_btn2='Ver apartamentos',
  hero_alt='Fachada do Jardins do Marquês, Porto',
  concept_k='01 — O conceito', concept_h='Apartamentos preparados para uma nova etapa.',
  concept_p=['O Jardins do Marquês fica no centro do Porto, numa zona onde a vida residencial se cruza com o comércio, os transportes e os serviços do dia a dia.',
             'Viver aqui significa acompanhar o ritmo da cidade sem abdicar de um espaço reservado para descansar. Do estúdio ao duplex, há um apartamento para cada fase da vida.'],
  concept_quote='Edifício novo, arrendamento de longa duração.',
  concept_alt='Sala de estar de um apartamento no Jardins do Marquês',
  stats=[('170', 'm', 'do metro do Marquês'), ('900', '€/mês', 'renda desde'), ('100', '%', 'com varanda e lugar de garagem')],
  loc_k='02 — Localização', loc_h='No centro de tudo, numa zona tranquila.',
  loc_p='A Rua do Bonjardim liga o Marquês à Baixa. O metro, os autocarros, o comércio e os serviços estão a poucos minutos a pé.',
  loc_list=[('Metro do Marquês', '170 m'), ('Paragens de autocarro', '180 m'), ('Supermercado', '220 m'), ('Escola', '300 m'),
            ('Praça da República', '800 m'), ('Metro da Trindade', '1 km'), ('Rua de Santa Catarina e Baixa', 'poucos minutos'), ('Polo universitário', 'acesso direto de metro')],
  loc_alt='Vista aérea da Praça do Marquês e do Jardins do Marquês', map_title='Mapa', maps='Abrir no Google Maps',
  slides=[('varanda-render', 'Varandas privativas em todos os apartamentos'), ('cozinha', 'Cozinhas equipadas com bancada em granito'),
          ('garagem', 'Lugar de garagem incluído'), ('cobertura', 'Painéis fotovoltaicos na cobertura')],
  prev='Anterior', next='Seguinte',
  bld_k='03 — O edifício', bld_h='Uma arquitetura feita para durar.',
  bld_p='Galerias abertas, muita luz natural e materiais escolhidos para o dia a dia. Um edifício novo, eficiente e pensado para quem quer viver no centro com conforto.',
  amen=['Varanda privativa em todas as frações', 'Lugar de garagem incluído', 'Painéis fotovoltaicos e bomba de calor', 'Ar condicionado',
        'Isolamento térmico e acústico', 'Janelas de alumínio com corte térmico e vidro duplo', 'Elevador'],
  bld_alt='Fachada do Jardins do Marquês com galerias e varandas',
  apt_k='04 — Apartamentos', apt_h='Escolha o seu apartamento.',
  apt_note='',
  from_='Desde', month='/mês', plans='Plantas',
  rows_common=[('Estacionamento', '1 lugar incluído'), ('Cozinha', 'Forno, placa, exaustor, combinado, máquina de lavar loiça e roupa embutidos'),
               ('Materiais', 'Pavimento flutuante em carvalho, armários lacados, bancadas em granito cinzento'),
               ('Conforto', 'Painéis fotovoltaicos, bomba de calor, ar condicionado, isolamento térmico e acústico')],
  apts=[
   dict(code='T0', tab='T0 · Estúdio', title='Estúdio junto ao metro do Marquês', price='900', img='t0', alt='Estúdio T0 no Jardins do Marquês',
        rows=[('Área bruta', '38,7 m²'), ('Varanda', '6,28 m²'), ('Distribuição', 'Estúdio em espaço aberto · piso 1')],
        plans=[('planta-t0', 'Planta do estúdio')]),
   dict(code='T1', tab='T1 · Duplex', title='Duplex T1 com suíte e escritório', price='1.300', img='t1', alt='Duplex T1 no Jardins do Marquês',
        rows=[('Área bruta', '64,9 m²'), ('Varandas', '23,08 m²'), ('Distribuição', 'Duplex · pisos 3–4. Entrada: sala, cozinha aberta e casa de banho. Piso superior: suíte com roupeiro e quarto extra (escritório, closet ou hóspedes)')],
        plans=[('planta-t1-piso1', 'Piso 1'), ('planta-t1-piso2', 'Piso 2')]),
   dict(code='T2', tab='T2 · Duplex', title='Duplex T2 para famílias', price='1.500', img='t2', alt='Duplex T2 no Jardins do Marquês',
        rows=[('Área bruta', 'A: 78,81 m² · B: 83,65 m²'), ('Varandas', 'A: 40,88 m² · B: 16,69 m²'), ('Distribuição', 'Duplex · pisos 3–4 · duas opções (A e B)')],
        plans=[('planta-t1-piso1', 'Opção A · Piso 1'), ('planta-t2a-piso2', 'Opção A · Piso 2'), ('planta-t2b-piso1', 'Opção B · Piso 1'), ('planta-t2b-piso2', 'Opção B · Piso 2')]),
  ],
  gal_k='05 — Galeria', gal_h='Por dentro e por fora.', gal_note='',
  gallery=[('fachada-render', 'Fachada'), ('sala', 'Sala de estar'), ('quarto', 'Quarto'), ('varanda-estudio', 'Varanda e estúdio'),
           ('cozinha', 'Cozinha'), ('casa-de-banho', 'Casa de banho'), ('duche', 'Duche'), ('sala-render', 'Sala'),
           ('varanda-render', 'Galeria exterior'), ('rua-interior', 'Rua interior'), ('fachada', 'Fachada'), ('rua-acesso', 'Acesso ao edifício'),
           ('aerea-igreja', 'Vista aérea'), ('aerea-bairro', 'A zona')],
  contact_k='06 — Contacto', contact_h='Fale connosco.', contact_p='Diga-nos o que procura. Respondemos o mais rapidamente possível.',
  steps=['Envie o seu pedido', 'A nossa equipa contacta-o', 'Visite o apartamento'],
  office='Escritório', phone_l='Telefone',
  f_name='Nome completo', f_phone='Telefone', f_email='Email', f_type='Que tipologia de apartamento procura?', sel='Selecionar',
  types=[('T0', 'T0 – Estúdio'), ('T1', 'T1 – Duplex'), ('T2', 'T2 – Duplex')],
  f_budget='O valor inicial da renda da tipologia que prefere está dentro do seu orçamento?', budget=[('Sim', 'Sim'), ('Não', 'Não')],
  f_move='Está disponível para se mudar…', move=[('Imediatamente', 'Imediatamente'), ('Nos próximos 3 meses', 'Nos próximos 3 meses'), ('Daqui a 3 meses ou mais', 'Daqui a 3 meses ou mais')],
  consent='Aceito ser contactado(a) pela Youropa sobre este pedido.', submit='Enviar pedido',
  ui='{ searchPlaceholder: "Procurar país", searchEmptyState: "Nenhum resultado encontrado", countryListAriaLabel: "Lista de países", noCountrySelected: "Selecionar país", clearSearchAriaLabel: "Limpar pesquisa", closeCountrySelectorAriaLabel: "Fechar" }',
  phone_msg='Introduza um número de telefone válido para o país selecionado.',
  email_msg='Introduza um email válido, por exemplo nome@exemplo.com.',
  err='Ocorreu um erro. Tente novamente ou contacte-nos.',
 ),
 'en': dict(
  lang='en', other_url='https://arrendar-marques.youropapt.com/', other_label='PT', other_hreflang='pt', other_name='Português',
  thanks='thank-you-en.html', origin='LP Marques Rental EN', gal_label='Gallery', sending='Sending…',
  nav=[('concept', 'The concept'), ('location', 'Location'), ('apartments', 'Apartments'), ('gallery', 'Gallery')],
  cta='Learn more', menu='Menu', close='Close',
  hero_eyebrow='Jardins do Marquês · Rua do Bonjardim, Porto',
  hero_h1='Porto starts at your door.',
  hero_sub='New apartments for rent, from T0 to T2 Duplex, near Marquês metro. All with a balcony and a parking space. From €900/month.',
  hero_btn2='See apartments',
  hero_alt='Facade of Jardins do Marquês, Porto',
  concept_k='01 — The concept', concept_h='Apartments ready for a new chapter.',
  concept_p=['Jardins do Marquês is in a central area of Porto, where neighbourhood life meets shops, transport and everyday services.',
             'Living here means keeping up with the city while having a calm place to rest. From studio to duplex, there is an apartment for every stage of life.'],
  concept_quote='Brand-new building, long-term rental.',
  concept_alt='Living room of an apartment at Jardins do Marquês',
  stats=[('170', 'm', 'from Marquês metro'), ('900', '€/month', 'rent from'), ('100', '%', 'with balcony and parking space')],
  loc_k='02 — Location', loc_h='Close to everything, in a quiet neighbourhood.',
  loc_p='Rua do Bonjardim links Marquês to the city centre. Metro, buses, shops and services are a few minutes away on foot.',
  loc_list=[('Marquês metro', '170 m'), ('Bus stops', '180 m'), ('Supermarket', '220 m'), ('School', '300 m'),
            ('Praça da República', '800 m'), ('Trindade metro', '1 km'), ('Rua de Santa Catarina and Baixa', 'a few minutes'), ('University area', 'direct by metro')],
  loc_alt='Aerial view of Praça do Marquês and Jardins do Marquês', map_title='Map', maps='Open in Google Maps',
  slides=[('varanda-render', 'Private balconies in every apartment'), ('cozinha', 'Fitted kitchens with granite worktops'),
          ('garagem', 'Parking space included'), ('cobertura', 'Solar panels on the roof')],
  prev='Previous', next='Next',
  bld_k='03 — The building', bld_h='Architecture built to last.',
  bld_p='Open galleries, lots of natural light and materials chosen for everyday life. A new, efficient building for people who want to live in the centre in comfort.',
  amen=['Private balcony in every apartment', 'Parking space included', 'Solar panels and heat pump', 'Air conditioning',
        'Thermal and acoustic insulation', 'Double-glazed aluminium windows with thermal break', 'Lift'],
  bld_alt='Facade of Jardins do Marquês with galleries and balconies',
  apt_k='04 — Apartments', apt_h='Pick your apartment.',
  apt_note='',
  from_='From', month='/month', plans='Floor plans',
  rows_common=[('Parking', '1 space included'), ('Kitchen', 'Built-in oven, hob, extractor, fridge-freezer, dishwasher, washer'),
               ('Materials', 'Oak floating floors, lacquered cabinetry, grey granite worktops'),
               ('Comfort', 'Solar panels, heat pump, air conditioning, thermal and acoustic insulation')],
  apts=[
   dict(code='T0', tab='T0 · Studio', title='Studio near Marquês metro', price='900', img='t0', alt='T0 studio at Jardins do Marquês',
        rows=[('Gross area', '38.7 m²'), ('Balcony', '6.28 m²'), ('Layout', 'Open-plan studio · floor 1')],
        plans=[('planta-t0', 'Studio plan')]),
   dict(code='T1', tab='T1 · Duplex', title='T1 duplex with suite and office', price='1,300', img='t1', alt='T1 duplex at Jardins do Marquês',
        rows=[('Gross area', '64.9 m²'), ('Balconies', '23.08 m²'), ('Layout', 'Duplex · floors 3–4. Entrance: living room, open kitchen and bathroom. Upper floor: suite with wardrobe and extra room (office, dressing room or guest)')],
        plans=[('planta-t1-piso1', 'Level 1'), ('planta-t1-piso2', 'Level 2')]),
   dict(code='T2', tab='T2 · Duplex', title='T2 duplex for families', price='1,500', img='t2', alt='T2 duplex at Jardins do Marquês',
        rows=[('Gross area', 'A: 78.81 m² · B: 83.65 m²'), ('Balconies', 'A: 40.88 m² · B: 16.69 m²'), ('Layout', 'Duplex · floors 3–4 · two layouts (A and B)')],
        plans=[('planta-t1-piso1', 'Layout A · Level 1'), ('planta-t2a-piso2', 'Layout A · Level 2'), ('planta-t2b-piso1', 'Layout B · Level 1'), ('planta-t2b-piso2', 'Layout B · Level 2')]),
  ],
  gal_k='05 — Gallery', gal_h='Inside and out.', gal_note='',
  gallery=[('fachada-render', 'Facade'), ('sala', 'Living room'), ('quarto', 'Bedroom'), ('varanda-estudio', 'Balcony and studio'),
           ('cozinha', 'Kitchen'), ('casa-de-banho', 'Bathroom'), ('duche', 'Shower'), ('sala-render', 'Living room'),
           ('varanda-render', 'Outdoor gallery'), ('rua-interior', 'Inner street'), ('fachada', 'Facade'), ('rua-acesso', 'Building access'),
           ('aerea-igreja', 'Aerial view'), ('aerea-bairro', 'The neighbourhood')],
  contact_k='06 — Contact', contact_h='Talk to us.', contact_p="Tell us what you're looking for. We'll reply as soon as possible.",
  steps=['Send us your request', 'Our team contacts you', 'Visit the apartment'],
  office='Office', phone_l='Phone',
  f_name='Full name', f_phone='Phone', f_email='Email', f_type='Which apartment type are you interested in?', sel='Select',
  types=[('T0', 'T0 – Studio'), ('T1', 'T1 – Duplex'), ('T2', 'T2 – Duplex')],
  f_budget='Is the starting rent for your preferred apartment type within your budget?', budget=[('Yes', 'Yes'), ('No', 'No')],
  f_move='Are you ready to move in…', move=[('Immediately', 'Immediately'), ('Within the next 3 months', 'Within the next 3 months'), ('In 3 months or more', 'In 3 months or more')],
  consent='I agree to be contacted by Youropa about this request.', submit='Send request',
  ui='{}',
  phone_msg='Please enter a valid phone number for the selected country.',
  email_msg='Please enter a valid email, for example name@example.com.',
  err='Sorry, something went wrong. Please try again or contact us.',
 ),
}

CSS = open(os.path.join(ROOT, 'v2.css')).read()
JS = open(os.path.join(ROOT, 'v2.js')).read()

ICON_CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
ICON_L = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
ICON_R = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'


def e(x):
    return html.escape(x, quote=True)


def build(lang):
    t = T[lang]
    head_top, seo, gtm_ns, footer, title, desc = old_parts(lang)
    nav = ''.join(f'<a href="#{i}">{e(l)}</a>' for i, l in t['nav'])
    loc = ''.join(f'<li><span class="n">{k+1:02d}</span><span class="p">{e(a)}</span><span class="d">{e(b)}</span></li>' for k, (a, b) in enumerate(t['loc_list']))
    # No telemóvel, a 1.ª foto do carrossel é a imagem da varanda (mostra melhor a varanda num ecrã vertical)
    MOBILE_SLIDE = {}
    def slide_img(k, f, c):
        img = f'<img src="{IMG}{f}.webp" alt="{e(c)}" loading="lazy" width="1920" height="1280">'
        if k in MOBILE_SLIDE:
            return f'<picture class="m-alt"><source media="(max-width: 800px)" srcset="{IMG}{MOBILE_SLIDE[k]}.webp">{img}</picture>'
        return img
    slides = ''.join(f'<figure class="slide">{slide_img(k, f, c)}<figcaption><span>{k+1}/{len(t["slides"])}</span>{e(c)}</figcaption></figure>' for k, (f, c) in enumerate(t['slides']))
    amen = ''.join(f'<li>{ICON_CHECK}<span>{e(a)}</span></li>' for a in t['amen'])
    tabs = ''.join(f'<button type="button" class="tab" role="tab" id="tab-{a["code"]}" aria-controls="pn-{a["code"]}" aria-selected="{"true" if k == 0 else "false"}" tabindex="{0 if k == 0 else -1}" data-t="{a["code"]}">{e(a["tab"])}</button>' for k, a in enumerate(t['apts']))
    panels = ''
    for k, a in enumerate(t['apts']):
        rows = ''.join(f'<div><dt>{e(x)}</dt><dd>{e(y)}</dd></div>' for x, y in a['rows'] + t['rows_common'])
        plans = ''.join(f'<button type="button" class="plan" data-full="assets/img/{p}.webp" data-cap="{e(a["code"] + " · " + c)}"><img src="assets/img/{p}.webp" alt="{e(a["code"] + " · " + c)}" loading="lazy"><span>{e(c)}</span></button>' for p, c in a['plans'])
        panels += f'''
          <div class="panel{' on' if k == 0 else ''}" id="pn-{a['code']}" role="tabpanel" aria-labelledby="tab-{a['code']}">
            <div class="pmedia">
              <img class="pphoto" src="assets/img/{a['img']}.webp" alt="{e(a['alt'])}" loading="lazy" width="1200" height="675">
              <p class="plabel">{e(t['plans'])}</p>
              <div class="plans">{plans}</div>
            </div>
            <div class="pinfo">
              <span class="ptype">{e(a['tab'])}</span>
              <h3>{e(a['title'])}</h3>
              <p class="price"><small>{e(t['from_'])}</small> €{a['price']}<small>{e(t['month'])}</small></p>
              <dl class="info">{rows}</dl>
              <a class="btn" href="#contact" data-pick="{a['code']}">{e(t['cta'])}</a>
            </div>
          </div>'''
    stats = ''.join(f'<li class="stat"><p class="num"><span class="count" data-to="{n}">{n}</span>{f"<small>{e(u)}</small>" if u else ""}</p><p class="lbl">{e(l)}</p></li>' for n, u, l in t['stats'])
    gal = ''.join(f'<button type="button" class="gi" data-full="{IMG}{f}.webp" data-cap="{e(c)}"><img src="{IMG}{f}-sm.webp" alt="{e(c)}" loading="lazy"></button>' for f, c in t['gallery'])
    steps = ''.join(f'<li><b>{k+1}</b>{e(s)}</li>' for k, s in enumerate(t['steps']))
    opt = lambda pairs: ''.join(f'<option value="{e(v)}">{e(l)}</option>' for v, l in pairs)
    js = (JS.replace('__THANKS__', t['thanks']).replace('__UI__', t['ui']).replace('__PHONE_MSG__', t['phone_msg'])
            .replace('__EMAIL_MSG__', t['email_msg']).replace('__ERR__', t['err']).replace('__LANG__', 'pt' if lang == 'pt' else 'en').replace('__SENDING__', t['sending']))

    return f'''<!doctype html>
<html lang="{t['lang']}">
  <head>
{head_top}    <title>{e(title)}</title>
    <meta name="description" content="{e(desc)}" />
    <link rel="preload" href="assets/fonts/gambarino.woff2" as="font" type="font/woff2" crossorigin />
    <link rel="preload" href="assets/fonts/bespoke.woff2" as="font" type="font/woff2" crossorigin />
    <link rel="preload" as="image" href="{IMG}fachada-render.webp" media="(min-width: 801px)" />
    <link rel="preload" as="image" href="{IMG}fachada-render-sm.webp" media="(max-width: 800px)" />
    <link rel="stylesheet" href="assets/vendor/intl-tel-input/css/intlTelInput.min.css" />
{seo}    <meta name="theme-color" content="#16152b" />
    <script>
      document.documentElement.classList.add("js");
      setTimeout(function () {{ if (!window.__lpReady) document.documentElement.classList.remove("js"); }}, 3000);
    </script>
    <style>
{CSS}
    </style>
  </head>
  <body>
{gtm_ns}
    <header class="top" id="top">
      <div class="topin">
        <a class="logo" href="#hero" aria-label="Jardins do Marquês"><img src="assets/img/logo.png" alt="Youropa" width="133" height="22"></a>
        <nav class="mainnav" id="mainnav" aria-label="{e(t['menu'])}">{nav}<a class="navcta" href="#contact">{e(t['cta'])}</a></nav>
        <div class="topright">
          <a class="lang" href="{t['other_url']}" hreflang="{t['other_hreflang']}" title="{e(t['other_name'])}">{t['other_label']}</a>
          <a class="btn btn-sm" href="#contact">{e(t['cta'])}</a>
          <button type="button" class="burger" aria-controls="mainnav" aria-expanded="false" aria-label="{e(t['menu'])}"><span></span><span></span></button>
        </div>
      </div>
    </header>

    <main>
      <section class="hero" id="hero">
        <picture>
          <source media="(max-width: 800px)" srcset="{IMG}fachada-render-sm.webp">
          <img src="{IMG}fachada-render.webp" alt="{e(t['hero_alt'])}" width="1920" height="1080" fetchpriority="high">
        </picture>
        <div class="herotxt">
          <span class="eyebrow">{e(t['hero_eyebrow'])}</span>
          <h1>{e(t['hero_h1'])}</h1>
          <p>{e(t['hero_sub'])}</p>
          <div class="btns"><a class="btn" href="#contact">{e(t['cta'])}</a><a class="btn btn-line" href="#apartments">{e(t['hero_btn2'])}</a></div>
        </div>
      </section>

      <section class="sec concept" id="concept">
        <div class="wrap grid2">
          <div class="txt reveal">
            <h2>{e(t['concept_h'])}</h2>
            {''.join(f'<p>{e(p)}</p>' for p in t['concept_p'])}
            <p class="quote">{e(t['concept_quote'])}</p>
          </div>
          <figure class="imgtall reveal"><img src="{IMG}sala.webp" alt="{e(t['concept_alt'])}" loading="lazy" width="1920" height="1280"></figure>
        </div>
      </section>

      <section class="stats" aria-label="Jardins do Marquês">
        <ul class="wrap statsin">{stats}</ul>
      </section>

      <section class="sec location" id="location">
        <div class="wrap grid2 loc">
          <figure class="imgwide reveal"><img style="object-position: 72% 50%" src="{IMG}aerea-marques.webp" alt="{e(t['loc_alt'])}" loading="lazy" width="1920" height="1080"></figure>
          <div class="txt reveal">
            <h2>{e(t['loc_h'])}</h2>
            <p>{e(t['loc_p'])}</p>
            <ol class="poi">{loc}</ol>
          </div>
        </div>
        <div class="wrap mapwrap reveal">
          <div class="mapbox">
            <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3003.8314388738604!2d-8.608697623459642!3d41.16002931006617!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0xd246457e680a7ef%3A0xae2e9d402995bf60!2sR.%20do%20Bonjardim%201089%2C%204000-307%20Porto!5e0!3m2!1s{'pt' if lang == 'pt' else 'en'}!2spt!4v1791543085294!5m2!1s{'pt' if lang == 'pt' else 'en'}!2spt" allowfullscreen loading="lazy" referrerpolicy="strict-origin-when-cross-origin" title="{e(t['map_title'])}"></iframe>
          </div>
          <p class="mapcap">Rua do Bonjardim 1089, Porto · <a href="https://www.google.com/maps/search/?api=1&amp;query=Rua+do+Bonjardim+1089+Porto" target="_blank" rel="noopener">{e(t['maps'])}</a></p>
        </div>
      </section>

      <section class="slider" aria-roledescription="carousel">
        <div class="track" id="track">{slides}</div>
        <div class="sliderctl">
          <button type="button" class="arrow" data-dir="-1" aria-label="{e(t['prev'])}">{ICON_L}</button>
          <button type="button" class="arrow" data-dir="1" aria-label="{e(t['next'])}">{ICON_R}</button>
        </div>
      </section>

      <section class="sec building" id="features">
        <div class="wrap grid2">
          <div class="txt reveal">
            <h2>{e(t['bld_h'])}</h2>
            <p>{e(t['bld_p'])}</p>
            <ul class="amen">{amen}</ul>
          </div>
          <figure class="imgtall reveal"><img src="{IMG}fachada.webp" alt="{e(t['bld_alt'])}" loading="lazy" width="1920" height="1280"></figure>
        </div>
      </section>

      <section class="sec apartments" id="apartments">
        <div class="wrap">
          <div class="head reveal">
            <h2>{e(t['apt_h'])}</h2>
            {f'<p class="note">{e(t["apt_note"])}</p>' if t['apt_note'] else ''}
          </div>
          <div id="prices">
            <div class="tabs" role="tablist">{tabs}</div>
            {panels}
          </div>
        </div>
      </section>

      <section class="sec gallery" id="gallery">
        <div class="wrap">
          <div class="head reveal">
            <h2>{e(t['gal_h'])}</h2>
          </div>
          <div class="grid">{gal}</div>
{f'          <p class="note small">{e(t["gal_note"])}</p>' + chr(10) if t['gal_note'] else ''}        </div>
      </section>

      <section class="sec contact" id="contact">
        <div class="wrap grid2 ct" id="form">
          <div class="txt">
            <h2>{e(t['contact_h'])}</h2>
            <p>{e(t['contact_p'])}</p>
            <ol class="steps">{steps}</ol>
            <address>
              <span>{e(t['office'])}</span>Av. da Boavista 2438, 4100-409 Porto<br>
              <span>{e(t['phone_l'])}</span><a href="tel:+351915928833">+351 915 928 833</a>
            </address>
          </div>
          <!-- Formulário recebido pelo Netlify Forms. O email para a Inmovilla é enviado pela
               função netlify/functions/submission-created.mjs (ver README.md). -->
          <form id="lead" name="lead" method="POST" action="/{t['thanks']}" data-netlify="true" netlify-honeypot="website">
            <input type="hidden" name="form-name" value="lead" />
            <div><label for="name">{e(t['f_name'])}</label><input id="name" name="name" required autocomplete="name" /></div>
            <div class="row">
              <div><label for="phone">{e(t['f_phone'])}</label><input id="phone" name="phone" type="tel" required autocomplete="tel" /></div>
              <div><label for="email">{e(t['f_email'])}</label><input id="email" name="email" type="email" required autocomplete="email" pattern="[^@\\s]+@[^@\\s]+\\.[A-Za-z]{{2,}}" /></div>
            </div>
            <div><label for="type">{e(t['f_type'])}</label><select id="type" name="typology" required><option value="" selected disabled>{e(t['sel'])}</option>{opt(t['types'])}</select></div>
            <div><label for="budget">{e(t['f_budget'])}</label><select id="budget" name="within_budget" required><option value="" selected disabled>{e(t['sel'])}</option>{opt(t['budget'])}</select></div>
            <div><label for="move">{e(t['f_move'])}</label><select id="move" name="move_in_timing" required><option value="" selected disabled>{e(t['sel'])}</option>{opt(t['move'])}</select></div>
            <div style="position: absolute; left: -9999px" aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off" /></label></div>
            <label class="chk"><input type="checkbox" name="consent" required /> <span>{e(t['consent'])}</span></label>
            <input type="hidden" name="origin" value="{t['origin']}" />
            <input type="hidden" name="location" value="Porto - Marquês" />
            <input type="hidden" name="property_ref" id="ref" value="" />
            <input type="hidden" name="source" value="Google" />
            <input type="hidden" name="campaign" id="campaign" value="" />
            <input type="hidden" name="language" value="{'pt' if lang == 'pt' else 'en'}" />
            <input type="hidden" name="utm_source" id="utm_source" /><input type="hidden" name="utm_medium" id="utm_medium" /><input type="hidden" name="utm_campaign" id="utm_campaign" /><input type="hidden" name="utm_content" id="utm_content" /><input type="hidden" name="utm_term" id="utm_term" />
            <button class="btn" type="submit">{e(t['submit'])}</button>
          </form>
        </div>
      </section>
    </main>

{footer}
    <dialog class="lightbox" id="lightbox" aria-label="{e(t['gal_label'])}">
      <button type="button" class="lbclose" aria-label="{e(t['close'])}">×</button>
      <button type="button" class="lbnav" data-dir="-1" aria-label="{e(t['prev'])}">{ICON_L}</button>
      <figure><img alt=""><figcaption></figcaption></figure>
      <button type="button" class="lbnav" data-dir="1" aria-label="{e(t['next'])}">{ICON_R}</button>
    </dialog>

    <script src="assets/vendor/intl-tel-input/js/intlTelInputWithUtils.min.js"></script>
    <script>
{js}
    </script>
  </body>
</html>
'''


for lang, fn in [('pt', 'rent-porto-pt.html'), ('en', 'rent-porto-en.html')]:
    out = build(lang)
    open(os.path.join(PUB, fn), 'w').write(out)
print('ok')
