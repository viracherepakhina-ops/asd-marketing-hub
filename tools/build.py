"""Builds ../site/index.html from template.html (shared with the claude.ai version)."""
import json, re, os
HERE=os.path.dirname(os.path.abspath(__file__))
s=open(os.path.join(HERE,'template.html')).read()
def rep(a,b,cnt=1):
  global s
  assert s.count(a)==cnt,(s.count(a),a[:90]); s=s.replace(a,b)
s=s.replace('<meta name="claude:viewport-fit-sides" content="cover">','')
# manager: free text with suggestions
rep('<label>Account manager<select id="fMgr" required></select></label>','<label>Account manager<input id="fMgr" required list="mgrList" placeholder="Type or pick your name" autocomplete="name"></label>')
rep('$("#fMgr").innerHTML = `<option value="">Choose your name</option>` + MANAGERS.map(m=>`<option>${esc(m)}</option>`).join("");','')
rep('const MANAGERS = ["Thomas Egbers","Morgan Pixley","Mary Benton","Arthur \\"Buzz\\" Carruth","Steve Merrick","David Sarver","Valerii Mashkovtsev","Nonna Airapetova","Chris Morton","Gary","Edward","Val","Other"];',
    'const MANAGERS = ["Thomas Egbers","Morgan Pixley","Mary Benton","Arthur \\"Buzz\\" Carruth","Steve Merrick","David Sarver","Valerii Mashkovtsev","Nonna Airapetova","Chris Morton","Gary","Edward","Val"];')
rep('$("#mgrFilter").onchange=renderRequests;','$("#mgrFilter").onchange=renderRequests;\nfunction mgrOptions(){ const names=[...new Set([...MANAGERS,...orders.map(o=>o.manager).filter(Boolean)])].sort(); const cur=$("#mgrFilter").value; $("#mgrFilter").innerHTML=`<option value="">All account managers</option>`+names.map(m=>`<option>${esc(m)}</option>`).join(""); $("#mgrFilter").value=cur; }')
rep('$("#mgrFilter").innerHTML += MANAGERS.map(m=>`<option>${esc(m)}</option>`).join("");','')
rep('function renderRequests(){\n','function renderRequests(){\n  mgrOptions();\n')
# admin: delete order + logout
rep('''      :`<div style="display:flex;gap:6px;flex-wrap:wrap"><input id="tr-${esc(o.id)}" placeholder="Tracking #" style="max-width:170px"><button class="btn primary" data-send="${esc(o.id)}">Mark Sent</button></div>`}</td></tr>`; }).join("")''',
'''      :`<div style="display:flex;gap:6px;flex-wrap:wrap"><input id="tr-${esc(o.id)}" placeholder="Tracking #" style="max-width:170px"><button class="btn primary" data-send="${esc(o.id)}">Mark Sent</button></div>`}
      <button class="btn danger" data-delorder="${esc(o.id)}" style="margin-top:6px">Delete</button></td></tr>`; }).join("")''')
rep('''  $("#ordersBody").querySelectorAll("[data-unsend]").forEach(b=>b.onclick=()=>setSent(b.dataset.unsend,false));''',
'''  $("#ordersBody").querySelectorAll("[data-unsend]").forEach(b=>b.onclick=()=>setSent(b.dataset.unsend,false));
  $("#ordersBody").querySelectorAll("[data-delorder]").forEach(b=>b.onclick=async()=>{ if(b.dataset.sure!=="1"){ b.dataset.sure="1"; b.textContent="Click again to delete"; return; }
    try{ b.blur(); await db.doc("orders/"+b.dataset.delorder).delete(); toast("Request deleted"); }catch(e){ toast("Could not delete. Try again."); } });''')
rep('<p class="eyebrow">Only you see this</p>\n    <h1>Admin</h1>','<p class="eyebrow">Only you see this</p>\n    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h1>Admin</h1><button class="btn" id="logoutBtn">Sign out of admin</button></div>')
# order submit: also send Netlify Form for email notifications
rep('  try{ await db.collection("orders").add(body); try{ localStorage.setItem("asd-mgr",body.manager); }catch(e){}',
'''  try{ await db.collection("orders").add(body); try{ localStorage.setItem("asd-mgr",body.manager); }catch(e){}
    try{ fetch("/",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams({"form-name":"material-request","bot-field":"",event:body.event,event_date:body.eventDate,manager:body.manager,needed_by:body.neededBy,ship_to:body.shipTo,notes:body.notes,items:items.map(i=>`${i.qty} x ${i.name} (${i.sku})`).join("\\n")}).toString()}); }catch(e){}''')
