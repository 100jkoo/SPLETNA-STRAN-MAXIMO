/* MAXIMO TEKSTIL · shared menu behaviour */
/* SETTINGS: paste the sign-up address of your newsletter service here (Wix Email Marketing / Brevo / Mailchimp form action).
   While it is empty, a sign-up opens an email to sales so no subscriber is lost. */
var MX_NEWSLETTER_ENDPOINT='';
var MX_NEWSLETTER_EMAIL='narocila@maximo-tekstil.com';
/* SETTINGS · forms, WhatsApp, analytics
   MX_FORM_ENDPOINT: address of a form service that emails the form to you (for example Formspree or Web3Forms).
     With an address set, orders, sample requests and inquiries are sent straight from the website.
     While it is empty, the visitor picks Gmail, Outlook, their email app or WhatsApp, so no request is lost.
   MX_FORM_KEY: access key, only if the form service asks for one.
   MX_GA_ID: Google Analytics 4 ID (G-XXXXXXXXXX). While it is empty no analytics and no cookie notice are loaded. */
var MX_FORM_ENDPOINT='';
var MX_FORM_KEY='';
var MX_ORDERS_EMAIL='narocila@maximo-tekstil.com';
var MX_WHATSAPP='38640855805';
var MX_GA_ID='';
(function(){
  var hd=document.querySelector('.mx-hd');if(!hd)return;
  var items=[].slice.call(hd.querySelectorAll('.mx-item.mx-has'));
  var scrim=document.querySelector('.mx-scrim');
  var desk=window.matchMedia('(min-width:1180px)');
  var hoverable=window.matchMedia('(hover:hover) and (pointer:fine)');
  var openItem=null,tOpen=null,tClose=null;

  function setOpen(it,on){
    if(!it)return;
    var b=it.querySelector('.mx-trig');
    it.classList.toggle('is-open',on);b.setAttribute('aria-expanded',on?'true':'false');
  }
  function open(it){
    clearTimeout(tClose);
    if(openItem&&openItem!==it)setOpen(openItem,false);
    openItem=it;setOpen(it,true);hd.classList.add('is-open');if(scrim)scrim.classList.add('is-on');
  }
  function closeAll(){
    clearTimeout(tOpen);
    if(openItem)setOpen(openItem,false);openItem=null;hd.classList.remove('is-open');if(scrim)scrim.classList.remove('is-on');
  }
  items.forEach(function(it){
    var b=it.querySelector('.mx-trig'),p=it.querySelector('.mx-panel');
    b.addEventListener('click',function(e){
      e.preventDefault();
      if(openItem===it)closeAll();else open(it);
    });
    b.addEventListener('keydown',function(e){
      if(e.key==='ArrowDown'){e.preventDefault();open(it);var f=p.querySelector('a');if(f)f.focus()}
    });
    it.addEventListener('mouseenter',function(){
      if(!hoverable.matches||!desk.matches)return;
      clearTimeout(tClose);clearTimeout(tOpen);
      tOpen=setTimeout(function(){open(it)},openItem?0:90);
    });
    it.addEventListener('mouseleave',function(){
      if(!hoverable.matches||!desk.matches)return;
      var a=document.activeElement;if(a&&a.tagName==='INPUT'&&it.contains(a))return;
      clearTimeout(tOpen);tClose=setTimeout(closeAll,220);
    });
  });
  if(scrim)scrim.addEventListener('click',closeAll);
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'){
      if(openItem){var b=openItem.querySelector('.mx-trig');closeAll();b.focus()}
      if(drawerOn())toggleDrawer(false);
    }
  });
  document.addEventListener('click',function(e){if(openItem&&!hd.contains(e.target))closeAll()});
  hd.addEventListener('focusout',function(e){if(openItem&&e.relatedTarget&&!openItem.contains(e.relatedTarget))closeAll()});
  hd.querySelectorAll('.mx-panel a').forEach(function(a){a.addEventListener('click',function(){setTimeout(closeAll,0)})});

  /* mobile drawer */
  var burger=hd.querySelector('.mx-burger'),drawer=document.getElementById('mx-drawer');
  function drawerOn(){return drawer&&drawer.classList.contains('is-on')}
  function toggleDrawer(on){
    if(!drawer)return;
    drawer.classList.toggle('is-on',on);burger.setAttribute('aria-expanded',on?'true':'false');
    burger.setAttribute('aria-label',on?'Close menu':'Open menu');
    document.documentElement.classList.toggle('mx-lock',on);
    if(on)drawer.removeAttribute('inert');else drawer.setAttribute('inert','');
  }
  if(burger)burger.addEventListener('click',function(){toggleDrawer(!drawerOn())});
  if(drawer){
    drawer.setAttribute('inert','');
    drawer.querySelectorAll('.mx-acc>button').forEach(function(b){
      b.addEventListener('click',function(){b.setAttribute('aria-expanded',b.getAttribute('aria-expanded')==='true'?'false':'true')});
    });
    drawer.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){toggleDrawer(false)})});
  }
  var mq=function(){if(desk.matches)toggleDrawer(false);else closeAll()};
  if(desk.addEventListener)desk.addEventListener('change',mq);else desk.addListener(mq);

  /* pages that render their content with JavaScript: retry the #anchor jump once content exists */
  function jump(){
    var h=location.hash.slice(1);if(!h||h.indexOf('=')>-1)return;
    var n=0;(function tryIt(){
      var el=document.getElementById(decodeURIComponent(h));
      if(el){el.scrollIntoView({block:'start'});return}
      if(++n<20)setTimeout(tryIt,100);
    })();
  }
  window.addEventListener('load',function(){setTimeout(jump,60)});
  window.addEventListener('hashchange',jump);

  /* newsletter sign-up forms */
  [].slice.call(document.querySelectorAll('form.mx-nl')).forEach(function(f){
    var msg=f.querySelector('.mx-nl-msg');
    f.addEventListener('submit',function(e){
      e.preventDefault();
      var em=f.email.value.trim(),ok=/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em);
      f.classList.remove('is-err');
      if(!ok){f.classList.add('is-err');msg.textContent='Please enter a valid email address.';f.email.focus();return}
      if(!f.consent.checked){f.classList.add('is-err');msg.textContent='Please tick the box to agree to receive the newsletter.';return}
      function done(){f.classList.add('is-ok');msg.textContent='Thank you. You will receive our next newsletter.'}
      var ep=MX_NEWSLETTER_ENDPOINT||MX_FORM_ENDPOINT;
      if(ep){
        var d=new FormData();if(!MX_NEWSLETTER_ENDPOINT&&MX_FORM_KEY)d.append('access_key',MX_FORM_KEY);
        d.append('email',em);d.append('consent','yes');d.append('subject','Newsletter subscription');d.append('_subject','Newsletter subscription');d.append('source',f.getAttribute('data-where')||'');
        fetch(ep,{method:'POST',body:d,headers:{Accept:'application/json'}}).then(function(r){if(r.ok)done();else throw 0})
          .catch(function(){f.classList.add('is-err');msg.textContent='Something went wrong. Please write to '+MX_NEWSLETTER_EMAIL+'.'});
      }else if(window.MX&&MX.send){
        MX.send({subject:'Newsletter subscription',title:'Confirm your subscription',email:em,kind:'newsletter',onDone:done,
          body:'Please add '+em+' to the Maximo Tekstil newsletter (once a month). I agree to receive it and can unsubscribe at any time.'});
      }else{
        location.href='mailto:'+MX_NEWSLETTER_EMAIL+'?subject='+encodeURIComponent('Newsletter subscription')+'&body='+encodeURIComponent('Please add '+em+' to the Maximo Tekstil newsletter (once a month). I agree to receive it and can unsubscribe at any time.');
        done();
      }
    });
  });
})();

