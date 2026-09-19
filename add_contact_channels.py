#!/usr/bin/env python3
"""Add business WhatsApp link and customer-provided messaging fields to the generated homepage.
Do not publish an employee's/personal WeChat ID.
"""
from pathlib import Path

page = Path(__file__).resolve().parent / 'dist' / 'index.html'
html = page.read_text(encoding='utf-8')
anchor = '<form class="contact-form"'
assert html.count(anchor) == 1, 'Contact form not uniquely found'

# Retain the business WhatsApp contact, but never print a personal WeChat handle.
contacts = '''<div class="messaging-contacts" aria-label="Business WhatsApp" style="display:flex;flex-wrap:wrap;gap:14px;margin:24px 0;align-items:center"><a href="https://wa.me/31641670074" target="_blank" rel="noopener noreferrer" class="btn btn-primary" aria-label="Chat with SeeSmartHome on WhatsApp">WhatsApp · +31 6 4167 0074 ↗</a></div>'''
html = html.replace(anchor, contacts + anchor, 1)

# A visitor may supply WhatsApp OR WeChat. Email is genuinely optional.
old_email = '<span data-i18n="email">E-mailadres</span> *<input type="email" name="email" required'
assert html.count(old_email) == 1, 'Original required email field not uniquely found'
html = html.replace(old_email, '<span data-contact-label="emailOptional">E-mailadres (optioneel)</span><input type="email" name="email"', 1)

needle = '<label><span data-i18n="message">'
assert html.count(needle) == 1, 'Message field not uniquely found'
fields = '''<p class="micro" data-contact-label="hint">Laat minstens één contactgegeven achter: uw WhatsApp-nummer of WeChat-ID. Een e-mailadres is niet verplicht.</p><label><span data-contact-label="preferred">Voorkeur voor contact</span><select name="preferred_contact_method"><option value="">Geen voorkeur / No preference</option><option value="whatsapp">WhatsApp</option><option value="wechat">WeChat</option></select></label><div class="form-row"><label><span data-contact-label="whatsapp">Uw WhatsApp-nummer (of WeChat-ID)</span><input name="whatsapp_number" type="tel" autocomplete="tel" maxlength="40" placeholder="+31 …" required></label><label><span data-contact-label="wechat">Uw WeChat-ID (of WhatsApp-nummer)</span><input name="wechat_id" maxlength="100" autocomplete="off"></label></div>'''
html = html.replace(needle, fields + needle, 1)

script = '''<script>(function(){
const text={
 nl:{emailOptional:'E-mailadres (optioneel)',hint:'Laat minstens één contactgegeven achter: uw WhatsApp-nummer of WeChat-ID. Een e-mailadres is niet verplicht.',preferred:'Voorkeur voor contact',whatsapp:'Uw WhatsApp-nummer',wechat:'Uw WeChat-ID'},
 en:{emailOptional:'Email address (optional)',hint:'Please provide either your WhatsApp number or WeChat ID. Email is optional.',preferred:'Preferred contact method',whatsapp:'Your WhatsApp number',wechat:'Your WeChat ID'},
 zh:{emailOptional:'邮箱（选填）',hint:'请至少留下微信号或 WhatsApp 号码其中一项；不必填写邮箱。',preferred:'希望通过哪种方式联系',whatsapp:'您的 WhatsApp 号码',wechat:'您的微信号'}
};
let current=(document.querySelector('.lang-btn.active[data-lang]')||{}).dataset?.lang||'nl';
function render(){document.querySelectorAll('[data-contact-label]').forEach(function(el){var value=text[current]&&text[current][el.dataset.contactLabel];if(value){el.textContent=value;}});}
document.querySelectorAll('.lang-btn[data-lang]').forEach(function(b){b.addEventListener('click',function(){current=text[b.dataset.lang]?b.dataset.lang:'nl';render();});});
const wa=document.querySelector('[name="whatsapp_number"]');
const wx=document.querySelector('[name="wechat_id"]');
function syncRequired(){const empty=!(wa.value.trim()||wx.value.trim());wa.required=empty;wx.required=empty;}
wa.addEventListener('input',syncRequired);
wx.addEventListener('input',syncRequired);
syncRequired();render();
})();</script>'''
assert html.count('</body>') == 1
html = html.replace('</body>', script + '</body>', 1)
page.write_text(html, encoding='utf-8')
print('Added business WhatsApp and customer-provided messaging fields; personal WeChat removed, email optional')
