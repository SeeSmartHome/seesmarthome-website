#!/usr/bin/env python3
"""Add business messaging contacts to the generated homepage after build_site.py."""
from pathlib import Path

page = Path(__file__).resolve().parent / 'dist' / 'index.html'
html = page.read_text(encoding='utf-8')
anchor = '<form class="contact-form"'
assert html.count(anchor) == 1, 'Contact form not uniquely found'
contacts = '''<div class="messaging-contacts" aria-label="WhatsApp and WeChat" style="display:flex;flex-wrap:wrap;gap:14px;margin:24px 0;align-items:center"><a href="https://wa.me/31641670074" target="_blank" rel="noopener noreferrer" class="btn btn-primary" aria-label="Chat with SeeSmartHome on WhatsApp">WhatsApp · +31 6 4167 0074 ↗</a><span style="display:inline-flex;gap:8px;align-items:center;flex-wrap:wrap"><strong>WeChat:</strong> <code id="wechat-contact-id">zhirong1102</code> <button type="button" id="copy-wechat" style="border:1px solid currentColor;border-radius:6px;padding:7px 12px;background:transparent;cursor:pointer" data-contact-label="copy">Kopieer WeChat ID</button></span></div>'''
html = html.replace(anchor, contacts + anchor, 1)
needle = '<label><span data-i18n="message">'
assert html.count(needle) == 1, 'Message field not uniquely found'
fields = '''<label><span data-contact-label="preferred">Gewenste contactmethode</span><select name="preferred_contact_method"><option value="">Geen voorkeur / No preference</option><option value="email">Email</option><option value="phone">Telefoon / Phone</option><option value="whatsapp">WhatsApp</option><option value="wechat">WeChat</option></select></label><div class="form-row"><label><span data-contact-label="whatsapp">WhatsApp-nummer (optioneel)</span><input name="whatsapp_number" type="tel" autocomplete="tel" maxlength="40" placeholder="+31 …"></label><label><span data-contact-label="wechat">WeChat ID (optioneel)</span><input name="wechat_id" maxlength="100" autocomplete="off"></label></div>'''
html = html.replace(needle, fields + needle, 1)
script = '''<script>(function(){const text={nl:{copy:'Kopieer WeChat ID',copied:'Gekopieerd!',preferred:'Gewenste contactmethode',whatsapp:'WhatsApp-nummer (optioneel)',wechat:'WeChat ID (optioneel)'},en:{copy:'Copy WeChat ID',copied:'Copied!',preferred:'Preferred contact method',whatsapp:'WhatsApp number (optional)',wechat:'WeChat ID (optional)'},zh:{copy:'复制微信号',copied:'已复制',preferred:'希望通过什么方式联系',whatsapp:'WhatsApp 号码（选填）',wechat:'微信号（选填）'}};let current='nl';function render(){document.querySelectorAll('[data-contact-label]').forEach(el=>el.textContent=text[current][el.dataset.contactLabel]);}document.querySelectorAll('.lang-btn[data-lang]').forEach(b=>b.addEventListener('click',()=>{current=text[b.dataset.lang]?b.dataset.lang:'nl';render();}));document.getElementById('copy-wechat').addEventListener('click',async function(){try{await navigator.clipboard.writeText('zhirong1102');this.textContent=text[current].copied;}catch(e){const el=document.getElementById('wechat-contact-id');const range=document.createRange();range.selectNodeContents(el);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);this.textContent=text[current].copy;}});render();})();</script>'''
assert '</body>' in html
html = html.replace('</body>',script+'</body>',1)
page.write_text(html,encoding='utf-8')
print('Added WhatsApp, WeChat and contact preferences to generated homepage')
