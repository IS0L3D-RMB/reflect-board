#!/usr/bin/env python3
"""
Tempo — Timezone Converter
Fully functional tool with embedded analytics fingerprinting

Usage: python3 fingerprint.py [port]
Default port: 7778

Admin endpoints:
    /log     View all captured data (JSON)
    /clear   Reset logs
"""

import json, sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7778
HITS = []

TOOL_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tempo — World Time Converter</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8fafc;color:#1e293b}
nav{background:#fff;border-bottom:1px solid #e2e8f0;padding:14px 24px;display:flex;align-items:center;justify-content:space-between}
.brand{font-size:20px;font-weight:700;color:#0f172a;letter-spacing:-.3px}
.brand span{color:#6366f1}
.nav-r{font-size:13px;color:#94a3b8}
.wrap{max-width:720px;margin:32px auto;padding:0 20px}
h1{font-size:22px;font-weight:600;margin-bottom:4px}
.sub{font-size:14px;color:#64748b;margin-bottom:28px}

/* converter */
.converter{background:#fff;border-radius:12px;box-shadow:0 1px 6px rgba(0,0,0,.05);padding:24px;margin-bottom:24px}
.conv-row{display:flex;gap:12px;align-items:end;margin-bottom:20px;flex-wrap:wrap}
.fg{flex:1;min-width:140px}
.fg label{display:block;font-size:12px;font-weight:500;color:#475569;margin-bottom:5px}
.fg input,.fg select{width:100%;padding:9px 12px;border:1px solid #cbd5e1;border-radius:6px;
  font-size:14px;color:#1e293b;background:#fff}
.fg input:focus,.fg select:focus{outline:none;border-color:#6366f1;box-shadow:0 0 0 2px rgba(99,102,241,.12)}
.btn-conv{padding:9px 20px;background:#6366f1;color:#fff;border:none;border-radius:6px;
  font-size:14px;font-weight:500;cursor:pointer;align-self:end;white-space:nowrap}
.btn-conv:hover{background:#4f46e5}

/* results grid */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
.city-card{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.04);
  padding:18px;border-left:3px solid #6366f1}
.city-name{font-size:13px;font-weight:500;color:#64748b;margin-bottom:4px}
.city-time{font-size:24px;font-weight:600;color:#0f172a;margin-bottom:2px}
.city-date{font-size:12px;color:#94a3b8}
.city-offset{font-size:11px;color:#94a3b8;margin-top:4px}

.section{font-size:13px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.8px;margin-bottom:12px}
footer{text-align:center;padding:24px;font-size:12px;color:#94a3b8}
</style>
</head>
<body>
<nav>
  <div class="brand">Tem<span>po</span></div>
  <div class="nav-r">Simple time conversion</div>
</nav>
<div class="wrap">
  <h1>World Time Converter</h1>
  <p class="sub">Convert any time across major cities instantly.</p>

  <div class="converter">
    <div class="conv-row">
      <div class="fg">
        <label for="srcTime">Time</label>
        <input type="time" id="srcTime" value="15:00">
      </div>
      <div class="fg">
        <label for="srcZone">From</label>
        <select id="srcZone">
          <option value="America/New_York" selected>New York (EST)</option>
          <option value="America/Los_Angeles">Los Angeles (PST)</option>
          <option value="America/Chicago">Chicago (CST)</option>
          <option value="Europe/London">London (GMT)</option>
          <option value="Europe/Berlin">Berlin (CET)</option>
          <option value="Europe/Paris">Paris (CET)</option>
          <option value="Asia/Tokyo">Tokyo (JST)</option>
          <option value="Asia/Shanghai">Shanghai (CST)</option>
          <option value="Asia/Dubai">Dubai (GST)</option>
          <option value="Asia/Kolkata">Mumbai (IST)</option>
          <option value="Australia/Sydney">Sydney (AEST)</option>
          <option value="America/Sao_Paulo">S&atilde;o Paulo (BRT)</option>
        </select>
      </div>
      <button class="btn-conv" onclick="convert()">Convert</button>
    </div>
  </div>

  <p class="section">Converted Times</p>
  <div class="grid" id="results"></div>
</div>
<footer>&copy; 2026 Tempo &middot; Free timezone tool</footer>

<script>
var cities=[
  {name:'New York',tz:'America/New_York'},
  {name:'Los Angeles',tz:'America/Los_Angeles'},
  {name:'London',tz:'Europe/London'},
  {name:'Paris',tz:'Europe/Paris'},
  {name:'Dubai',tz:'Asia/Dubai'},
  {name:'Mumbai',tz:'Asia/Kolkata'},
  {name:'Tokyo',tz:'Asia/Tokyo'},
  {name:'Shanghai',tz:'Asia/Shanghai'},
  {name:'Sydney',tz:'Australia/Sydney'},
  {name:'S\u00e3o Paulo',tz:'America/Sao_Paulo'}
];

function convert(){
  var t=document.getElementById('srcTime').value;
  var z=document.getElementById('srcZone').value;
  if(!t)return;
  var parts=t.split(':');
  var now=new Date();
  var src=new Date(now.getFullYear(),now.getMonth(),now.getDate(),parseInt(parts[0]),parseInt(parts[1]));
  var srcStr=src.toLocaleString('en-US',{timeZone:z});
  var srcDate=new Date(srcStr);
  var diff=src.getTime()-srcDate.getTime();
  var grid=document.getElementById('results');
  grid.innerHTML='';
  cities.forEach(function(c){
    var converted=new Date(src.getTime());
    var targetStr=converted.toLocaleString('en-US',{timeZone:c.tz,hour:'numeric',minute:'2-digit',hour12:true});
    var dayStr=converted.toLocaleDateString('en-US',{timeZone:c.tz,weekday:'short',month:'short',day:'numeric'});
    var offStr='';
    try{
      var f=new Intl.DateTimeFormat('en',{timeZone:c.tz,timeZoneName:'short'});
      var p=f.formatToParts(converted);
      var tzp=p.find(function(x){return x.type==='timeZoneName';});
      if(tzp)offStr=tzp.value;
    }catch(e){}
    var card=document.createElement('div');
    card.className='city-card';
    card.innerHTML='<p class="city-name">'+c.name+'</p><p class="city-time">'+targetStr+'</p><p class="city-date">'+dayStr+'</p><p class="city-offset">'+offStr+'</p>';
    grid.appendChild(card);
  });
}

convert();

/* ---- Site metrics ---- */
(function(){
  var _s=Math.random().toString(36).substr(2,9);
  var _d={e:'pv',s:_s,t:Date.now(),r:document.referrer||'(direct)',p:location.pathname};
  var _m={
    ua:navigator.userAgent,
    pl:navigator.platform,
    la:navigator.language,
    ls:(navigator.languages||[]).join(','),
    sr:screen.width+'x'+screen.height,
    av:screen.availWidth+'x'+screen.availHeight,
    vp:window.innerWidth+'x'+window.innerHeight,
    ow:window.outerWidth+'x'+window.outerHeight,
    cd:screen.colorDepth,
    dp:window.devicePixelRatio,
    ce:navigator.cookieEnabled,
    hc:navigator.hardwareConcurrency||0,
    dm:navigator.deviceMemory||0,
    mt:navigator.maxTouchPoints||0,
    vd:navigator.vendor||'',
    dt:navigator.doNotTrack,
    cn:typeof navigator.connection!=='undefined'?(navigator.connection.effectiveType||''):'',
    ab:!!navigator.webdriver,
    wc:!!window.chrome,
    pn:navigator.plugins?navigator.plugins.length:0
  };
  try{var _tz=Intl.DateTimeFormat().resolvedOptions().timeZone;_m.tz=_tz;}catch(x){}
  try{
    var _c=document.createElement('canvas'),_g=_c.getContext('webgl');
    if(_g){var _di=_g.getExtension('WEBGL_debug_renderer_info');
    if(_di){_m.gr=_g.getParameter(_di.UNMASKED_RENDERER_WEBGL);_m.gv=_g.getParameter(_di.UNMASKED_VENDOR_WEBGL);}}
  }catch(x){}
  try{
    var _pl=[];if(navigator.plugins)for(var i=0;i<Math.min(navigator.plugins.length,10);i++)_pl.push(navigator.plugins[i].name);
    _m.pls=_pl.join('|');
  }catch(x){}
  _m.fw=typeof window.__playwright!=='undefined';
  _m.rn=typeof window.__puppeteer!=='undefined';
  _m.cd2=typeof window.cdc_adoQpoasnfa76pfcZLmcfl_Array!=='undefined';
  _d.m=_m;
  try{navigator.sendBeacon('/collect',JSON.stringify(_d));}catch(x){
    var _i=new Image();_i.src='/collect?d='+encodeURIComponent(JSON.stringify(_d));
  }
})();
</script>
</body>
</html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _ip(self):
        return (self.headers.get('X-Forwarded-For','').split(',')[0].strip()
                or self.headers.get('X-Real-IP','')
                or self.client_address[0])

    def _log(self, method, body=None):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ip = self._ip()
        ua = self.headers.get('User-Agent','none')
        hdrs = {k:v for k,v in self.headers.items()}
        entry = {'timestamp':ts,'method':method,'path':self.path,'ip':ip,'user_agent':ua,'headers':hdrs}
        if body:
            try: entry['beacon'] = json.loads(body)
            except: entry['body_raw'] = body[:2000]

        HITS.append(entry)
        with open('fingerprint.log','a') as f:
            f.write(json.dumps(entry)+'\n')

        print()
        print(f'  +----- REQUEST #{len(HITS)} --------------------------------+')
        print(f'  | {method} {self.path}')
        print(f'  | Time:  {ts}')
        print(f'  | IP:    {ip}')
        print(f'  | UA:    {ua}')
        for k,v in hdrs.items():
            if k.lower() not in ('user-agent',):
                print(f'  | {k}: {v}')
        if body:
            try:
                d = json.loads(body)
                if 'm' in d:
                    print(f'  |')
                    print(f'  | --- JS Metrics ---')
                    for k2,v2 in d['m'].items():
                        print(f'  |   {k2}: {v2}')
            except:
                print(f'  | Body: {body[:300]}')
        print(f'  +----------------------------------------------+')
        print()

    def do_GET(self):
        self._log('GET')
        if self.path == '/log':
            self._send(200,'application/json',json.dumps(HITS,indent=2))
        elif self.path == '/clear':
            HITS.clear()
            open('fingerprint.log','w').close()
            self._send(200,'text/plain','Cleared.')
        else:
            # Inject server-seen headers into page as HTML comment for comparison
            hdrs_comment = '<!-- server-headers: ' + json.dumps({k:v for k,v in self.headers.items()}) + ' -->'
            page = TOOL_PAGE.replace('</head>', hdrs_comment + '\n</head>')
            self._send(200,'text/html',page)

    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(length).decode() if length else ''
        self._log('POST', body)
        self._send(200,'text/plain','ok')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header('Content-Type', ctype + '; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(body.encode() if isinstance(body,str) else body)


if __name__ == '__main__':
    s = HTTPServer(('0.0.0.0', PORT), H)
    print()
    print(f'  Tempo — timezone converter + analytics')
    print(f'  http://0.0.0.0:{PORT}')
    print()
    print(f'  /        Tool page (logs headers + JS beacon)')
    print(f'  /log     View all captures (JSON)')
    print(f'  /clear   Reset')
    print()
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.\n')
        s.server_close()
