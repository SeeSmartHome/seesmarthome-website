#!/usr/bin/env python3
"""Create legal/privacy draft pages and sitewide links after the static build.
Never publish a residential/visiting address or remove any indexing restrictions.
"""
from pathlib import Path
import re

out = Path(__file__).resolve().parent / 'dist'
home = out / 'index.html'
if not home.is_file():
    raise RuntimeError('Build the site before adding legal pages')

labels = {
    'company': {'nl': 'Bedrijfsgegevens', 'en': 'Company details', 'zh': '公司信息'},
    'privacy': {'nl': 'Privacyverklaring', 'en': 'Privacy notice', 'zh': '隐私声明'},
    'form': {
        'nl': 'Wij gebruiken uw gegevens om uw aanvraag te behandelen. Lees onze ',
        'en': 'We use your details to handle your inquiry. Read our ',
        'zh': '我们使用您的资料处理询价。请阅读',
    },
}

def multi(values, tag='span'):
    return ''.join(f'<{tag} data-legal-lang="{lang}"'+(' hidden' if lang != 'nl' else '')+f'>{values[lang]}</{tag}>' for lang in ('nl','en','zh'))

css = '''<style>.legal-main{padding:60px 0 95px;max-width:880px}.legal-main h1{font-size:clamp(2rem,5vw,3.5rem);margin:.2em 0 .45em}.legal-main h2{font-size:1.27rem;margin:2em 0 .5em}.legal-main p,.legal-main li{line-height:1.8}.legal-main a{text-decoration:underline}.legal-main .legal-alert{border-left:3px solid currentColor;padding:10px 16px;margin:20px 0;background:rgba(127,127,127,.08)}.legal-main [hidden],[data-legal-lang][hidden]{display:none!important}.legal-link{white-space:nowrap} .contact-form [data-legal-lang][hidden],.footer [data-legal-lang][hidden]{display:none!important}</style>'''
js = '''<script src="/assets/legal-language.js" defer></script>'''
(out / 'assets' / 'legal-language.js').write_text('''(function(){function show(lang){document.querySelectorAll('[data-legal-lang]').forEach(function(el){el.hidden=el.getAttribute('data-legal-lang')!==lang;});}function init(){var active=document.querySelector('.lang-btn.active[data-lang]');show(active?active.getAttribute('data-lang'):'nl');document.querySelectorAll('.lang-btn[data-lang]').forEach(function(btn){btn.addEventListener('click',function(){show(btn.getAttribute('data-lang'));});});}if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}})();\n''', encoding='utf-8')

# First add navigation/footer links to existing generated public pages (not /admin).
changed = 0
for page in out.rglob('*.html'):
    rel = page.relative_to(out)
    if rel.parts[0] == 'admin':
        continue
    html = page.read_text(encoding='utf-8')
    if '</head>' not in html or '</footer>' not in html:
        continue
    prefix = '../' * (len(rel.parts)-1)
    links = ' '.join(f'<a class="legal-link" href="{prefix}{name}.html">{multi(labels[name])}</a>' for name in ('company','privacy'))
    if '<div class="footer-nav">' not in html:
        raise RuntimeError('Missing footer navigation: '+str(rel))
    html = html.replace('<div class="footer-nav">','<div class="footer-nav">'+links,1)
    # Remove obsolete preview-only message about missing company and privacy information,
    # but keep the overall preview banner, pending image clearance and noindex.
    html = re.sub(r'<span data-i18n="legal">.*?</span>', '<span>SeeSmartHome B.V. · KVK 42142350 · <a href="'+prefix+'company.html">'+multi(labels['company'])+'</a></span>', html, count=1, flags=re.S)
    html = html.replace('</head>', css+js+'</head>',1)
    if rel == Path('index.html'):
        privacy_note = '<p class="micro legal-form-note">'+''.join(
            f'<span data-legal-lang="{lang}"'+(' hidden' if lang!='nl' else '')+'>'+labels['form'][lang]+'<a href="privacy.html">'+labels['privacy'][lang]+'</a>.</span>'
            for lang in ('nl','en','zh'))+'</p>'
        html, count = re.subn(r'<p class="micro" data-i18n="privacy">.*?</p>',privacy_note,html,count=1, flags=re.S)
        if count != 1:
            raise RuntimeError('Cannot locate homepage contact form privacy notice')
    page.write_text(html,encoding='utf-8')
    changed += 1
