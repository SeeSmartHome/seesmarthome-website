#!/usr/bin/env python3
"""Build the static SeeSmartHome site from Decap-edited JSON; stdlib only."""
from pathlib import Path
from html import escape
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
DATA = json.loads((ROOT / 'content/projects.json').read_text(encoding='utf-8'))
MEDIA = json.loads((ROOT / 'content/site-media.json').read_text(encoding='utf-8'))
SITEJS = (ROOT / 'assets/site.js').read_text(encoding='utf-8')
found = re.search(r'const data=(\{.*?\});let lang=', SITEJS, flags=re.S)
if not found:
    raise RuntimeError('Cannot locate existing three-language dictionary in site.js')
site_data = json.loads(found.group(1))


def safe(v):
    return escape(str(v or ''), quote=True)


def validate_path(v):
    # CMS uploads are local asset paths, not arbitrary scripts/external URLs.
    if not isinstance(v, str) or not v.startswith('/assets/') or '..' in v or '\\' in v or '"' in v:
        raise ValueError(f'Unsafe or invalid asset reference: {v!r}')
    if not (ROOT / v.lstrip('/')).is_file():
        raise FileNotFoundError(f'Image/video missing from source: {v}')
    return v


def title(p, lang): return p.get('title_'+lang, '')
def category(p, lang): return p.get('category_'+lang, '')
def description(p, lang): return p.get('description_'+lang, '')

projects = []
seen = set()
for p in DATA.get('projects', []):
    slug = p.get('slug', '')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in seen:
        raise ValueError(f'Invalid/duplicate project URL slug: {slug}')
    seen.add(slug)
    for lang in ('nl','en','zh'):
        if not title(p,lang).strip() or not category(p,lang).strip() or not description(p,lang).strip():
            raise ValueError(f'Missing {lang} title/category/description for {slug}')
    cover = validate_path(p['cover'])
    gallery = [validate_path(i) for i in p.get('images', [])]
    if not gallery: gallery = [cover]
    p = dict(p, cover=cover, images=gallery)
    if p.get('published',False): projects.append(p)
projects.sort(key=lambda p:(int(p.get('order',50)),p['slug']))
for v in MEDIA.values(): validate_path(v)

# Sync site.js's existing language logic with CMS-edited projects.
site_data['projects'] = {}
for p in projects:
    site_data['projects'][p['slug']] = {
        'name':{x:title(p,x) for x in ('nl','en','zh')},
        'cat':{x:category(p,x) for x in ('nl','en','zh')},
        'description':{x:description(p,x) for x in ('nl','en','zh')},
        'details':{x:p.get('details_'+x,[]) or [] for x in ('nl','en','zh')},
        'images':[v.lstrip('/').replace('assets/','',1) for v in p['images']],
        'status':'collab'
    }
new_js = SITEJS[:found.start(1)] + json.dumps(site_data,ensure_ascii=False,separators=(',',':')) + SITEJS[found.end(1):]

if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
for source in ROOT.iterdir():
    if source.name in {'dist', 'content', 'build_site.py', 'prepare_content.py', 'README-CMS.md', 'netlify.toml', '.gitignore'} or source.name.startswith('.'):
        continue
    if source.is_file(): shutil.copy2(source,OUT/source.name)
    elif source.is_dir(): shutil.copytree(source, OUT/source.name)
(OUT/'assets/site.js').write_text(new_js,encoding='utf-8')


def card(p, prefix='', featured=False):
    href=f'{prefix}{p["slug"]}.html'
    img=safe(('../' if not prefix else '') + p['cover'].lstrip('/'))
    name=safe(title(p,'nl'))
    cat=safe(category(p,'nl'))
    slug=safe(p['slug'])
    return (f'<article class="project-card {"featured" if featured else ""}">'
        f'<a class="project-pic" href="{href}"><img src="{img}" alt="{name}" loading="lazy" decoding="async">'
        '<span class="image-arrow" aria-hidden="true">↗</span></a>'
        '<div class="card-bottom"><div>'
        f'<span class="micro" data-project="{slug}" data-field="cat">{cat}</span>'
        f'<h3><a href="{href}" data-project="{slug}" data-field="name">{name}</a></h3>'
        f'</div><a class="mini-arrow" href="{href}" aria-label="View project">↗</a></div></article>')

home = (OUT/'index.html').read_text(encoding='utf-8')
featured = sorted((p for p in projects if p.get('featured',False)), key=lambda p:(int(p.get('featured_order',99)),int(p.get('order',50))))[:3]
if not featured: featured=projects[:3]
if featured:
    main = card(featured[0], prefix='projects/', featured=True)
    side = ''.join(card(p,prefix='projects/') for p in featured[1:])
    repl = '<div class="feature-grid">'+ main + f'<div class="feature-side">{side}</div></div><div class="section-end">'
else:
    repl = '<div class="feature-grid"></div><div class="section-end">'
home,n = re.subn(r'<div class="feature-grid">.*?</div><div class="section-end">',repl,home,count=1,flags=re.S)
if n != 1: raise RuntimeError('Homepage featured projects container not found')
home = home.replace('src="assets/hero-walk-in-closet.jpeg"',f'src="{safe(MEDIA["hero_image"].lstrip("/"))}"')
home = home.replace('src="assets/custom-interiors-poster.jpg"',f'src="{safe(MEDIA["video_poster"].lstrip("/"))}"')
home = home.replace('src="assets/custom-interiors-project-video.mp4"',f'src="{safe(MEDIA["project_video"].lstrip("/"))}"')
(OUT/'index.html').write_text(home, encoding='utf-8')

