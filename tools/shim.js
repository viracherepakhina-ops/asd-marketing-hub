/* Tiny client for the site's /api — same shape the page code uses (collection/doc/onSnapshot). */
(function(){
  const KEY_STORE="asd-admin-key";
  const adminKey=()=>{ try{ return localStorage.getItem(KEY_STORE)||""; }catch(e){ return ""; } };
  async function call(method,path,body){
    const h={"Content-Type":"application/json"}; const k=adminKey(); if(k) h["x-admin-key"]=k;
    const r=await fetch("/api/"+path,{method,headers:h,body:body?JSON.stringify(body):undefined,cache:"no-store"});
    if(!r.ok){ const e=new Error("HTTP "+r.status); e.code=r.status===401?"invalid_argument":"unavailable"; throw e; }
    return r.json();
  }
  const subs={};  // col -> [{cb,order}]
  async function refresh(col){
    const list=subs[col]; if(!list||!list.length) return;
    try{ const {docs}=await call("GET",col);
      list.forEach(({cb,order})=>{ let d=docs.slice(); if(order){ const [f,dir]=order; d.sort((a,b)=>{ const x=a[f],y=b[f]; return (x>y?1:x<y?-1:0)*(dir==="desc"?-1:1); }); }
        cb({docs:d.map(x=>{ const {id,...rest}=x; return {id,exists:true,data:()=>rest}; })}); });
    }catch(e){ console.warn("refresh failed",col,e); }
  }
  setInterval(()=>Object.keys(subs).forEach(refresh),20000);
  document.addEventListener("visibilitychange",()=>{ if(!document.hidden) Object.keys(subs).forEach(refresh); });
  function collection(col,order){
    return {
      orderBy:(f,dir)=>collection(col,[f,dir||"asc"]),
      onSnapshot(cb){ (subs[col]=subs[col]||[]).push({cb,order}); refresh(col); return ()=>{ subs[col]=subs[col].filter(s=>s.cb!==cb); }; },
      async add(body){ const r=await call("POST",col,body); refresh(col); return {id:r.id}; },
      doc:(id)=>doc(col+"/"+id)
    };
  }
  function doc(path){
    const [col,id]=path.split("/");
    return {
      async set(b){ await call("PUT",col+"/"+encodeURIComponent(id),b); refresh(col); },
      async update(b){ await call("PATCH",col+"/"+encodeURIComponent(id),b); refresh(col); },
      async delete(){ await call("DELETE",col+"/"+encodeURIComponent(id)); refresh(col); }
    };
  }
  window.HubDB={ collection, doc, adminKey, setAdminKey(k){ try{ k?localStorage.setItem(KEY_STORE,k):localStorage.removeItem(KEY_STORE); }catch(e){} },
    async checkAdmin(){ if(!adminKey()) return false; try{ await call("GET","auth"); return true; }catch(e){ return false; } } };
})();