if changed < 3:
    raise RuntimeError('Unexpectedly few public pages updated')

updated_home = home.read_text(encoding='utf-8')
header = re.search(r'<header\b.*?</header>',updated_home,re.S).group(0)
preview = re.search(r'<div class="preview-note".*?</div>',updated_home,re.S).group(0)
footer = re.search(r'<footer\b.*?</footer>',updated_home,re.S).group(0)

company = {
'nl': '''<h1>Bedrijfsgegevens</h1><p>Informatie over de onderneming achter SeeSmartHome.</p><h2>Onderneming</h2><p><strong>Statutaire naam en handelsnaam:</strong> SeeSmartHome B.V.<br><strong>KVK-nummer:</strong> 42142350<br><strong>Statutaire zetel:</strong> Rotterdam, Nederland</p><h2>Contact</h2><p>E-mail: <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a><br>Telefoon / WhatsApp: <a href="tel:+31641670074">+31 6 4167 0074</a></p><h2>Vragen en klachten</h2><p>Stuur uw vraag of klacht met uw projectreferentie naar <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>. Wij nemen contact met u op om de kwestie te behandelen. Wettelijke consumentenrechten blijven van kracht.</p>''',
'en': '''<h1>Company details</h1><p>Information about the business behind SeeSmartHome.</p><h2>Company</h2><p><strong>Registered and trading name:</strong> SeeSmartHome B.V.<br><strong>Chamber of Commerce (KVK):</strong> 42142350<br><strong>Registered seat:</strong> Rotterdam, the Netherlands</p><h2>Contact</h2><p>Email: <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a><br>Phone / WhatsApp: <a href="tel:+31641670074">+31 6 4167 0074</a></p><h2>Questions and complaints</h2><p>Send your question or complaint with your project reference to <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>. We will contact you to handle the matter. Your statutory consumer rights remain unaffected.</p>''',
'zh': '''<h1>公司信息</h1><p>SeeSmartHome 的经营主体及联系方式。</p><h2>经营主体</h2><p><strong>公司法定名称及商号：</strong>SeeSmartHome B.V.<br><strong>荷兰商会注册号（KVK）：</strong>42142350<br><strong>法定所在地：</strong>荷兰鹿特丹</p><h2>联系我们</h2><p>邮箱：<a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a><br>电话／WhatsApp：<a href="tel:+31641670074">+31 6 4167 0074</a></p><h2>咨询及投诉</h2><p>如有疑问或投诉，请附上项目编号发送邮件至 <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>。我们会联系您处理，法定消费者权利不受影响。</p>''',
}

