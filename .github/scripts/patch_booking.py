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

# 2) Layout fixes: helper text below phone; final contact options as info cards; remove redundant footer copy.
if '/* booking-contact-hint-fix */' not in s:
    s = s.replace(
        '</style>',
        '''\n/* booking-contact-hint-fix */\n.booking-contact-hint{position:static!important;display:block!important;margin-top:8px!important;line-height:1.45!important;font-size:12px!important;color:var(--muted)!important;}\n</style>''',
        1,
    )

if '/* booking-contact-option-cards */' not in s:
    s = s.replace(
        '</style>',
        '''\n/* booking-contact-option-cards */\n#screen-booking-contact .booking-option-card{background:var(--teal-light);border:1px solid rgba(46,110,107,.20);border-radius:12px;padding:12px 14px;color:var(--teal-dark);font-weight:600;line-height:1.5;margin:12px 0 16px;}\n#screen-booking-contact .booking-note,#screen-booking-contact .form-privacy{display:none!important;}\n</style>''',
        1,
    )

s = s.replace(
    '<p class="booking-sub" data-bk-uk="Варіант 1 — залиште ім’я і номер та виберіть, у якому месенджері вам зручніше отримати підтвердження. Я напишу вам сам." data-bk-ru="Вариант 1 — оставьте имя и номер и выберите, в каком мессенджере вам удобнее получить подтверждение. Я напишу вам сам."></p>',
    '<p class="booking-sub booking-option-card" data-bk-uk="Варіант 1 — залиште ім’я і номер та виберіть, у якому месенджері вам зручніше отримати підтвердження. Я напишу вам сам." data-bk-ru="Вариант 1 — оставьте имя и номер и выберите, в каком мессенджере вам удобнее получить подтверждение. Я сам вам напишу."></p>'
)
s = s.replace(
    '<div class="booking-divider" data-bk-uk="або" data-bk-ru="или"></div><p class="booking-sub" data-bk-uk="Варіант 2 — напишіть мені самі в одній зі зручних соцмереж або месенджерів. Я вже отримаю вибраний час і ваш коментар." data-bk-ru="Вариант 2 — напишите мне сами в одной из удобных соцсетей или мессенджеров. Я уже получу выбранное время и ваш комментарий."></p>',
    '<div class="booking-divider" data-bk-uk="або" data-bk-ru="или"></div><p class="booking-sub booking-option-card" data-bk-uk="Варіант 2 — напишіть мені самі в одній зі зручних соцмереж або месенджерів. Я вже отримаю вибраний час і ваш коментар." data-bk-ru="Вариант 2 — напишите мне сами в одной из удобных соцсетей или мессенджеров. Я уже получу выбранное время и ваш комментарий."></p>'
)

# 3) Validate name before going to time selection and preserve entered contact data.
old_start = "function startBooking(){try{gtag('event','booking_start')}catch(e){};const n=document.getElementById('inputName')?.value||'';const c=document.getElementById('inputContact')?.value||'';if(document.getElementById('finalName'))document.getElementById('finalName').value=n;if(document.getElementById('finalContact'))document.getElementById('finalContact').value=c;bookingDay='today';bookingDate='';renderSlots();goTo('booking-time');renderBookingTexts()}"
new_start = "function startBooking(){const nameEl=document.getElementById('inputName');const n=(nameEl?.value||'').trim();if(!n){nameEl?.classList.add('error');nameEl?.focus();return}nameEl?.classList.remove('error');try{gtag('event','booking_start')}catch(e){};const c=document.getElementById('inputContact')?.value||'';if(document.getElementById('finalName'))document.getElementById('finalName').value=n;if(document.getElementById('finalContact'))document.getElementById('finalContact').value=c;bookingDay='today';bookingDate='';try{sessionStorage.setItem('bookingDay','today');sessionStorage.removeItem('bookingDate')}catch(e){};renderSlots();goTo('booking-time');renderBookingTexts()}"
s = s.replace(old_start, new_start)

# Patch already-updated startBooking too.
s = s.replace(
    "bookingDay='today';bookingDate='';renderSlots();goTo('booking-time');renderBookingTexts()}",
    "bookingDay='today';bookingDate='';try{sessionStorage.setItem('bookingDay','today');sessionStorage.removeItem('bookingDate')}catch(e){};renderSlots();goTo('booking-time');renderBookingTexts()}",
    1,
)

# 4) Persist selected day/date robustly so Tomorrow/Other day survives all following screens.
old_select_day = "function selectDay(day,el){bookingDay=day;bookingDate='';document.querySelectorAll('.day-btn').forEach(x=>x.classList.remove('selected'));el.classList.add('selected');const w=document.getElementById('otherDateWrap');w.classList.toggle('show',day==='other');if(day!=='other')renderSlots()}"
new_select_day = "function selectDay(day,el){bookingDay=day;bookingDate='';try{sessionStorage.setItem('bookingDay',day);sessionStorage.removeItem('bookingDate')}catch(e){};document.querySelectorAll('.day-btn').forEach(x=>x.classList.remove('selected'));el.classList.add('selected');const w=document.getElementById('otherDateWrap');w.classList.toggle('show',day==='other');if(day!=='other')renderSlots()}"
s = s.replace(old_select_day, new_select_day)

