package web

import (
	"fmt"
	"html/template"
	"net/http"
)

func render(w http.ResponseWriter, t *template.Template, data any) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	if err := t.Execute(w, data); err != nil {
		http.Error(w, err.Error(), 500)
	}
}

var funcs = template.FuncMap{"bytes": humanBytes}

func humanBytes(n int64) string {
	const u = 1024
	if n < u {
		return fmt.Sprintf("%d B", n)
	}
	div, exp := int64(u), 0
	for x := n / u; x >= u; x /= u {
		div *= u
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(n)/float64(div), "KMGT"[exp])
}

const base = `
<style>
 :root { --bg:#f6f7f9; --card:#ffffff; --line:#e3e8ef; --fg:#1f2430; --mut:#6b7280; --accent:#2f6fed; --ok:#1a8f4c; }
 * { box-sizing:border-box }
 body { margin:0; background:var(--bg); color:var(--fg); font:14px/1.5 system-ui,sans-serif }
 a { color:var(--accent); text-decoration:none } a:hover { text-decoration:underline }
 header { padding:1rem 1.5rem; border-bottom:1px solid var(--line); display:flex; align-items:baseline; gap:1rem }
 header h1 { margin:0; font-size:1.1rem } header .mut { color:var(--mut) }
 main { padding:1.5rem; max-width:70rem; margin:0 auto }
 table { width:100%; border-collapse:collapse }
 th,td { text-align:left; padding:.5rem .6rem; border-bottom:1px solid var(--line); vertical-align:top }
 th { color:var(--mut); font-weight:600; font-size:.8rem; text-transform:uppercase; letter-spacing:.03em }
 tr:hover td { background:var(--card) }
 .num { text-align:right; font-variant-numeric:tabular-nums }
 .badge { background:var(--accent); color:#001; font-size:.7rem; padding:.05rem .4rem; border-radius:.4rem; font-weight:700 }
 .card { background:var(--card); border:1px solid var(--line); border-radius:.6rem; padding:1rem 1.2rem; margin:0 0 1rem }
 .card h2 { margin:0 0 .6rem; font-size:.85rem; text-transform:uppercase; color:var(--mut); letter-spacing:.03em }
 .kv { display:grid; grid-template-columns:9rem 1fr; gap:.3rem 1rem }
 .kv div:nth-child(odd) { color:var(--mut) }
 pre { background:#f0f2f5; border:1px solid var(--line); border-radius:.4rem; padding:.6rem; overflow:auto; font-size:.8rem; max-height:18rem }
 code { background:#f0f2f5; padding:.05rem .3rem; border-radius:.3rem; font-size:.85em }
 .empty { color:var(--mut); font-style:italic }
 .metrics { display:flex; gap:1rem; margin:0 0 1.5rem }
 .metric { background:var(--card); border:1px solid var(--line); border-radius:.6rem; padding:.8rem 1.2rem; min-width:9rem }
 .metric .v { font-size:1.6rem; font-weight:700 } .metric .l { color:var(--mut); font-size:.8rem }
 .charts { display:flex; flex-direction:column; gap:.5rem }
 .charts-stack { display:flex; flex-direction:column; gap:.5rem; margin-top:.3rem }
 .chart { width:100%; height:auto; display:block; background:#fff; border:1px solid var(--line); border-radius:.4rem }
 .chart .tick { fill:#6b7280; font-size:8px } .chart .ctitle-svg { fill:#374151; font-size:9px; font-weight:600 }
 .toggle { display:inline-block; padding:.2rem .7rem; border-radius:.4rem; border:1px solid var(--line); font-size:.8rem; cursor:pointer; background:var(--card); color:var(--fg) }
 .toggle.on { background:var(--accent); color:#001; border-color:var(--accent); font-weight:700 }
 .dcard { background:var(--card); border:1px solid var(--line); border-radius:.6rem; padding:1rem 1.2rem; margin:0 0 1rem }
 .drow { display:flex; align-items:center; gap:.8rem }
 .dname { font-weight:600; font-size:1.05rem }
 .caption { color:var(--mut); font-size:.82rem; margin:.2rem 0 .7rem }
 .ctitle { color:var(--mut); font-size:.78rem; margin-bottom:.3rem }
 .label-row { display:flex; align-items:center; gap:.5rem; font-size:.84rem; margin:.25rem 0 }
 .label-row .k { color:var(--mut); width:3.5rem } .label-row .v { font-weight:600 }
 .label-row .v.unconfirmed { font-weight:400; font-style:italic; color:var(--mut) }
 .label-row .ok { color:var(--ok); font-weight:700 }
 .mini { font-size:.72rem; padding:.05rem .45rem; border-radius:.4rem; border:1px solid var(--line); background:var(--card); color:var(--fg); cursor:pointer }
 .mini.yes { border-color:var(--ok); color:var(--ok) }
</style>`

