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

s = s.replace(
    "bookingDay='today';bookingDate='';renderSlots();goTo('booking-time');renderBookingTexts()}",
    "bookingDay='today';bookingDate='';try{sessionStorage.setItem('bookingDay','today');sessionStorage.removeItem('bookingDate')}catch(e){};renderSlots();goTo('booking-time');renderBookingTexts()}",
    1,
)

# 4) Custom-time summary gets different wording.
old_summary = "function updateBookingSummary(){const txt=bookingDateLabel();['bookingSelectedText','bookingFinalSelected'].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=(lang==='uk'?'Обраний час: ':'Выбранное время: ')+txt})}"
new_summary = "function updateBookingSummary(){const txt=bookingDateLabel();const prefix=bookingCustom?(lang==='uk'?'Запропонований вами час: ':'Предложенное вами время: '):(lang==='uk'?'Обраний час: ':'Выбранное время: ');['bookingSelectedText','bookingFinalSelected'].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=prefix+txt})}"
s = s.replace(old_summary, new_summary)

# 5) HARD FIX: keep selected day/date independently of the existing inline booking functions.
# Capture phase runs before inline onclick handlers. This is intentionally separate from selectDay/selectSlot
# so later workflow rewrites cannot silently return Tomorrow/Other day to Today.
if 'id="booking-day-persistence-fix"' not in s:
    day_fix = r'''
<script id="booking-day-persistence-fix">
(function(){
  function setDayState(day){
    try{sessionStorage.setItem('bookingDay',day);if(day!=='other')sessionStorage.removeItem('bookingDate')}catch(e){}
    try{bookingDay=day;if(day!=='other')bookingDate=''}catch(e){}
  }
  document.addEventListener('click',function(e){
    const dayBtn=e.target.closest && e.target.closest('.day-btn');
    if(dayBtn){
      const ru=(dayBtn.getAttribute('data-bk-ru')||dayBtn.textContent||'').trim().toLowerCase();
      const uk=(dayBtn.getAttribute('data-bk-uk')||'').trim().toLowerCase();
      if(ru.includes('завтра')||uk.includes('завтра')) setDayState('tomorrow');
      else if(ru.includes('другой')||uk.includes('інший')) setDayState('other');
      else setDayState('today');
    }
    const slot=e.target.closest && e.target.closest('.slot-btn');
    if(slot){
      try{
        const savedDay=sessionStorage.getItem('bookingDay')||'today';
        const savedDate=sessionStorage.getItem('bookingDate')||'';
        bookingDay=savedDay;
        bookingDate=savedDate;
      }catch(err){}
    }
  },true);
  document.addEventListener('change',function(e){
    if(e.target && e.target.id==='bookingDateInput'){
      const v=e.target.value||'';
      try{sessionStorage.setItem('bookingDay','other');sessionStorage.setItem('bookingDate',v)}catch(err){}
      try{bookingDay='other';bookingDate=v}catch(err){}
    }
  },true);
})();
</script>
'''
    s = s.replace('</body>', day_fix + '\n</body>', 1)

# 6) Desktop QA carries name/phone/day/date into the test tab.
old_openqa = """  function openQa(screen,label){\n    const u=new URL(location.href);u.searchParams.set('qaBooking',screen);if(label)u.searchParams.set('qaLabel',label);window.open(u.toString(),'_blank');\n  }"""
new_openqa = """  function openQa(screen,label){\n    const u=new URL(location.href);\n    u.searchParams.set('qaBooking',screen);\n    if(label)u.searchParams.set('qaLabel',label);\n    const n=document.getElementById('inputName')?.value||document.getElementById('finalName')?.value||'';\n    const c=document.getElementById('inputContact')?.value||document.getElementById('finalContact')?.value||'';\n    if(n)u.searchParams.set('qaName',n);else u.searchParams.delete('qaName');\n    if(c)u.searchParams.set('qaPhone',c);else u.searchParams.delete('qaPhone');\n    const savedDay=sessionStorage.getItem('bookingDay')||((typeof bookingDay!=='undefined')?bookingDay:'today');\n    const savedDate=sessionStorage.getItem('bookingDate')||((typeof bookingDate!=='undefined')?bookingDate:'');\n    u.searchParams.set('qaDay',savedDay);\n    if(savedDate)u.searchParams.set('qaDate',savedDate);else u.searchParams.delete('qaDate');\n    window.open(u.toString(),'_blank');\n  }"""
s = s.replace(old_openqa, new_openqa)

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