listing_path=OUT/'projects/index.html'
listing=listing_path.read_text(encoding='utf-8')
listing,n = re.subn(r'<section class="wrap projects-grid">.*?</section>',
    '<section class="wrap projects-grid">'+''.join(card(p) for p in projects)+'</section>',
    listing,count=1,flags=re.S)
if n != 1: raise RuntimeError('Portfolio listing section not found')
listing=listing.replace('src="../assets/custom-interiors-poster.jpg"',f'src="../{safe(MEDIA["video_poster"].lstrip("/"))}"')
listing=listing.replace('src="../assets/custom-interiors-project-video.mp4"',f'src="../{safe(MEDIA["project_video"].lstrip("/"))}"')
listing_path.write_text(listing,encoding='utf-8')

# Use existing branded header/footer and all existing responsive CSS for each generated detail page.
template=(ROOT/'projects/bedroom.html').read_text(encoding='utf-8')
header=re.search(r'<header .*?</header>',template,re.S).group(0)
preview=re.search(r'<div class="preview-note".*?</div>',template,re.S).group(0)
footer=re.search(r'<footer .*?</footer>',template,re.S).group(0)

for p in projects:
    slug=safe(p['slug']); name=safe(title(p,'nl'))
    desc=safe(description(p,'nl')); cat=safe(category(p,'nl'))
    details=p.get('details_nl',[]) or []
    details_html=''.join(f'<li data-project="{slug}" data-field="details" data-detail="{i}">{safe(x)}</li>' for i,x in enumerate(details))
    gallery=''.join(
      f'<figure class="gallery-item"><img src="../{safe(src.lstrip("/"))}" alt="{name} · {i+1}" loading="lazy" decoding="async">'
      f'<figcaption><span>{i+1:02d} / {len(p["images"]):02d}</span> <span data-project="{slug}" data-field="cat">{cat}</span></figcaption></figure>'
      for i,src in enumerate(p['images']))
    main=f'''<main><section class="wrap detail-top"><a href="index.html" class="text-link" data-i18n="back">← Alle projecten</a>
      <span class="eyebrow">{safe(p.get('credit','SeeSmartHome × MINCHO'))}</span>
      <h1 data-project="{slug}" data-field="name">{name}</h1><p data-project="{slug}" data-field="description">{desc}</p></section>
      <div class="detail-hero wrap"><img src="../{safe(p['cover'].lstrip("/"))}" alt="{name}" loading="eager" decoding="async"></div>
      <section class="wrap detail-description"><div><span class="eyebrow" data-i18n="summary">Over deze beeldselectie</span>
      <h2 data-project="{slug}" data-field="name">{name}</h2><p data-project="{slug}" data-field="description">{desc}</p></div>
      <aside><span class="eyebrow" data-i18n="details">Zichtbare details</span><ul>{details_html}</ul></aside></section>
      <section class="wrap detail-gallery"><div class="section-label"><span data-i18n="gallery">Fotogalerij</span><span>{len(p['images']):02d} IMAGES</span></div>
      <div class="gallery-grid">{gallery}</div><p class="image-note">{safe(p.get('image_notice',''))}</p></section>
      <section class="cta-band"><div class="wrap cta-band-inner"><h2 data-i18n="similar">Een vergelijkbaar project bespreken?</h2>
      <a class="btn btn-primary" data-i18n="cta" href="../index.html?project={slug}#contact">Vraag een offerte aan</a></div></section></main>'''
    page=f'<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    page+=f'<meta name="robots" content="noindex,nofollow,noarchive"><meta name="description" content="{safe(description(p,"nl")[:155])}">'
    page+=f'<title>{name} | SeeSmartHome</title><link rel="stylesheet" href="../assets/site.css"><script src="../assets/site.js" defer></script></head><body>'
    page+=header+preview+main+footer+'</body></html>'
    (OUT/'projects'/f'{p["slug"]}.html').write_text(page, encoding='utf-8')

# Remove old detail pages that have no published matching CMS record.
keep={f'{p["slug"]}.html' for p in projects}|{'index.html','materials.html'}
for old in (OUT/'projects').glob('*.html'):
    if old.name not in keep: old.unlink()


# Existing service cards in the V8 template may point to a project that was
# unpublished in the CMS. Keep service images, but redirect their links to the
# portfolio overview so visitors never encounter broken project links.
unpublished = seen - {p['slug'] for p in projects}
for path in OUT.rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    for slug in unpublished:
        if path.parent == OUT:
            text = text.replace(f'href="projects/{slug}.html"', 'href="projects/index.html"')
        elif path.parent == OUT/'projects':
            text = text.replace(f'href="{slug}.html"', 'href="index.html"')
            text = text.replace(f'href="../projects/{slug}.html"', 'href="index.html"')
    path.write_text(text,encoding='utf-8')

print(f'Built {len(projects)} published project pages and homepage with {len(featured)} featured items → {OUT}')