var indexTmpl = template.Must(template.New("index").Funcs(funcs).Parse(`<!doctype html><html><head>
<meta charset="utf-8"><title>inspector-go</title>` + base + `</head><body>
<header><h1>inspector-go</h1><span class="mut" id="status">connecting…</span></header>
<main>
<div class="metrics">
 <div class="metric"><div class="v" id="m-dev">–</div><div class="l">devices seen</div></div>
 <div class="metric"><div class="v" id="m-insp">–</div><div class="l">inspected</div></div>
 <div class="metric"><div class="v" id="m-data">–</div><div class="l">data use · last 10s</div></div>
</div>
<div id="devices"></div>
</main>
<script>
const C_LINE='#1f77b4';  // matplotlib blue, matching the original
function hb(n){if(n<1024)return Math.round(n)+' B';const u=['KB','MB','GB','TB'];let i=-1;do{n/=1024;i++}while(n>=1024&&i<3);return n.toFixed(1)+' '+u[i];}
// chart draws one stacked line panel (white grid, blue line+area) — the PR-275
// burst-style look, at 1s resolution. series[0]=now, series[n-1]=60s ago.
function chart(series,label){
  const W=640,H=128,padL=46,padR=10,padT=15,padB=16,n=series.length;
  const plotW=W-padL-padR, plotH=H-padT-padB;
  let max=0; for(const v of series) if(v>max) max=v;
  let g='<svg viewBox="0 0 '+W+' '+H+'" class="chart" preserveAspectRatio="none">';
  g+='<rect x="'+padL+'" y="'+padT+'" width="'+plotW+'" height="'+plotH+'" fill="#ffffff"/>';
  for(let i=0;i<=3;i++){const y=padT+plotH*i/3, val=max*(1-i/3);
    g+='<line x1="'+padL+'" y1="'+y.toFixed(1)+'" x2="'+(W-padR)+'" y2="'+y.toFixed(1)+'" stroke="#e3e8ef"/>';
    g+='<text x="'+(padL-5)+'" y="'+(y+3).toFixed(1)+'" text-anchor="end" class="tick">'+hb(val)+'/s</text>';}
  if(max>0){
    let pts=[];
    for(let i=0;i<n;i++){const x=padL+plotW*(1-i/(n-1)), y=padT+plotH*(1-series[i]/max); pts.push(x.toFixed(1)+','+y.toFixed(1));}
    g+='<polygon points="'+padL+','+(padT+plotH)+' '+pts.join(' ')+' '+(W-padR)+','+(padT+plotH)+'" fill="'+C_LINE+'" opacity="0.10"/>';
    g+='<polyline points="'+pts.join(' ')+'" fill="none" stroke="'+C_LINE+'" stroke-width="1.3"/>';
  } else {
    g+='<text x="'+(padL+plotW/2)+'" y="'+(padT+plotH/2)+'" text-anchor="middle" class="tick">no traffic in last 60s</text>';
  }
  g+='<text x="'+padL+'" y="'+(padT-4)+'" class="ctitle-svg">'+label+'</text>';
  g+='<text x="'+padL+'" y="'+(H-4)+'" class="tick">−60s</text>';
  g+='<text x="'+(W-padR)+'" y="'+(H-4)+'" text-anchor="end" class="tick">now</text>';
  g+='</svg>';
  return g;
}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
// one labeling row: confirmed value with edit, or an inferred guess to confirm/correct.
function row(k, field, inferred, confirmed, mac){
  const da='data-mac="'+esc(mac)+'" data-field="'+field+'"';
  if(confirmed){
    return '<div class="label-row"><span class="k">'+k+'</span><span class="v">'+esc(confirmed)+'</span><span class="ok">✓</span>'
      +'<a class="mini" data-act="edit" data-cur="'+esc(confirmed)+'" '+da+'>✎ change</a></div>';
  }
  const guess = inferred ? esc(inferred)+' <span class="mut">(guess)</span>' : '<span class="mut">unknown</span>';
  let btns = inferred ? '<a class="mini yes" data-act="confirm" data-val="'+esc(inferred)+'" '+da+'>✓ correct</a> ' : '';
  btns += '<a class="mini" data-act="edit" data-cur="'+esc(inferred||'')+'" '+da+'>✎ '+(inferred?'fix':'set')+'</a>';
  return '<div class="label-row"><span class="k">'+k+'</span><span class="v unconfirmed">'+guess+'</span>'+btns+'</div>';
}
function card(x){
  const toggle = x.gateway ? '<span class="badge">gateway</span>'
    : '<a class="toggle '+(x.inspected?'on':'')+'" href="#" onclick="return tog(\''+x.mac+'\','+(x.inspected?0:1)+')">'+(x.inspected?'inspecting':'inspect')+'</a>';
  let body = '<div class="dcard"><div class="drow"><a class="dname" href="/device?mac='+encodeURIComponent(x.mac)+'">'+esc(x.name)+'</a>'+toggle+'</div>'
    +'<div class="caption">'+x.ip+' · <code>'+x.mac+'</code> · '+x.contacts+' contacts · '+hb(x.bytes)+' in 60s</div>';
  if(!x.gateway){
    body += row('Vendor','vendor_confirmed',x.vendorInferred,x.vendorConfirmed,x.mac)
         +  row('Type','type_confirmed',x.typeInferred,x.typeConfirmed,x.mac);
  }
  body += '<div class="charts-stack">'+chart(x.up,'↑ Upload Traffic (sent by device) — last 60s')+chart(x.down,'↓ Download Traffic (received) — last 60s')+'</div></div>';
  return body;
}
async function lab(mac,field,value){ try{ await fetch('/label?mac='+encodeURIComponent(mac)+'&field='+field+'&value='+encodeURIComponent(value)); }catch(e){} tick(); }
async function tog(mac,on){ try{ await fetch('/inspect?mac='+encodeURIComponent(mac)+'&on='+on); }catch(e){} tick(); return false; }
async function tick(){
  try{
    const d = await (await fetch('/api/state')).json();
    document.getElementById('m-dev').textContent = d.devices;
    document.getElementById('m-insp').textContent = d.inspected;
    document.getElementById('m-data').textContent = hb(d.dataUse);
    document.getElementById('devices').innerHTML = (d.list||[]).map(card).join('') || '<p class="empty">No devices yet — discovery in progress.</p>';
    document.getElementById('status').textContent = 'live · updating every 1.5s';
  }catch(e){ document.getElementById('status').textContent = 'disconnected'; }
}
// delegated handler for the confirm/edit label buttons (survives the innerHTML redraws)
document.getElementById('devices').addEventListener('click', function(e){
  const el = e.target.closest('[data-act]');
  if(!el) return;
  e.preventDefault();
  const mac = el.getAttribute('data-mac'), field = el.getAttribute('data-field');
  if(el.getAttribute('data-act') === 'confirm'){
    lab(mac, field, el.getAttribute('data-val'));
  } else {
    const v = prompt('Enter value', el.getAttribute('data-cur') || '');
    if(v !== null && v.trim() !== '') lab(mac, field, v.trim());
  }
});
tick(); setInterval(tick, 1500);
</script>
</body></html>`))

