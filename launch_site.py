#!/usr/bin/env python3
"""Finalize the generated public website for search engines without exposing a home address.
Run last, after all page-generating and page-editing build steps.
"""
from pathlib import Path
from html import escape
from datetime import date
import json
import re

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
BASE = 'https://seesmarthome.nl'
if not (OUT / 'index.html').is_file() or not (OUT / 'company.html').is_file():
    raise RuntimeError('Expected site and company pages were not generated')

# The old design bundle included duplicate homepage files and obsolete root-level project
# snapshots. They must not become indexable alternatives to the CMS-generated pages.
allowed_root = {'index.html', 'company.html', 'privacy.html', 'thank-you.html'}
for obsolete in OUT.glob('*.html'):
    if obsolete.name not in allowed_root:
        obsolete.unlink()

pages = [Path('index.html'), Path('company.html'), Path('projects/index.html'), Path('projects/materials.html')]
projects = json.loads((ROOT / 'content/projects.json').read_text(encoding='utf-8'))
for item in projects.get('projects', []):
    if item.get('published', False):
        pages.append(Path('projects') / (item['slug'] + '.html'))

preview = re.compile(r'<div\s+class="preview-note"[^>]*>.*?</div>', re.S | re.I)
robots_tag = re.compile(r'<meta\s+name=["\']robots["\'][^>]*>', re.I)
footer_preview = re.compile(r'<span\s+data-i18n="footer">.*?</span>', re.S | re.I)

for rel in pages + [Path('privacy.html'), Path('thank-you.html')]:
    path = OUT / rel
    if not path.is_file():
        if rel == Path('thank-you.html'):
            continue
        raise FileNotFoundError(str(path))
    html = path.read_text(encoding='utf-8')
    html = preview.sub('', html)
    html = footer_preview.sub('<span>SeeSmartHome B.V. · Maatwerk interieurs</span>', html)
    # Remove all old indexing directives on pages we genuinely want indexed.
    html = robots_tag.sub('', html)
    if rel in pages:
        canonical = BASE + ('/' if rel == Path('index.html') else '/' + rel.as_posix())
        head = ('<meta name="robots" content="index,follow">'
                '<link rel="canonical" href="' + escape(canonical, quote=True) + '">')
        if rel == Path('index.html'):
            html = re.sub(r'<meta\s+name="description"\s+content="[^"]*">',
                          '<meta name="description" content="SeeSmartHome B.V.: maatwerk kasten, garderobes en complete interieurs in Nederland. Van ontwerp en productie tot levering en montage.">',
                          html, count=1)
        html = html.replace('</head>', head + '</head>', 1)
    else:
        # The privacy notice contains facts still awaiting confirmation; the submission
        # confirmation page is not useful in search. Both remain available to visitors.
        html = html.replace('</head>', '<meta name="robots" content="noindex,follow"></head>', 1)
    if 'INTERNAL PREVIEW' in html or 'INTERNE PREVIEW' in html or '内部预览' in html:
        raise RuntimeError('Visible preview notice remains: ' + str(rel))
    if 'Muntplein' in html or 'Bertus Aafjeshove' in html or '3437 AS' in html:
        raise RuntimeError('Private address detected: ' + str(rel))
    path.write_text(html, encoding='utf-8')

# A sitemap should include only the publicly indexable canonical pages, never the admin,
# privacy draft or form submission confirmation.
urls = []
for rel in pages:
    if not (OUT / rel).is_file():
        raise FileNotFoundError('Missing sitemap page: ' + str(rel))
    url = BASE + ('/' if rel == Path('index.html') else '/' + rel.as_posix())
    urls.append('  <url><loc>' + escape(url) + '</loc></url>')
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + '\n'.join(urls) + '\n</urlset>\n', encoding='utf-8')
(OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /admin/\n'
    'Sitemap: https://seesmarthome.nl/sitemap.xml\n', encoding='utf-8')

headers = (OUT / '_headers').read_text(encoding='utf-8') if (OUT / '_headers').exists() else ''
if re.search(r'^/\*\s*\n\s*X-Robots-Tag:\s*noindex', headers, re.M | re.I):
    raise RuntimeError('Global noindex remains in HTTP headers')
for rel in pages:
    text = (OUT / rel).read_text(encoding='utf-8')
    if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', text, re.I):
        raise RuntimeError('Searchable page still noindexed: ' + str(rel))
print(f'Public launch build: {len(pages)} canonical URLs, sitemap and robots.txt; no preview banners or residential address.')
