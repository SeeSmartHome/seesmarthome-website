#!/usr/bin/env python3
"""Build the CMS-editable FAQ into the homepage, plus FAQ links on public pages."""
from pathlib import Path
from html import escape
import json
import re

root = Path(__file__).resolve().parent
out = root / 'dist'
data = json.loads((root / 'content/faq.json').read_text(encoding='utf-8'))
languages = ('nl', 'en', 'zh')
category_names = {
    'delivery': {'nl': 'Levering & logistiek', 'en': 'Delivery & logistics', 'zh': '运输与交付'},
    'payment': {'nl': 'Offerte & betaling', 'en': 'Quotation & payment', 'zh': '报价与付款'},
    'warranty': {'nl': 'Garantie & nazorg', 'en': 'Warranty & aftercare', 'zh': '质保与售后'},
}

def safe(value):
    return escape(str(value), quote=True)

def versions(values, tag='span', cls=''):
    class_attr = f' class="{cls}"' if cls else ''
    return ''.join(
        f'<{tag}{class_attr} data-faq-lang="{lang}"{(" hidden" if lang != "nl" else "")}>{safe(values[lang])}</{tag}>'
        for lang in languages
    )

items = []
for item in data.get('items', []):
    if item.get('category') not in category_names:
        raise ValueError('Unknown FAQ category: ' + str(item.get('category')))
    for language in languages:
        for field in ('question', 'answer'):
            value = item.get(f'{field}_{language}')
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f'FAQ missing {field}_{language}: {item!r}')
    if item.get('published', True):
        items.append(item)
items.sort(key=lambda item: (int(item.get('order', 50)), item['question_nl']))

groups = []
for idx, (category, names) in enumerate(category_names.items(), 1):
    entries = [item for item in items if item['category'] == category]
    if not entries:
        continue
    questions = []
    for item in entries:
        heading = versions({lang: item['question_' + lang] for lang in languages})
        answer = versions({lang: item['answer_' + lang] for lang in languages}, tag='div', cls='faq-answer')
        questions.append(f'<details class="faq-item"><summary>{heading}</summary>{answer}</details>')
    groups.append(
        f'<div class="faq-group"><div><span class="faq-category-index">{idx:02d} / FAQ</span>'
        f'<h3>{versions(names)}</h3></div><div class="faq-list">{"".join(questions)}</div></div>'
    )

if not groups:
    raise ValueError('No published FAQ items')

heading = {'nl': 'Veelgestelde vragen.', 'en': 'Frequently asked questions.', 'zh': '常见问题解答。'}
intro = {
    'nl': 'Heldere antwoorden over de weg van ontwerp naar levering, betaling en nazorg.',
    'en': 'Straightforward answers about the journey from design to delivery, payment and aftercare.',
    'zh': '关于定制流程、国际运输、付款方式和安装后售后的常见疑问。',
}
note = {
    'nl': 'Dit is algemene informatie. Uw offerte en overeenkomst leggen projectspecifieke afspraken vast. Wettelijke consumentenrechten blijven altijd gelden.',
    'en': 'This is general information. Project-specific arrangements are recorded in your quotation and agreement. Statutory consumer rights always remain in force.',
    'zh': '以上为一般性说明。具体服务范围、时间和付款安排以项目报价及合同约定为准，消费者法定权利不受影响。',
}
section = (
    '<section class="section wrap faq-section" id="faq" aria-labelledby="faq-heading">'
    '<div class="section-label"><span>04 / FAQ</span><span>SEESMARTHOME / SERVICE</span></div>'
    '<div class="faq-heading"><h2 id="faq-heading">' + versions(heading) + '</h2><p>' + versions(intro) + '</p></div>'
    + ''.join(groups) + '<p class="faq-note">' + versions(note) + '</p></section>\n'
)

home = out / 'index.html'
html = home.read_text(encoding='utf-8')
anchor = '<section class="contact section wrap" id="contact">'
if html.count(anchor) != 1:
    raise RuntimeError('Cannot uniquely locate homepage contact section')
if 'id="faq"' in html:
    raise RuntimeError('FAQ already installed')
html = html.replace(anchor, section + anchor, 1)
home.write_text(html, encoding='utf-8')

changed = 0
for page in out.rglob('*.html'):
    rel = page.relative_to(out)
    if rel.parts[0] == 'admin':
        continue
    html = page.read_text(encoding='utf-8')
    if 'assets/faq.css' in html:
        raise RuntimeError(f'FAQ styles already installed in {rel}')
    if html.count('</head>') != 1:
        raise RuntimeError(f'Missing head in {rel}')
    prefix = '../' * (len(rel.parts) - 1)
    # Add only one direct navigation and one footer link per page; retain existing links.
    faq_href = '#faq' if rel == Path('index.html') else prefix + 'index.html#faq'
    nav_link = f'<a href="{faq_href}">FAQ</a>'
    nav_pattern = r'(<nav class="nav" id="nav">)(.*?)(</nav>)'
    def add_nav(match):
        inner = match.group(2)
        needle = '<a data-i18n="contact"'
        if needle not in inner:
            raise RuntimeError(f'Cannot locate nav contact in {rel}')
        return match.group(1) + inner.replace(needle, nav_link + needle, 1) + match.group(3)
    html, num_nav = re.subn(nav_pattern, add_nav, html, count=1, flags=re.S)
    if num_nav != 1:
        raise RuntimeError(f'Cannot locate nav in {rel}')
    footer_pattern = r'(<div class="footer-nav">)(.*?)(</div>)'
    def add_footer(match):
        inner = match.group(2)
        needle = '<a data-i18n="contact"'
        if needle not in inner:
            raise RuntimeError(f'Cannot locate footer contact in {rel}')
        return match.group(1) + inner.replace(needle, nav_link + needle, 1) + match.group(3)
    html, num_footer = re.subn(footer_pattern, add_footer, html, count=1, flags=re.S)
    if num_footer != 1:
        raise RuntimeError(f'Cannot locate footer in {rel}')
    html = html.replace('</head>', f'<link rel="stylesheet" href="{prefix}assets/faq.css"><script src="{prefix}assets/faq.js" defer></script></head>', 1)
    page.write_text(html, encoding='utf-8')
    changed += 1
if changed < 3:
    raise RuntimeError(f'Unexpectedly few pages received FAQ links: {changed}')
print(f'FAQ: {len(items)} published answers across {len(groups)} categories; updated {changed} pages')