/* promotion banner: hide after its end date, keep the mobile menu below the header while the banner is visible */
(function(){
  var now=Date.now();
  [].slice.call(document.querySelectorAll('.mx-promo,.mx-promo-note')).forEach(function(el){var u=Date.parse(el.getAttribute('data-until'));if(u&&now>u)el.hidden=true});
  var bar=document.querySelector('.mx-promo');if(!bar||bar.hidden)return;
  var root=document.documentElement,raf=0;
  function upd(){raf=0;var b=bar.getBoundingClientRect().bottom;root.style.setProperty('--mx-off',Math.max(0,Math.round(b))+'px')}
  window.addEventListener('scroll',function(){if(!raf)raf=requestAnimationFrame(upd)},{passive:true});
  window.addEventListener('resize',upd);upd();
})();
/* when the offer is over, the Offers menu entry disappears */
(function(){var f=document.querySelector('.mx-feat--offer');if(!f)return;var u=Date.parse(f.getAttribute('data-until'));if(!u||Date.now()<=u)return;
  var li=f.closest('.mx-item');if(li)li.style.display='none';
  [].slice.call(document.querySelectorAll('.mx-drawer .mx-acc')).forEach(function(a){if(a.querySelector('.mx-hot'))a.style.display='none'});})();

/* promo ticker pause button */
(function(){var p=document.querySelector('.mx-promo');if(!p)return;var b=p.querySelector('.mx-pr-pp');if(!b)return;
  b.addEventListener('click',function(){var on=p.classList.toggle('is-paused');b.setAttribute('aria-pressed',on?'true':'false');b.setAttribute('aria-label',on?'Nadaljuj premikanje':'Ustavi premikanje')})})();