old_other = "function selectOtherDate(v){bookingDate=v;renderSlots()}"
new_other = "function selectOtherDate(v){bookingDate=v;try{sessionStorage.setItem('bookingDay','other');sessionStorage.setItem('bookingDate',v)}catch(e){};renderSlots()}"
s = s.replace(old_other, new_other)

old_slot = "function selectSlot(t,b){if(bookingDay==='other'&&!bookingDate){document.getElementById('bookingDateInput').focus();return}bookingTime=t;bookingCustom='';document.querySelectorAll('.slot-btn').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');try{gtag('event','time_selected',{time:t,day:bookingDay})}catch(e){};setTimeout(()=>{goTo('booking-comment');updateBookingSummary();renderBookingTexts()},180)}"
new_slot = "function selectSlot(t,b){try{bookingDay=sessionStorage.getItem('bookingDay')||bookingDay;bookingDate=sessionStorage.getItem('bookingDate')||bookingDate}catch(e){};if(bookingDay==='other'&&!bookingDate){document.getElementById('bookingDateInput').focus();return}bookingTime=t;bookingCustom='';document.querySelectorAll('.slot-btn').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');try{gtag('event','time_selected',{time:t,day:bookingDay})}catch(e){};setTimeout(()=>{goTo('booking-comment');updateBookingSummary();renderBookingTexts()},180)}"
s = s.replace(old_slot, new_slot)

# 5) Custom-time summary gets different wording.
old_summary = "function updateBookingSummary(){const txt=bookingDateLabel();['bookingSelectedText','bookingFinalSelected'].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=(lang==='uk'?'Обраний час: ':'Выбранное время: ')+txt})}"
new_summary = "function updateBookingSummary(){const txt=bookingDateLabel();const prefix=bookingCustom?(lang==='uk'?'Запропонований вами час: ':'Предложенное вами время: '):(lang==='uk'?'Обраний час: ':'Выбранное время: ');['bookingSelectedText','bookingFinalSelected'].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=prefix+txt})}"
s = s.replace(old_summary, new_summary)

# 6) Desktop QA carries name/phone/day/date into the test tab.
old_openqa = """  function openQa(screen,label){\n    const u=new URL(location.href);u.searchParams.set('qaBooking',screen);if(label)u.searchParams.set('qaLabel',label);window.open(u.toString(),'_blank');\n  }"""
new_openqa = """  function openQa(screen,label){\n    const u=new URL(location.href);\n    u.searchParams.set('qaBooking',screen);\n    if(label)u.searchParams.set('qaLabel',label);\n    const n=document.getElementById('inputName')?.value||document.getElementById('finalName')?.value||'';\n    const c=document.getElementById('inputContact')?.value||document.getElementById('finalContact')?.value||'';\n    if(n)u.searchParams.set('qaName',n);else u.searchParams.delete('qaName');\n    if(c)u.searchParams.set('qaPhone',c);else u.searchParams.delete('qaPhone');\n    const savedDay=sessionStorage.getItem('bookingDay')||((typeof bookingDay!=='undefined')?bookingDay:'today');\n    const savedDate=sessionStorage.getItem('bookingDate')||((typeof bookingDate!=='undefined')?bookingDate:'');\n    u.searchParams.set('qaDay',savedDay);\n    if(savedDate)u.searchParams.set('qaDate',savedDate);else u.searchParams.delete('qaDate');\n    window.open(u.toString(),'_blank');\n  }"""
s = s.replace(old_openqa, new_openqa)

old_qaload = "if(qa){window.addEventListener('load',()=>{setTimeout(()=>{try{if(qa==='custom'){goTo('customtime')}else if(qa==='comment'){bookingCustom='ТЕСТ: '+(qs.get('qaLabel')||'выбранное время');bookingDate='';bookingTime='';goTo('booking-comment');updateBookingSummary();renderBookingTexts()}}catch(e){console.error(e)}},100)})}"
new_qaload = "if(qa){window.addEventListener('load',()=>{setTimeout(()=>{try{const qn=qs.get('qaName')||'';const qp=qs.get('qaPhone')||'';bookingDay=qs.get('qaDay')||'today';bookingDate=qs.get('qaDate')||'';try{sessionStorage.setItem('bookingDay',bookingDay);if(bookingDate)sessionStorage.setItem('bookingDate',bookingDate);else sessionStorage.removeItem('bookingDate')}catch(e){};if(document.getElementById('inputName'))document.getElementById('inputName').value=qn;if(document.getElementById('finalName'))document.getElementById('finalName').value=qn;if(document.getElementById('inputContact'))document.getElementById('inputContact').value=qp;if(document.getElementById('finalContact'))document.getElementById('finalContact').value=qp;if(qa==='custom'){goTo('customtime')}else if(qa==='comment'){bookingCustom='';bookingTime=qs.get('qaLabel')||'';goTo('booking-comment');updateBookingSummary();renderBookingTexts()}}catch(e){console.error(e)}},100)})}"
s = s.replace(old_qaload, new_qaload)

# 7) Viber fallback if direct personal chat doesn't open.
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