rep('err&&err.code==="invalid_argument" ? "Your access to this page is view-only, so the request was not saved. Ask Vira to give you edit access." ','false ? "" ')
# boot
a=s.index('(async()=>{\n  if(!window.claude)'); b=s.index('})();',a)+5
s=s[:a]+'''(async()=>{
  db=window.HubDB; assets=null;
  isOwner=await HubDB.checkAdmin();
  document.querySelectorAll("[data-admin]").forEach(b=>b.hidden=!isOwner);
  const h=(location.hash||"").slice(1);
  if(h==="admin" && !isOwner) $("#adminLogin").hidden=false;
  if(["events","catalog","requests","admin"].includes(h)) show(h);
  db.collection("events").onSnapshot(s=>{ events=s.docs.map(x=>({id:x.id,...x.data()})); if(!editEv) renderEvents(); renderBanner(); });
  db.collection("materials").orderBy("sort").onSnapshot(s=>{ materials=s.docs.map(x=>({id:x.id,...x.data()})); renderFilters(); renderGrid(); renderCart(); renderAdmin(); });
  db.collection("orders").orderBy("createdAt","desc").onSnapshot(s=>{ orders=s.docs.map(x=>({id:x.id,...x.data()})); renderRequests(); renderAdmin(); if(!editEv) renderEvents(); });
})();
addEventListener("hashchange",()=>{ const h=(location.hash||"").slice(1); if(h==="admin"&&!isOwner) $("#adminLogin").hidden=false; else if(["events","catalog","requests","admin"].includes(h)) show(h); });
$("#logoutBtn").onclick=()=>{ HubDB.setAdminKey(""); location.hash="#events"; location.reload(); };
$("#adminLoginForm").addEventListener("submit",async e=>{ e.preventDefault(); HubDB.setAdminKey($("#adminKey").value.trim());
  if(await HubDB.checkAdmin()){ location.hash="#admin"; location.reload(); } else { HubDB.setAdminKey(""); $("#adminNote").textContent="Wrong admin password."; } });
$("#adminCancel").onclick=()=>{ $("#adminLogin").hidden=true; show("events"); };'''+s[b:]
rep('async function setSent(id,sent){ const o=orders.find(x=>x.id===id); if(!o) return;','async function setSent(id,sent){ const o=orders.find(x=>x.id===id); if(!o) return; const tv=sent?($("#tr-"+CSS.escape(id)).value||"").trim():""; document.activeElement&&document.activeElement.blur();')
rep('const tracking=sent?($("#tr-"+CSS.escape(id)).value||"").trim():"";','const tracking=tv;')
extra='''
<form name="material-request" data-netlify="true" netlify-honeypot="bot-field" hidden>
  <input name="bot-field"><input name="event"><input name="event_date"><input name="manager"><input name="needed_by"><textarea name="ship_to"></textarea><textarea name="notes"></textarea><textarea name="items"></textarea>
</form>
<div id="adminLogin" hidden style="position:fixed;inset:0;z-index:45;background:rgba(16,18,22,.25);display:grid;place-items:center;padding:24px">
  <form id="adminLoginForm" style="width:min(360px,100%);display:grid;gap:12px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:24px">
    <h2>Admin sign in</h2>
    <label>Admin password<input id="adminKey" type="password" autocomplete="current-password"></label>
    <div style="display:flex;gap:8px"><button class="btn primary" type="submit">Sign in</button><button class="btn" type="button" id="adminCancel">Cancel</button></div>
    <p class="note" id="adminNote" style="margin:0"></p>
  </form>
</div>
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
rep('<div class="toast" id="toast" hidden></div>','<div class="toast" id="toast" hidden></div>'+extra)
I={'/*I_EV*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
   '/*I_CAT*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>',
   '/*I_REQ*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h9l4 4v14H6zM9 11h7M9 15h7M9 7h4"/></svg>',
   '/*I_ADM*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/><circle cx="18" cy="17" r="2.5"/></svg>',
   '/*I_CART*/':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 4h2.5l2.2 11h10.6L20.5 8H7"/><circle cx="9.5" cy="19.5" r="1.5"/><circle cx="17" cy="19.5" r="1.5"/></svg>'}
for k,v in I.items(): s=s.replace(k,v)
s=s.replace('/*PHOTOS*/{}',json.dumps(json.load(open(os.path.join(HERE,'photos.json')))))
assert '/*I_' not in s and 'claude.use' not in s
h_end=s.index('</style>')+8
shim=open(os.path.join(HERE,'shim.js')).read()
html='<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex">\n<style>[hidden]{display:none!important}body{margin:0}img{max-width:100%}</style>\n'+s[:h_end]+'\n<script>'+shim+'</script>\n</head><body>\n'+s[h_end:]+'\n</body></html>\n'
out=os.path.join(HERE,'..','site')
os.makedirs(out,exist_ok=True)
open(os.path.join(out,'index.html'),'w').write(html)
if os.path.exists(os.path.join(out,'data.js')): os.remove(os.path.join(out,'data.js'))
print('built',len(html))