privacy = {
'nl': '''<h1>Privacyverklaring</h1><p class="legal-alert">Concept voor interne beoordeling. De feitelijke bewaartermijnen en internationale doorgiften moeten vóór de definitieve lancering worden gecontroleerd.</p><h2>1. Verwerkingsverantwoordelijke</h2><p>SeeSmartHome B.V., KVK 42142350, statutaire zetel Rotterdam. Privacyvragen: <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>.</p><h2>2. Welke gegevens en waarom?</h2><p>Bij een offerteaanvraag kunnen wij uw naam, e-mail, telefoonnummer, woonplaats, projecttype, projectomschrijving, gewenste contactwijze en vrijwillig opgegeven WhatsApp-nummer of WeChat-ID ontvangen. Wij gebruiken deze gegevens om uw aanvraag te behandelen, contact op te nemen, een offerte voor te bereiden en indien van toepassing de overeenkomst uit te voeren. Rechtsgrond: noodzakelijke stappen voorafgaand aan of uitvoering van een overeenkomst. Voor de beveiliging van het formulier en het voorkomen van misbruik kunnen beperkte technische gegevens worden verwerkt op basis van een gerechtvaardigd belang, na een belangenafweging. Voor fiscale administratie geldt waar van toepassing een wettelijke verplichting.</p><h2>3. Met wie delen wij gegevens?</h2><p>De website en het aanvraagformulier gebruiken Netlify; zakelijke e-mail loopt via Google Workspace. Wanneer u zelf kiest voor contact via WhatsApp of WeChat, kunnen gegevens ook door die diensten worden verwerkt. We delen gegevens alleen voor zover nodig om uw aanvraag en project af te handelen of wanneer dit wettelijk moet. Deel geen gevoelige persoonsgegevens via het formulier.</p><h2>4. Gegevens buiten de EER</h2><p>Bij gebruik van internationale leveranciers van digitale diensten of berichtenapps kan verwerking buiten de Europese Economische Ruimte plaatsvinden. De exacte verwerking en toepasselijke doorgiftewaarborgen moeten voor definitieve publicatie worden gecontroleerd. Neem contact met ons op voor actuele informatie.</p><h2>5. Bewaartermijnen</h2><p>Aanvraaggegevens bewaren wij niet langer dan nodig voor het afhandelen van de aanvraag en een noodzakelijke opvolging. Daarna worden zij verwijderd of geanonimiseerd, tenzij een overeenkomst, een geschil of een wettelijke bewaarplicht langere bewaring rechtvaardigt. Basisgegevens van de administratie worden in beginsel zeven jaar bewaard wanneer de fiscale bewaarplicht van toepassing is. Een concrete interne termijn voor niet-omgezette aanvragen wordt nog vastgesteld.</p><h2>6. Uw rechten</h2><p>U kunt verzoeken om inzage, correctie, verwijdering, beperking, overdraagbaarheid of bezwaar, voor zover wettelijk van toepassing. E-mail ons op <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>. U kunt ook een klacht indienen bij de <a href="https://autoriteitpersoonsgegevens.nl/" target="_blank" rel="noopener noreferrer">Autoriteit Persoonsgegevens</a>.</p><h2>7. Cookies en wijzigingen</h2><p>Het actuele gebruik van cookies en eventuele andere website-technologieën moet nog worden gecontroleerd. Als we analytische of marketingtechnologie toevoegen, passen wij deze verklaring en eventuele toestemmingsmechanismen waar nodig aan.</p>''',
'en': '''<h1>Privacy notice</h1><p class="legal-alert">Draft for internal review. Actual retention periods and international transfers must be checked before final launch.</p><h2>1. Controller</h2><p>SeeSmartHome B.V., KVK 42142350, registered seat Rotterdam. Privacy questions: <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>.</p><h2>2. Information and purposes</h2><p>When you request a quote we may receive your name, email, telephone number, city, project type and description, preferred contact method and any optional WhatsApp number or WeChat ID. We use these details to respond, prepare a quotation and, where applicable, perform a contract. The legal basis is taking steps before entering into or performing a contract. Limited technical data for form security and abuse prevention may be processed for legitimate interests, subject to a balancing assessment. Applicable tax records are retained to comply with legal obligations.</p><h2>3. Service providers</h2><p>We use Netlify to host this website and process inquiry forms, and Google Workspace for business email. If you choose WhatsApp or WeChat, those services may also process your contact information. We only share information where needed for your inquiry/project or when legally required. Do not send sensitive personal information through this form.</p><h2>4. Transfers outside the EEA</h2><p>International online services and messaging apps may process data outside the European Economic Area. Exact data flows and relevant transfer safeguards require verification before final publication. Contact us for up-to-date information.</p><h2>5. Retention</h2><p>We keep inquiries only as long as necessary to handle them and carry out necessary follow-up, after which they are deleted or anonymised unless a contract, dispute or statutory duty requires longer retention. Basic accounting records are generally retained for seven years where Dutch tax rules apply. A specific internal period for inquiries that do not become orders remains to be set.</p><h2>6. Your rights</h2><p>You may request access, correction, erasure, restriction, portability or object where applicable by emailing <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>. You may also complain to the Dutch <a href="https://autoriteitpersoonsgegevens.nl/" target="_blank" rel="noopener noreferrer">Data Protection Authority</a>.</p><h2>7. Cookies and updates</h2><p>Actual cookies and other site technologies are still being audited. If analytics or marketing tracking is added, we will update this notice and any applicable consent controls.</p>''',
'zh': '''<h1>隐私声明</h1><p class="legal-alert">本页为内部审核草稿。正式上线前还需核实实际保存期限及跨境数据处理保障措施。</p><h2>1. 个人资料控制方</h2><p>SeeSmartHome B.V.，KVK 42142350，法定所在地鹿特丹。隐私问题请联系 <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>。</p><h2>2. 收集哪些资料及用途</h2><p>您提交询价时，我们可能收到姓名、邮箱、电话、城市、项目类型及描述、首选联系方式，以及您自愿提供的 WhatsApp 号码或微信号。我们使用这些信息答复询价、准备报价，以及在适用时履行合同。相应法律依据为订约前应您要求采取的步骤或履行合同；用于防止表单滥用的必要技术信息可能基于经利益衡量的合法利益处理；依法须保存的税务资料基于法定义务处理。</p><h2>3. 服务商和资料共享</h2><p>网站及询价表单使用 Netlify，公司邮箱使用 Google Workspace。若您主动选择 WhatsApp 或微信联系，相应平台可能处理联系信息。我们仅在处理项目所需或法律要求时分享资料。请勿通过询价表单发送敏感个人资料。</p><h2>4. 欧洲经济区以外的数据</h2><p>国际数字服务及即时通讯平台可能在欧洲经济区以外处理数据。具体数据流和适用保障措施仍需在正式发布前核实；您可发邮件向我们询问最新情况。</p><h2>5. 保存期限</h2><p>询价资料仅保存至处理请求及必要后续沟通所需的期间，之后删除或匿名化；合同、争议或法定义务可能要求更长时间。适用荷兰税务保存义务时，基础会计记录一般须保存七年。未成交询价的内部具体期限仍待确定。</p><h2>6. 您的权利</h2><p>您可在适用法律范围内请求查阅、更正、删除、限制处理、数据可携带或提出反对，请邮件联系 <a href="mailto:info@seesmarthome.nl">info@seesmarthome.nl</a>。您也可以向荷兰 <a href="https://autoriteitpersoonsgegevens.nl/" target="_blank" rel="noopener noreferrer">个人资料保护监管机构</a>投诉。</p><h2>7. Cookie 与后续更新</h2><p>网站当前使用的 Cookie 与其他技术仍待核验；如果加入统计或广告追踪，我们会更新声明并在需要时建立同意机制。</p>''',
}

def make_page(name, body):
    title = 'Bedrijfsgegevens' if name == 'company' else 'Privacyverklaring'
    content = ''.join(f'<div data-legal-lang="{lang}"'+(' hidden' if lang != 'nl' else '')+'>'+body[lang]+'</div>' for lang in ('nl','en','zh'))
    page = ('<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow,noarchive"><meta name="description" content="SeeSmartHome B.V. · company information and privacy">'
            f'<title>{title} | SeeSmartHome</title><link rel="stylesheet" href="assets/site.css">'
            '<script src="assets/site.js" defer></script>'+css+js+'</head><body>'+header+preview+
            '<main class="wrap legal-main"><a href="index.html">← SeeSmartHome</a>'+content+'</main>'+footer+'</body></html>')
    if 'Muntplein' in page or '3437' in page or 'Bertus Aafjeshove' in page:
        raise RuntimeError('Residential address detected in generated page')
    (out/(name+'.html')).write_text(page,encoding='utf-8')

make_page('company', company)
make_page('privacy', privacy)
print(f'Added privacy draft and company information to {changed} public pages; address absent, indexing restrictions preserved')
