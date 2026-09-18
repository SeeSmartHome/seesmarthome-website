/* FAQ translations follow the existing three-language site buttons. */
(()=>{
  function showFAQ(lang){
    if(!['nl','en','zh'].includes(lang)) lang='nl';
    document.querySelectorAll('[data-faq-lang]').forEach(node=>{
      node.hidden=node.getAttribute('data-faq-lang')!==lang;
    });
  }
  document.querySelectorAll('.lang-btn[data-lang]').forEach(button=>{
    button.addEventListener('click',()=>showFAQ(button.getAttribute('data-lang')));
  });
  const active=document.querySelector('.lang-btn.active[data-lang]');
  showFAQ(active?active.getAttribute('data-lang'):'nl');
  document.addEventListener('DOMContentLoaded',()=>{
    const selected=document.querySelector('.lang-btn.active[data-lang]');
    showFAQ(selected?selected.getAttribute('data-lang'):'nl');
  });
})();