/* logo: woven intro on the first visit of the session (home page), replay when the logo is clicked on the home page */
(function(){var a=document.querySelector('.mx-logo');if(!a)return;
  if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  function play(){a.classList.remove('is-anim');void a.offsetWidth;a.classList.add('is-anim');clearTimeout(a._t);a._t=setTimeout(function(){a.classList.remove('is-anim')},1600)}
  var home=document.body.getAttribute('data-mx-section')==='home'||/(^|\/)(index\.html)?$/.test(location.pathname)&&!/\/(blog|on-stock)\//.test(location.pathname);
  var seen=false;try{seen=sessionStorage.getItem('mx-logo-intro')==='1';sessionStorage.setItem('mx-logo-intro','1')}catch(e){}
  if(!seen)play();
  a.addEventListener('click',function(e){if(home){e.preventDefault();play();window.scrollTo({top:0,behavior:'smooth'})}});
})();

/* ============================================================
   MAXIMO TEKSTIL · sending requests, WhatsApp, small animations, analytics
   The SETTINGS for this block are at the top of this file.
   ============================================================ */
(function(){
  var MAIL=MX_ORDERS_EMAIL;
  var T={
    en:{title:'Send your request',msg:'Your message',email:'Your email',send:'Send',sending:'Sending…',
        how:'Choose how to send it',or:'Or send it another way',gmail:'Gmail',outlook:'Outlook',app:'Email app',wa:'WhatsApp',copy:'Copy text',copied:'Copied',
        to:'Goes to',reply:'We usually reply the same or next working day.',
        almost:'Almost done',almostP:'Press Send in the window that opened. Your message then reaches us at',almostWa:'Press Send in WhatsApp. Your message then reaches our sales team.',
        other:'It did not open? Choose another way',thanks:'Thank you.',thanksP:'We have your message and usually reply the same or next working day.',
        close:'Close',fail:'We could not send it from the website. Please choose another way below.',bademail:'Enter a valid email address.',
        hello:'Hello,\n\nwe are interested in:\n\nFabric and colour: \nQuantity: \n\nCompany: \n\nBest regards,\n',
        waAria:'Message us on WhatsApp',waAsk:'Hello, I have a question about your fabrics.',waItem:'Hello, I am interested in ',
        ck:'We would like to use analytics cookies to see which fabrics visitors look at. Nothing is loaded until you agree.',ckYes:'Agree',ckNo:'No thanks',ckMore:'Privacy policy'},
    sl:{title:'Pošljite povpraševanje',msg:'Vaše sporočilo',email:'Vaš e-naslov',send:'Pošlji',sending:'Pošiljam…',
        how:'Izberite, kako ga pošljete',or:'Ali pošljite drugače',gmail:'Gmail',outlook:'Outlook',app:'E-pošta',wa:'WhatsApp',copy:'Kopiraj',copied:'Kopirano',
        to:'Prejme',reply:'Običajno odgovorimo isti ali naslednji delovni dan.',
        almost:'Še en korak',almostP:'V oknu, ki se je odprlo, pritisnite Pošlji. Sporočilo prejmemo na',almostWa:'V WhatsAppu pritisnite Pošlji. Sporočilo prejme naša prodaja.',
        other:'Se ni odprlo? Izberite drug način',thanks:'Hvala.',thanksP:'Sporočilo smo prejeli. Običajno odgovorimo isti ali naslednji delovni dan.',
        close:'Zapri',fail:'Pošiljanje s strani ni uspelo. Izberite drug način spodaj.',bademail:'Vnesite veljaven e-naslov.',
        hello:'Pozdravljeni,\n\nzanima nas:\n\nTkanina in barva: \nKoličina: \n\nPodjetje: \n\nLep pozdrav,\n',
        waAria:'Pišite nam na WhatsApp',waAsk:'Pozdravljeni, imam vprašanje o vaših tkaninah.',waItem:'Pozdravljeni, zanima me ',
        ck:'Radi bi uporabili analitične piškotke, da vidimo, katere tkanine obiskovalci gledajo. Brez vaše privolitve se nič ne naloži.',ckYes:'Strinjam se',ckNo:'Ne, hvala',ckMore:'Zasebnost'}
  };
  function lang(el){var n=el&&el.closest?el.closest('[lang]'):null;return n&&n.lang==='sl'?'sl':'en'}
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  var enc=encodeURIComponent;
  var IC={
    mail:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/></svg>',
    wa:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3a9 9 0 0 0-7.7 13.6L3 21l4.5-1.2A9 9 0 1 0 12 3Z"/><g transform="translate(7.3 7.1) scale(.4)" stroke-width="4.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></g></svg>',
    copy:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V6.5A2.5 2.5 0 0 0 13.5 4h-7A2.5 2.5 0 0 0 4 6.5v7A2.5 2.5 0 0 0 6.5 16H8"/></svg>',
    ok:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>'
  };

  var MX=window.MX=window.MX||{};
  MX.track=function(name,params){try{if(window.gtag)window.gtag('event',name,params||{})}catch(e){}};
  MX.waLink=function(text){return 'https://wa.me/'+MX_WHATSAPP+(text?'?text='+enc(text):'')};

  /* ---------- the send sheet ---------- */
  var dlg=null,E={},cur=null,t=T.en,state='',via='';
  function h(tag,cls,html){var n=document.createElement(tag);if(cls)n.className=cls;if(html!=null)n.innerHTML=html;return n}
  function build(){
    if(dlg)return;
    dlg=h('dialog','mx-send');dlg.setAttribute('aria-labelledby','mxSendT');
    dlg.innerHTML=
      '<div class="mx-send-in">'+
        '<div class="mx-send-h"><div><p class="mx-send-e"></p><h2 id="mxSendT"></h2></div><button type="button" class="mx-send-x" aria-label="Close">&times;</button></div>'+
        '<div class="mx-send-b">'+
          '<label class="mx-send-l"><span data-k="msg"></span><textarea rows="9" spellcheck="false"></textarea></label>'+
          '<p class="mx-send-note" hidden></p>'+
          '<label class="mx-send-l mx-send-em"><span data-k="email"></span><input type="email" autocomplete="email" inputmode="email"></label>'+
          '<button type="button" class="mx-send-main"></button>'+
          '<p class="mx-send-err" role="alert"></p>'+
          '<p class="mx-send-how"></p>'+
          '<div class="mx-send-ch">'+
            '<a class="mx-ch" data-ch="gmail" target="_blank" rel="noopener" href="#">'+IC.mail+'<span></span></a>'+
            '<a class="mx-ch" data-ch="outlook" target="_blank" rel="noopener" href="#">'+IC.mail+'<span></span></a>'+
            '<a class="mx-ch" data-ch="app" href="#">'+IC.mail+'<span></span></a>'+
            '<a class="mx-ch mx-ch-wa" data-ch="wa" target="_blank" rel="noopener" href="#">'+IC.wa+'<span></span></a>'+
            '<button type="button" class="mx-ch" data-ch="copy">'+IC.copy+'<span></span></button>'+
          '</div>'+
          '<p class="mx-send-f"></p>'+
        '</div>'+
        '<div class="mx-send-done" hidden><div class="mx-send-ok">'+IC.ok+'</div><h3></h3><p></p><div class="mx-send-da"><button type="button" class="mx-send-close"></button><button type="button" class="mx-send-back"></button></div></div>'+
      '</div>';
    document.body.appendChild(dlg);
    var q=function(s){return dlg.querySelector(s)};
    E={e:q('.mx-send-e'),title:q('h2'),x:q('.mx-send-x'),b:q('.mx-send-b'),msg:q('textarea'),note:q('.mx-send-note'),emRow:q('.mx-send-em'),em:q('input[type=email]'),
       main:q('.mx-send-main'),err:q('.mx-send-err'),how:q('.mx-send-how'),ch:q('.mx-send-ch'),f:q('.mx-send-f'),
       done:q('.mx-send-done'),dh:q('.mx-send-done h3'),dp:q('.mx-send-done p'),close:q('.mx-send-close'),back:q('.mx-send-back')};
    function subj(){return cur.subject||'Inquiry'}
    function body(){return E.msg.value.replace(/\r/g,'')}
    function picked(m){via=m;MX.track('mx_send',{method:m,form:cur.kind||''});setTimeout(function(){show('almost')},350)}
    E.ch.addEventListener('click',function(ev){
      var b=ev.target.closest('.mx-ch');if(!b)return;var c=b.getAttribute('data-ch');
      if(c==='gmail'){b.href='https://mail.google.com/mail/?view=cm&fs=1&to='+enc(MAIL)+'&su='+enc(subj())+'&body='+enc(body());picked(c)}
      else if(c==='outlook'){b.href='https://outlook.office.com/mail/deeplink/compose?to='+enc(MAIL)+'&subject='+enc(subj())+'&body='+enc(body());picked(c)}
      else if(c==='app'){b.href='mailto:'+MAIL+'?subject='+enc(subj())+'&body='+enc(body().replace(/\n/g,'\r\n'));picked(c)}
      else if(c==='wa'){b.href=MX.waLink(subj()+'\n\n'+body());picked(c)}
      else if(c==='copy'){
        var txt=MAIL+'\n'+subj()+'\n\n'+body(),lab=b.querySelector('span'),old=t.copy;
        var ok=function(){lab.textContent=t.copied;setTimeout(function(){lab.textContent=old},1600)};
        var fb=function(){E.msg.focus();E.msg.select();try{document.execCommand('copy');ok()}catch(e){}};
        if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(txt).then(ok,fb);else fb();
        MX.track('mx_send',{method:'copy',form:cur.kind||''});
      }
    });
    E.main.addEventListener('click',function(){
      var em=(E.em.value||cur.email||'').trim();
      if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)){E.err.textContent=t.bademail;E.emRow.hidden=false;E.em.focus();return}
      var d=new FormData();if(MX_FORM_KEY)d.append('access_key',MX_FORM_KEY);
      d.append('subject',subj());d.append('_subject',subj());d.append('email',em);d.append('_replyto',em);d.append('replyto',em);
      if(cur.company)d.append('company',cur.company);d.append('message',body());d.append('form',cur.kind||'');d.append('page',location.href);
      (cur.files||[]).forEach(function(f){d.append('attachment',f,f.name)});
      E.err.textContent='';E.main.disabled=true;E.main.textContent=t.sending;
      fetch(MX_FORM_ENDPOINT,{method:'POST',body:d,headers:{Accept:'application/json'}})
        .then(function(r){if(!r.ok)throw 0;MX.track('mx_send',{method:'form',form:cur.kind||''});show('sent')})
        .catch(function(){E.err.textContent=t.fail;dlg.classList.remove('has-ep');E.how.textContent=t.how})
        .then(function(){E.main.disabled=false;E.main.textContent=t.send});
    });
    function finish(){var c=cur,s=state;state='';if(dlg.open){if(dlg.close)dlg.close();else dlg.removeAttribute('open')}if(c&&c.onDone&&(s==='sent'||s==='almost'))c.onDone(s)}
    E.x.addEventListener('click',finish);E.close.addEventListener('click',finish);
    E.back.addEventListener('click',function(){show('')});
    dlg.addEventListener('click',function(ev){if(ev.target===dlg)finish()});
    dlg.addEventListener('cancel',function(ev){ev.preventDefault();finish()});
    MX._show=show;
  }
  function show(s){
    state=s;E.b.hidden=!!s;E.done.hidden=!s;
    if(s==='sent'){E.dh.textContent=t.thanks;E.dp.textContent=t.thanksP;E.back.hidden=true}
    if(s==='almost'){E.dh.textContent=t.almost;E.dp.textContent=via==='wa'?t.almostWa:t.almostP+' '+MAIL+'.';E.back.hidden=false}
    if(s)E.close.focus();
  }
  MX.send=function(o){
    cur=o=o||{};t=T[o.lang==='sl'?'sl':'en'];build();
    var ep=!!MX_FORM_ENDPOINT;
    dlg.classList.toggle('has-ep',ep);
    E.e.textContent=t.to+' '+MAIL;E.title.textContent=o.title||t.title;
    E.msg.value=(o.body||t.hello).replace(/\r/g,'');
    dlg.querySelector('[data-k=msg]').textContent=t.msg;dlg.querySelector('[data-k=email]').textContent=t.email;
    E.em.value=o.email||'';E.emRow.hidden=!ep||!!o.email;
    E.note.textContent=o.note||'';E.note.hidden=!o.note;
    E.main.textContent=t.send;E.err.textContent='';E.how.textContent=ep?t.or:t.how;E.f.textContent=t.reply;
    E.close.textContent=t.close;E.back.textContent=t.other;E.x.setAttribute('aria-label',t.close);
    ['gmail','outlook','app','wa','copy'].forEach(function(k){dlg.querySelector('[data-ch='+k+'] span').textContent=t[k]});
    /* phones: the email app and WhatsApp work best, show them first */
    dlg.classList.toggle('is-touch',!!(window.matchMedia&&matchMedia('(pointer:coarse)').matches));
    show('');
    if(!dlg.open){if(dlg.showModal)dlg.showModal();else dlg.setAttribute('open','')}
    setTimeout(function(){try{(ep&&!o.email?E.em:E.msg).focus({preventScroll:true});E.msg.setSelectionRange(0,0);E.msg.scrollTop=0}catch(e){}},40);
  };

  /* prepared email links (subject or text already filled in) open the send sheet instead of a possibly missing email program */
  document.addEventListener('click',function(e){
    if(e.defaultPrevented||e.button||e.metaKey||e.ctrlKey||e.shiftKey)return;
    var a=e.target.closest?e.target.closest('a[href^="mailto:"]'):null;if(!a||a.closest('.mx-send'))return;
    var hr=a.getAttribute('href'),q=hr.indexOf('?');if(q<0)return;
    var p;try{p=new URLSearchParams(hr.slice(q+1).replace(/\+/g,'%2B'))}catch(x){return}
    var s=p.get('subject'),b=p.get('body');if(!s&&!b)return;
    e.preventDefault();
    MX.send({subject:s||'',body:b||'',lang:lang(a),kind:'link'});
  });

  /* ---------- WhatsApp button on every page ---------- */
  (function(){
    if(!MX_WHATSAPP||document.querySelector('.mx-wa'))return;
    var sl=!!document.querySelector('main [lang="sl"]'),tt=sl?T.sl:T.en;
    var a=h('a','mx-wa',IC.wa+'<span>WhatsApp</span>');
    a.target='_blank';a.rel='noopener';a.href=MX.waLink();a.setAttribute('aria-label',tt.waAria);
    a.addEventListener('click',function(){
      var txt=window.MXwa;
      if(!txt){var h1=document.querySelector('main h1'),item=/\/(made-to-order|on-stock\/fabrics)\//.test(location.pathname)&&h1;
        txt=item?tt.waItem+h1.textContent.replace(/\s+/g,' ').trim()+'.':tt.waAsk}
      a.href=MX.waLink(txt);MX.track('mx_whatsapp',{page:location.pathname});
    });
    if(document.querySelector('.mbar'))a.classList.add('has-mbar');
    document.body.appendChild(a);
  })();

  /* ---------- promo ticker: days left ---------- */
  (function(){
    var bar=document.querySelector('.mx-promo');if(!bar||bar.hidden)return;
    var u=Date.parse(bar.getAttribute('data-until'));if(!u)return;
    var left=u-Date.now();if(left<=0)return;var d=Math.floor(left/864e5);
    var txt=d<1?'samo še <b>danes</b>':d===1?'še <b>1&nbsp;dan</b>':'še <b>'+d+'&nbsp;'+(d===2?'dneva':'dni')+'</b>';
    [].slice.call(bar.querySelectorAll('.mx-pr-set')).forEach(function(set){
      var s=document.createElement('span');s.className='mx-pr-left';s.innerHTML=txt;
      var i=document.createElement('i');i.className='mx-pr-sep';i.setAttribute('aria-hidden','true');
      set.appendChild(s);set.appendChild(i);
    });
  })();

  /* ---------- numbers count up when they come into view ---------- */
  (function(){
    var els=[].slice.call(document.querySelectorAll('[data-mx-count]'));
    if(!els.length||reduce||!('IntersectionObserver' in window))return;
    function run(el){
      var to=parseFloat(el.getAttribute('data-mx-count')),from=parseFloat(el.getAttribute('data-mx-from')||'0'),t0=null,dur=1100;
      function step(ts){if(!t0)t0=ts;var p=Math.min(1,(ts-t0)/dur),e=1-Math.pow(1-p,3);el.textContent=String(Math.round(from+(to-from)*e));if(p<1)requestAnimationFrame(step)}
      requestAnimationFrame(step);
    }
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){io.unobserve(e.target);run(e.target)}})},{threshold:.6});
    els.forEach(function(el){el.style.fontVariantNumeric='tabular-nums';io.observe(el)});
  })();

  /* ---------- colour strips ripple like a fan of swatches (index for the delay) ---------- */
  [].slice.call(document.querySelectorAll('.bstrip,.scard .strip,.mx-fan')).forEach(function(s){
    [].slice.call(s.children).forEach(function(c,i){c.style.setProperty('--i',i)});
  });

  /* ---------- home: the colour wall shows one colour after another until the visitor takes over ---------- */
  (function(){
    var wall=document.getElementById('wall'),nm=document.getElementById('tipName'),cd=document.getElementById('tipCode'),dot=document.getElementById('tipDot'),tip=document.getElementById('wallTip');
    if(!wall||!nm||reduce)return;
    var tiles=[].slice.call(wall.querySelectorAll('a')),d0=[nm.textContent,cd.textContent],lit=null,timer=null,busy=false,seen=false,n=0;
    function clear(){if(lit){lit.classList.remove('is-lit');lit=null}}
    function next(){
      if(busy||!seen||document.hidden)return;
      clear();
      if(++n%6===0){dot.style.removeProperty('--c');nm.textContent=d0[0];cd.textContent=d0[1];tip.classList.remove('is-item');return}
      var a=tiles[Math.floor(Math.random()*tiles.length)];lit=a;a.classList.add('is-lit');
      dot.style.setProperty('--c',a.style.getPropertyValue('--c'));nm.textContent=a.dataset.n;cd.textContent=a.dataset.f;tip.classList.add('is-item');
    }
    function start(){if(!timer)timer=setInterval(next,2200)}
    wall.addEventListener('mouseenter',function(){busy=true;clear()});
    wall.addEventListener('mouseleave',function(){busy=false});
    wall.addEventListener('focusin',function(){busy=true;clear()});
    wall.addEventListener('focusout',function(){busy=false});
    if('IntersectionObserver' in window){new IntersectionObserver(function(es){seen=es[0].isIntersecting},{threshold:.35}).observe(wall)}else seen=true;
    setTimeout(start,2600);
  })();

  /* ---------- analytics, only when an ID is set and only after the visitor agrees ---------- */
  (function(){
    if(!MX_GA_ID)return;
    var K='mx-analytics',v=null;try{v=localStorage.getItem(K)}catch(e){}
    function load(){
      var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+enc(MX_GA_ID);document.head.appendChild(s);
      window.dataLayer=window.dataLayer||[];window.gtag=function(){window.dataLayer.push(arguments)};window.gtag('js',new Date());window.gtag('config',MX_GA_ID,{anonymize_ip:true});
    }
    if(v==='yes'){load();return}
    if(v==='no')return;
    var sl=!!document.querySelector('main [lang="sl"]'),tt=sl?T.sl:T.en,sc=document.querySelector('script[src*="site.js"]'),base=sc?sc.getAttribute('src').replace(/assets\/site\.js.*$/,''):'';
    var bar=h('div','mx-ck','<p>'+tt.ck+' <a href="'+base+'privacy.html">'+tt.ckMore+'</a></p><div><button type="button" data-v="no">'+tt.ckNo+'</button><button type="button" data-v="yes">'+tt.ckYes+'</button></div>');
    bar.setAttribute('role','region');bar.setAttribute('aria-label','Cookies');
    bar.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var c=b.getAttribute('data-v');try{localStorage.setItem(K,c)}catch(x){}bar.remove();if(c==='yes')load()});
    document.body.appendChild(bar);
  })();
})();
