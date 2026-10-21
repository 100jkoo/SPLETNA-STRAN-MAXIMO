/* MAXIMO TEKSTIL · shared menu behaviour */
/* SETTINGS: paste the sign-up address of your newsletter service here (Wix Email Marketing / Brevo / Mailchimp form action).
   While it is empty, a sign-up opens an email to sales so no subscriber is lost. */
var MX_NEWSLETTER_ENDPOINT='';
var MX_NEWSLETTER_EMAIL='maximo1@siol.net';
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
  /* arriving from another page of the site: keep the section's dropdown open until the mouse leaves it */
  (function(){
    if(!hoverable.matches||!desk.matches)return;
    var ref=document.referrer;if(!ref||ref.indexOf(location.origin)!==0)return;
    var cur=hd.querySelector('.mx-item.mx-has>.mx-trig[aria-current="true"]');if(!cur)return;
    var it=cur.parentNode;
    setOpen(it,true);openItem=it;hd.classList.add('is-open');
    function away(e){
      if(it.contains(e.target)||!openItem)return;
      if(hd.contains(e.target)&&e.target.closest('.mx-item.mx-has'))return;
      document.removeEventListener('mousemove',away);
      if(openItem===it)closeAll();
    }
    setTimeout(function(){document.addEventListener('mousemove',away)},400);
  })();
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'){
      if(openItem){var b=openItem.querySelector('.mx-trig');closeAll();b.focus()}
      if(drawerOn())toggleDrawer(false);
    }
  });
  document.addEventListener('click',function(e){if(openItem&&!hd.contains(e.target))closeAll()});
  hd.addEventListener('focusout',function(e){if(openItem&&e.relatedTarget&&!openItem.contains(e.relatedTarget))closeAll()});
  hd.querySelectorAll('.mx-panel a').forEach(function(a){a.addEventListener('click',function(){setTimeout(closeAll,0)})});

  /* language switcher */
  (function(){
    var lb=hd.querySelector('.mx-lang-b');if(!lb)return;
    function setL(on){lb.setAttribute('aria-expanded',on?'true':'false')}
    lb.addEventListener('click',function(e){e.stopPropagation();setL(lb.getAttribute('aria-expanded')!=='true')});
    document.addEventListener('click',function(e){if(!lb.parentNode.contains(e.target))setL(false)});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'){setL(false)}});
  })();
  /* mobile drawer */
  var burger=hd.querySelector('.mx-burger'),drawer=document.getElementById('mx-drawer');
  function drawerOn(){return drawer&&drawer.classList.contains('is-on')}
  function toggleDrawer(on){
    if(!drawer)return;
    drawer.classList.toggle('is-on',on);burger.setAttribute('aria-expanded',on?'true':'false');
    burger.setAttribute('aria-label',on?'Menü schließen':'Menü öffnen');
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
      if(!ok){f.classList.add('is-err');msg.textContent='Bitte geben Sie eine gültige E-Mail-Adresse ein.';f.email.focus();return}
      if(!f.consent.checked){f.classList.add('is-err');msg.textContent='Bitte setzen Sie das Häkchen, um dem Erhalt des Newsletters zuzustimmen.';return}
      function done(){f.classList.add('is-ok');msg.textContent='Vielen Dank. Sie erhalten unseren nächsten Newsletter.'}
      if(MX_NEWSLETTER_ENDPOINT){
        var d=new FormData();d.append('email',em);d.append('consent','yes');d.append('source',f.getAttribute('data-where')||'');
        fetch(MX_NEWSLETTER_ENDPOINT,{method:'POST',body:d,headers:{Accept:'application/json'}}).then(function(r){if(r.ok)done();else throw 0})
          .catch(function(){f.classList.add('is-err');msg.textContent='Etwas ist schiefgelaufen. Bitte schreiben Sie an '+MX_NEWSLETTER_EMAIL+'.'});
      }else{
        location.href='mailto:'+MX_NEWSLETTER_EMAIL+'?subject='+encodeURIComponent('Newsletter subscription')+'&body='+encodeURIComponent('Please add '+em+' to the Maximo Tekstil newsletter (once a month). I agree to receive it and can unsubscribe at any time.');
        done();
      }
    });
  });
})();
