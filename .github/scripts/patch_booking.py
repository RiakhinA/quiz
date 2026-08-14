from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Required name, explicitly optional phone.
s = s.replace(
    'data-bk-uk="Ваше ім’я" data-bk-ru="Ваше имя"></label><input class="form-input" id="inputName" type="text"',
    'data-bk-uk="Ваше ім’я *" data-bk-ru="Ваше имя *"></label><input class="form-input" id="inputName" type="text" required'
)
s = s.replace(
    'data-bk-uk="Телефон — якщо зручно" data-bk-ru="Телефон — если удобно"',
    'data-bk-uk="Телефон — необов’язково" data-bk-ru="Телефон — необязательно"'
)

# 2) Keep the helper text under the phone field from colliding with the input.
if '/* booking-contact-hint-fix */' not in s:
    s = s.replace(
        '</style>',
        '''\n/* booking-contact-hint-fix */\n.booking-contact-hint{position:static!important;display:block!important;margin-top:8px!important;line-height:1.45!important;font-size:12px!important;color:var(--muted)!important;}\n</style>''',
        1,
    )

# 3) Validate name before going to time selection and preserve entered contact data.
old_start = "function startBooking(){try{gtag('event','booking_start')}catch(e){};const n=document.getElementById('inputName')?.value||'';const c=document.getElementById('inputContact')?.value||'';if(document.getElementById('finalName'))document.getElementById('finalName').value=n;if(document.getElementById('finalContact'))document.getElementById('finalContact').value=c;bookingDay='today';bookingDate='';renderSlots();goTo('booking-time');renderBookingTexts()}"
new_start = "function startBooking(){const nameEl=document.getElementById('inputName');const n=(nameEl?.value||'').trim();if(!n){nameEl?.classList.add('error');nameEl?.focus();return}nameEl?.classList.remove('error');try{gtag('event','booking_start')}catch(e){};const c=document.getElementById('inputContact')?.value||'';if(document.getElementById('finalName'))document.getElementById('finalName').value=n;if(document.getElementById('finalContact'))document.getElementById('finalContact').value=c;bookingDay='today';bookingDate='';renderSlots();goTo('booking-time');renderBookingTexts()}"
s = s.replace(old_start, new_start)

# 4) Custom-time summary gets different wording.
old_summary = "function updateBookingSummary(){const txt=bookingDateLabel();['bookingSelectedText','bookingFinalSelected'].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=(lang==='uk'?'Обраний час: ':'Выбранное время: ')+txt})}"
new_summary = "function updateBookingSummary(){const txt=bookingDateLabel();const prefix=bookingCustom?(lang==='uk'?'Запропонований вами час: ':'Предложенное вами время: '):(lang==='uk'?'Обраний час: ':'Выбранное время: ');['bookingSelectedText','bookingFinalSelected'].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=prefix+txt})}"
s = s.replace(old_summary, new_summary)

# 5) Desktop QA carries name/phone/day/date into the test tab.
old_openqa = """  function openQa(screen,label){\n    const u=new URL(location.href);u.searchParams.set('qaBooking',screen);if(label)u.searchParams.set('qaLabel',label);window.open(u.toString(),'_blank');\n  }"""
new_openqa = """  function openQa(screen,label){\n    const u=new URL(location.href);\n    u.searchParams.set('qaBooking',screen);\n    if(label)u.searchParams.set('qaLabel',label);\n    const n=document.getElementById('inputName')?.value||document.getElementById('finalName')?.value||'';\n    const c=document.getElementById('inputContact')?.value||document.getElementById('finalContact')?.value||'';\n    if(n)u.searchParams.set('qaName',n);else u.searchParams.delete('qaName');\n    if(c)u.searchParams.set('qaPhone',c);else u.searchParams.delete('qaPhone');\n    u.searchParams.set('qaDay',typeof bookingDay!=='undefined'?bookingDay:'today');\n    if(typeof bookingDate!=='undefined'&&bookingDate)u.searchParams.set('qaDate',bookingDate);else u.searchParams.delete('qaDate');\n    window.open(u.toString(),'_blank');\n  }"""
s = s.replace(old_openqa, new_openqa)

old_qaload = "if(qa){window.addEventListener('load',()=>{setTimeout(()=>{try{if(qa==='custom'){goTo('customtime')}else if(qa==='comment'){bookingCustom='ТЕСТ: '+(qs.get('qaLabel')||'выбранное время');bookingDate='';bookingTime='';goTo('booking-comment');updateBookingSummary();renderBookingTexts()}}catch(e){console.error(e)}},100)})}"
new_qaload = "if(qa){window.addEventListener('load',()=>{setTimeout(()=>{try{const qn=qs.get('qaName')||'';const qp=qs.get('qaPhone')||'';bookingDay=qs.get('qaDay')||'today';bookingDate=qs.get('qaDate')||'';if(document.getElementById('inputName'))document.getElementById('inputName').value=qn;if(document.getElementById('finalName'))document.getElementById('finalName').value=qn;if(document.getElementById('inputContact'))document.getElementById('inputContact').value=qp;if(document.getElementById('finalContact'))document.getElementById('finalContact').value=qp;if(qa==='custom'){goTo('customtime')}else if(qa==='comment'){bookingCustom='';bookingTime=qs.get('qaLabel')||'';goTo('booking-comment');updateBookingSummary();renderBookingTexts()}}catch(e){console.error(e)}},100)})}"
s = s.replace(old_qaload, new_qaload)

# 6) Viber fallback if direct personal chat doesn't open.
s = s.replace(
    '<a class="messenger-btn" href="viber://chat?number=%2B380935503707" onclick="trackMessengerLink(event,\'Viber\')">',
    '<a class="messenger-btn" href="viber://chat?number=%2B380935503707" onclick="return openViberFallback(event)">'
)
if 'function openViberFallback' not in s:
    insert = """
function openViberFallback(ev){
  try{trackMessengerLink(ev,'Viber')}catch(e){ev.preventDefault()}
  try{navigator.clipboard.writeText('+380935503707')}catch(e){}
  setTimeout(()=>{if(!document.hidden){alert(lang==='uk'?'Viber не відкрив чат автоматично. Номер +380935503707 скопійовано — відкрийте Viber і вставте його.':'Viber не открыл чат автоматически. Номер +380935503707 скопирован — откройте Viber и вставьте его.')}},1200)
  return true
}
"""
    s = s.replace('// BOOKING_FLOW_JS_END', insert + '\n// BOOKING_FLOW_JS_END', 1)

p.write_text(s, encoding='utf-8')
