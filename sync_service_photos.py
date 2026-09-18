#!/usr/bin/env python3
"""Use the current green-studio CMS gallery for its homepage service tile."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parent
projects = json.loads((root / 'content/projects.json').read_text(encoding='utf-8'))['projects']
green = next((p for p in projects if p.get('slug') == 'green-studio'), None)
if green is None:
    raise RuntimeError('green-studio project not found')
images = green.get('images') or [green['cover']]
# A shelving-focused angle is more legible at the service-tile crop.
image = images[2] if len(images) > 2 else green['cover']
if not image.startswith('/assets/') or not (root / image.lstrip('/')).is_file():
    raise RuntimeError(f'Homepage service photo missing: {image}')
page = root / 'dist/index.html'
html = page.read_text(encoding='utf-8')
pattern = r'(<a href="projects/green-studio\.html"><div class="service-picture"><img\b[^>]*?\bsrc=")[^"]+("[^>]*>)'
html, count = re.subn(pattern, lambda m: m.group(1) + image.lstrip('/') + m.group(2), html, count=1)
if count != 1:
    raise RuntimeError('Green studio homepage service photo not found uniquely')
page.write_text(html, encoding='utf-8')
print(f'Synced green-studio homepage service tile to {image}')
