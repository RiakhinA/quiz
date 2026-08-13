from pathlib import Path
p=Path('index.html'); s=p.read_text()

s=s.replace("document.getElementById('progressFill').style.width = ((currentQ / qs.length) * 100) + '%';", "document.getElementById('progressFill').style.width = (((currentQ + 1) / qs.length) * 100) + '%';")
s=s.replace("  selectedOpts = [];\n\n  document.getElementById('qLabel')", "  selectedOpts = Array.isArray(answerIdx[currentQ]) ? answerIdx[currentQ].slice() : [];\n\n  document.getElementById('qLabel')")
s=s.replace("    card.onclick = () => selectOpt(card, i, q.multi);\n    grid.appendChild(card);", "    if (selectedOpts.includes(i)) card.classList.add('selected');\n    card.onclick = () => selectOpt(card, i, q.multi);\n    grid.appendChild(card);")

start=s.index('async function submitForm() {'); end=s.index('\nfunction escapeHtml',start)
submit="""async function submitForm() {
  const nameEl=document.getElementById('inputName'); const contactEl=document.getElementById('inputContact');
  const name=nameEl.value.trim(); const contact=contactEl.value.trim(); let ok=true;
  if(!name){nameEl.classList.add('error');ok=false;} if(!validContact(contact)){contactEl.classList.add('error');ok=false;} if(!ok)return;
  userName=name; const btn=document.getElementById('btnSubmit'); btn.disabled=true;
  const oldLabel=btn.querySelector('span').textContent; btn.querySelector('span').textContent='...';
  const qs=T[lang].questions; const answerTexts=qs.map((q,i)=>(answerIdx[i]||[]).map(idx=>q.opts[idx]?.t).filter(Boolean).join(', '));
  try{
    const response=await fetch('/api/send-lead',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,contact,lang,answerTexts,questions:qs.map(q=>q.q)})});
    if(!response.ok)throw new Error('Lead endpoint returned '+response.status);
    try{gtag('event','generate_lead')}catch(e){} try{if(typeof fbq==='function')fbq('track','Lead')}catch(e){} showThanks();
  }catch(e){console.error('Lead submission error:',e);btn.disabled=false;btn.querySelector('span').textContent=oldLabel;alert(lang==='uk'?'Не вдалося надіслати заявку. Спробуйте ще раз.':'Не удалось отправить заявку. Попробуйте ещё раз.');}
}
"""
s=s[:start]+submit+s[end:]

s=s.replace('.form-privacy { font-size: 12px; color: var(--muted); text-align: center; margin-top: 14px; }','.form-privacy { font-size: 12px; color: var(--muted); text-align: center; margin-top: 14px; }\n.form-social{margin-top:24px;text-align:center}.form-social-title{font-size:13px;color:var(--muted);margin-bottom:11px}.social-links{display:grid;grid-template-columns:1fr 1fr;gap:10px}.social-link{display:flex;align-items:center;justify-content:center;min-height:42px;padding:10px 12px;border:1px solid var(--border);border-radius:11px;background:var(--white);color:var(--text);text-decoration:none;font-size:13px;font-weight:700;transition:all .2s}.social-link:hover{border-color:var(--teal);color:var(--teal);background:var(--teal-light)}',1)

s=s.replace('@media (max-width: 820px) {','@media (max-width: 960px) {',1)
s=s.replace('  .photo-card { max-width: 380px; }','  .photo-card { max-width: 380px; width:100%; margin:0 auto; }',1)
s=s.replace('  .map-frame { padding: 16px; }\n}','  .map-frame { padding: 16px; }\n  .lang-bar { position:relative; }\n}\n@media (max-width:560px){ .hero-wrap{padding:28px 16px 48px}.form-outer,.thanks-outer{padding:24px 16px}.form-card,.thanks-card{padding:28px 20px} }',1)

needle='''      <button class="btn-submit" id="btnSubmit" onclick="submitForm()"><span data-t="btnSubmit"></span></button>\n      <p class="form-privacy" data-t="privacy"></p>'''
html='''      <button class="btn-submit" id="btnSubmit" onclick="submitForm()"><span data-t="btnSubmit"></span></button>\n      <div class="form-social"><div class="form-social-title" data-t="socialTitle"></div><div class="social-links">\n        <a class="social-link" href="https://ig.me/m/anton_riakhin_psy" target="_blank" rel="noopener noreferrer">Instagram</a>\n        <a class="social-link" href="https://t.me/riakhin_anton" target="_blank" rel="noopener noreferrer">Telegram</a>\n      </div></div>\n      <p class="form-privacy" data-t="privacy"></p>'''
if 'href="https://ig.me/m/anton_riakhin_psy"' not in s:s=s.replace(needle,html,1)
s=s.replace('    btnSubmit: "Записатись на розбір →",\n    privacy:','    btnSubmit: "Записатись на розбір →",\n    socialTitle: "Або можете написати мені напряму",\n    privacy:',1)
s=s.replace('    btnSubmit: "Записаться на разбор →",\n    privacy:','    btnSubmit: "Записаться на разбор →",\n    socialTitle: "Или можете написать мне напрямую",\n    privacy:',1)
p.write_text(s)
