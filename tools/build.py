import json,re,os
s=open('template.html').read()
def rep(a,b,cnt=1):
  global s
  assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
s=s.replace('<meta name="claude:viewport-fit-sides" content="cover">','')
s=re.sub(r'\s*<button data-v="admin" data-admin hidden>.*?</button>','',s)
rep('<button class="btn primary" id="addEventBtn" data-admin hidden>Add event</button>','')
rep('<h1>Requests</h1>','<h1>My requests</h1>')
rep('<p class="lede">Every request sent through the hub, newest first. Status changes to Sent with a tracking number once it ships.</p>','<p class="lede">Requests sent from this device, newest first. Marketing gets each one right away and ships it before the need-by date.</p>')
rep('<div class="toolbar"><select class="small" id="mgrFilter"><option value="">All account managers</option></select></div>','<select class="small" id="mgrFilter" hidden><option value="">All</option></select><div style="height:14px"></div>')
s=re.sub(r'\n  <section id="v-admin" hidden>.*?\n  </section>\n','\n',s,flags=re.S)
rep('<h3>Event details</h3>${editing?eventForm(e):','<h3>Event details</h3>${false?"":')
rep('${isOwner?`<button class="btn" data-editev="${esc(e.id)}">Edit event</button>`:""}','')
rep('["events","catalog","requests","admin"].forEach(x=>$("#v-"+x).hidden = x!==v);','["events","catalog","requests"].forEach(x=>$("#v-"+x).hidden = x!==v);')
rep('$("#addEventBtn").onclick=','window._unused=')
rep('$("#nmCat").innerHTML=','if($("#nmCat"))$("#nmCat").innerHTML=')
rep('$("#addMat").addEventListener(','$("#addMat")&&$("#addMat").addEventListener(')
a=s.index('  if(!db){ $("#formNote").textContent="The hub can\'t save requests'); b=s.index('\n',a); s=s[:a]+s[b+1:]
rep('  try{ await db.collection("orders").add(body); try{ localStorage.setItem("asd-mgr",body.manager); }catch(e){}',
'''  try{ const fd=new URLSearchParams({"form-name":"material-request","bot-field":"",event:body.event,event_date:body.eventDate,manager:body.manager,needed_by:body.neededBy,ship_to:body.shipTo,notes:body.notes,
      items:items.map(i=>`${i.qty} x ${i.name} (${i.sku})`).join("\\n")});
    const r=await fetch("/",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:fd.toString()});
    if(!r.ok) throw new Error("http "+r.status);
    orders=[{id:"o"+Date.now(),...body},...orders]; try{ localStorage.setItem("asd-orders",JSON.stringify(orders)); localStorage.setItem("asd-mgr",body.manager); }catch(e){}
    renderRequests(); renderEvents();''')
rep(': "The request was not saved. Check your connection and try again."; }',': "The request was not sent. Check your connection and try again."; }')
rep('err&&err.code==="invalid_argument" ? "Your access to this page is view-only, so the request was not saved. Ask Vira to give you edit access." ','false ? "" ')
a=s.index('(async()=>{\n  if(!window.claude)'); b=s.index('})();',a)+5
s=s[:a]+'''events=(window.EVENTS||[]); materials=(window.MATERIALS||[]);
try{ orders=JSON.parse(localStorage.getItem("asd-orders")||"[]")||[]; }catch(e){ orders=[]; }
renderEvents(); renderFilters(); renderGrid(); renderCart(); renderRequests();
{ const h=(location.hash||"").slice(1); if(["events","catalog","requests"].includes(h)) show(h); }'''+s[b:]
rep('badge("adm",orders.filter(o=>o.status!=="Sent").length);','')
rep('<td class="sku">${esc(o.tracking)||"—"}</td>','<td></td>')
rep('<th>Status</th><th>Tracking</th>','<th>Status</th><th></th>')
s=s.replace('<span class="pill ${o.status==="Sent"?"sent":"not"}">${esc(o.status)}</span>${o.sentDate?`<div class="note">${fmt(o.sentDate)}</div>`:""}','<span class="pill not">Sent to marketing</span>')
rep('db?"No events yet.":"Loading events…"','"No events yet."')
rep('db?"No materials yet.":"Loading the catalog…"','"No materials yet."')
gate='''
<form name="material-request" data-netlify="true" netlify-honeypot="bot-field" hidden>
  <input name="bot-field"><input name="event"><input name="event_date"><input name="manager"><input name="needed_by"><textarea name="ship_to"></textarea><textarea name="notes"></textarea><textarea name="items"></textarea>
</form>
<div id="gate" style="position:fixed;inset:0;z-index:50;background:var(--bg);display:grid;place-items:center;padding:24px">
  <form id="gateForm" style="width:min(360px,100%);display:grid;gap:12px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:28px">
    <div class="logo"><span class="mark"><i></i><i></i><i></i><i></i></span><div>ASD Marketing Hub<small>Events and marketing materials</small></div></div>
    <label>Access code<input id="gateCode" autocomplete="off"></label>
    <button class="btn primary" type="submit">Enter</button>
    <p class="note" id="gateNote" style="margin:0">Ask Vira Cherepakhina for the code.</p>
  </form>
</div>
<script>
(function(){ const CODE="ASD2026"; const ok=()=>{ document.getElementById("gate").remove(); };
  try{ if(localStorage.getItem("asd-access")===CODE) return ok(); }catch(e){}
  document.getElementById("gateForm").addEventListener("submit",e=>{ e.preventDefault();
    if(document.getElementById("gateCode").value.trim().toUpperCase()===CODE){ try{ localStorage.setItem("asd-access",CODE); }catch(e){} ok(); }
    else document.getElementById("gateNote").textContent="That code is not right. Check it with Vira."; });
})();
</script>'''
rep('<div class="toast" id="toast" hidden></div>','<div class="toast" id="toast" hidden></div>'+gate)
I={'/*I_EV*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
   '/*I_CAT*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>',
   '/*I_REQ*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h9l4 4v14H6zM9 11h7M9 15h7M9 7h4"/></svg>',
   '/*I_CART*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 4h2.5l2.2 11h10.6L20.5 8H7"/><circle cx="9.5" cy="19.5" r="1.5"/><circle cx="17" cy="19.5" r="1.5"/></svg>'}
for k,v in I.items(): s=s.replace(k,v)
s=s.replace('/*PHOTOS*/{}',json.dumps(json.load(open('photos.json'))))
assert '/*I_' not in s and 'claude.use' not in s and 'db.collection' not in s.split('/* boot */')[1]
h_end=s.index('</style>')+8
html='<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex">\n<style>[hidden]{display:none!important}body{margin:0}img{max-width:100%}</style>\n'+s[:h_end]+'\n<script src="data.js"></script>\n</head><body>\n'+s[h_end:]+'\n</body></html>\n'
os.makedirs('../site',exist_ok=True)
open('../site/index.html','w').write(html)
d=json.load(open('site-data.json'))
open('../site/data.js','w').write('// Updated '+d['updated']+'\nwindow.EVENTS = '+json.dumps(d['events'],ensure_ascii=False,indent=1)+';\nwindow.MATERIALS = '+json.dumps(d['materials'],ensure_ascii=False,indent=1)+';\n')
for i,js in enumerate(re.findall(r'<script>(.*?)</script>',html,re.S)): pass
print('built',len(html))
