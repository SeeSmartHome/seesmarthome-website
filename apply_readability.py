#!/usr/bin/env python3
"""Include the typography accessibility stylesheet in generated public pages."""
from pathlib import Path
root = Path(__file__).resolve().parent / 'dist'
css = root / 'assets' / 'readability.css'
if not css.is_file():
    raise FileNotFoundError(css)
changed = 0
for page in root.rglob('*.html'):
    if page.relative_to(root).parts[0] == 'admin':
        continue
    text = page.read_text(encoding='utf-8')
    if 'readability.css' in text:
        continue
    if text.count('</head>') != 1:
        raise RuntimeError(f'Unexpected HTML head: {page}')
    prefix = '../' * (len(page.relative_to(root).parts) - 1)
    text = text.replace('</head>', f'<link rel="stylesheet" href="{prefix}assets/readability.css"></head>', 1)
    page.write_text(text, encoding='utf-8')
    changed += 1
if changed < 3:
    raise RuntimeError(f'Unexpectedly few pages updated: {changed}')
print(f'Applied readability stylesheet to {changed} public HTML pages')