var deviceTmpl = template.Must(template.New("device").Funcs(funcs).Parse(`<!doctype html><html><head>
<meta charset="utf-8"><title>{{if .Name}}{{.Name}}{{else}}{{.MAC}}{{end}} · inspector-go</title>` + base + `</head><body>
<header><h1><a href="/">← devices</a></h1>
<span>{{if .Name}}{{.Name}}{{else}}<span class="empty">unknown device</span>{{end}}</span>
{{if .IsGateway}}<span class="badge">gateway</span>
{{else if .Inspected}}<a class="toggle on" href="/inspect?mac={{.MAC}}&on=0">inspecting · click to stop</a>
{{else}}<a class="toggle" href="/inspect?mac={{.MAC}}&on=1">not inspected · click to start</a>{{end}}</header>
<main>
<div class="card"><h2>Traffic — last 60s</h2>
{{if .Inspected}}
<div class="charts-stack">{{.Upload}}{{.Download}}</div>
{{else}}<p class="empty">Not inspected — start inspection above to capture this device's traffic.</p>{{end}}
</div>
<div class="card"><h2>Identity</h2>
<div class="kv">
 <div>IP</div><div>{{.IP}}</div>
 <div>MAC</div><div><code>{{.MAC}}</code></div>
 <div>Vendor</div><div>{{if .Vendor}}{{.Vendor}}{{else}}<span class="empty">—</span>{{end}}</div>
 <div>DHCP hostname</div><div>{{if .DHCP}}{{.DHCP}}{{else}}<span class="empty">—</span>{{end}}</div>
 <div>User-Agent</div><div>{{if .UserAgent}}{{.UserAgent}}{{else}}<span class="empty">—</span>{{end}}</div>
 <div>JA3</div><div>{{if .JA3}}{{range .JA3}}<code>{{.}}</code> {{end}}{{else}}<span class="empty">—</span>{{end}}</div>
</div></div>

<div class="card"><h2>Contacted destinations</h2>
{{if .Contacts}}
<table><tr><th>Host</th><th>Proto</th><th>Ports</th><th class="num">Packets</th><th class="num">Bytes</th></tr>
{{range .Contacts}}<tr><td>{{.Host}}</td><td>{{.Protocol}}</td><td>{{.Ports}}</td><td class="num">{{.Packets}}</td><td class="num">{{bytes .Bytes}}</td></tr>{{end}}
</table>
{{else}}<p class="empty">No traffic captured (this device isn't being inspected, or hasn't talked yet).</p>{{end}}
</div>

{{if .MDNS}}<div class="card"><h2>mDNS</h2><pre>{{.MDNS}}</pre></div>{{end}}
{{if .SSDP}}<div class="card"><h2>SSDP / UPnP</h2><pre>{{.SSDP}}</pre></div>{{end}}
</main></body></html>`))
