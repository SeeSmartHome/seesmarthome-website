#!/usr/bin/env python3
"""Keep business WhatsApp clickable while removing the number from visible site text.
Run after launch_site.py; the wa.me URL necessarily still contains the number.
"""
from pathlib import Path
import re

out = Path(__file__).resolve().parent / 'dist'
if not (out / 'index.html').is_file() or not (out / 'company.html').is_file():
    raise RuntimeError('Expected generated public pages are missing')

number = '31641670074'
formatted = '+31 6 4167 0074'
link = f'https://wa.me/{number}'
replacements = 0

for page in out.rglob('*.html'):
    if 'admin' in page.relative_to(out).parts:
        continue
    html = page.read_text(encoding='utf-8')

    # Convert the company page's previously displayed telephone number to a
    # WhatsApp-only link; keep the contact option without printing the digits.
    html, converted = re.subn(
        rf'<a href="tel:\+{number}">\+31 6 4167 0074</a>',
        f'<a href="{link}" target="_blank" rel="noopener noreferrer" aria-label="Chat with SeeSmartHome on WhatsApp">WhatsApp ↗</a>',
        html,
    )
    replacements += converted
    html = html.replace('Telefoon / WhatsApp:', 'WhatsApp:')
    html = html.replace('Phone / WhatsApp:', 'WhatsApp:')
    html = html.replace('电话／WhatsApp：', 'WhatsApp：')

    # Preserve existing URL, styling and accessibility attributes on every
    # WhatsApp button; change only what the visitor sees on the button.
    html, relabelled = re.subn(
        rf'(<a\b[^>]*href="{re.escape(link)}"[^>]*>).*?(</a>)',
        lambda match: match.group(1) + 'WhatsApp ↗' + match.group(2),
        html,
        flags=re.S,
    )
    replacements += relabelled

    # The digit sequence is allowed only inside the wa.me link target, not as
    # visible copy, phone links or unrelated HTML attributes.
    without_link_target = html.replace(link, '[WHATSAPP_LINK]')
    if formatted in without_link_target or number in without_link_target or 'tel:+31641670074' in without_link_target:
        raise RuntimeError('Publicly displayed phone number remains in ' + str(page.relative_to(out)))
    page.write_text(html, encoding='utf-8')

if replacements < 4:
    raise RuntimeError(f'Expected homepage and company WhatsApp links, found {replacements} replacements')
print(f'WhatsApp button retained and visible phone number removed from generated pages ({replacements} links checked).')
