import{G as Q,j as a,a as e,g as h,r as p,R as V,H as $,c as j,b as H,d as Y,F as I}from"./main.84aef56a.js";import{d as N,u}from"./useIntervalQuery.b3466ab8.js";import{B as q}from"./BarChart.0ddb05fa.js";function S(t){return Q({tag:"svg",attr:{viewBox:"0 0 24 24"},child:[{tag:"path",attr:{d:"M7 20h2V8h3L8 4 4 8h3zm13-4h-3V4h-2v12h-3l4 4z"}}]})(t)}const F=({device:t})=>a("div",{className:"device-item status-empty",children:[a("div",{className:"device-info",children:[e("img",{src:"https://via.placeholder.com/150",alt:t?t.auto_name:"Unknown Device",className:"hidden w-auto h-12 lg:block md:h-16"}),a("div",{className:"grid px-4 overflow-scroll",children:[e("h3",{children:t?t.auto_name:"Unknown Device"}),e("div",{className:"flex justify-between text-xs md:block",children:e("div",{children:a("p",{children:[t&&t.ip,e("br",{}),t&&t.mac]})})})]})]}),e("div",{className:"device-tags",children:e("div",{className:"px-4 py-1 text-sm text-white bg-gray-600 rounded-full h-fit",children:"tag"})}),a("div",{className:"device-details",children:[t&&e("div",{className:"flex items-center justify-center px-4 text-sm border-r border-gray-300 w-fit",children:N(t.outbound_byte_count)}),e("div",{className:"flex items-center justify-center px-4 text-sm w-fit",children:e("a",{href:`/device-activity?deviceid=${t.device_id}`,className:"",children:"Details"})})]})]}),G=h`
  query Query {
    devices {
      device_id
      auto_name
      ip
      mac
      outbound_byte_count
    }
  }
`,L=()=>{var m;const[t,i]=p.exports.useState(!1),c=u(G,null,5e3),[r,y]=p.exports.useState(""),[l,n]=p.exports.useState([]);return p.exports.useEffect(()=>{var s,d;(s=c==null?void 0:c.data)!=null&&s.devices&&n((d=c==null?void 0:c.data)==null?void 0:d.devices)},[(m=c==null?void 0:c.data)==null?void 0:m.devices]),a("section",{className:"bg-gray-50 flex-flex-col-gap-4",id:"inspecting-devices",children:[a("div",{className:"flex items-center w-full gap-4 md:gap-5",children:[a("div",{className:"",children:[e("h2",{className:"h1",children:"Inspecting Devices"}),e("p",{className:"py-2",children:"Naming & tagging helps with our research"})]}),e("div",{className:"w-8 h-8 md:w-10 md:h-10 animate-spin-slow",children:e(V,{})})]}),a("div",{className:"grid grid-cols-4 gap-4 py-4 md:flex md:items-center",children:[a("form",{className:"flex flex-1 order-last col-span-4 md:order-first",children:[e("input",{type:"text",name:"search",id:"searchDevices",value:r,onChange:s=>y(s.target.value),className:"w-full px-4 py-2 text-gray-600 bg-white border border-gray-400 rounded-md",placeholder:"Search devices by name or tag"}),a("label",{htmlFor:"searchDevices",className:"sr-only",children:[e($,{}),"Search devices by name or tag"]})]}),a("button",{className:"flex items-center justify-center gap-1 p-2 text-sm",children:["Name",e(S,{className:"w-4 h-4 text-gray-400"})]}),a("button",{className:"flex items-center justify-center gap-1 p-2 text-sm",onClick:()=>{const s=l.sort((d,x)=>d.outbound_byte_count>x.outbound_byte_count?1:(console.log(d.outbound_byte_count),0));n(s)},children:["Traffic",e(S,{className:"w-4 h-4 text-gray-400"})]}),e("div",{className:"flex items-center justify-center gap-3 px-2",children:e(j,{checked:t,onChange:i,children:a("span",{className:"flex",children:[e(H,{className:`${t?"text-white rounded-lg bg-secondary":"text-dark"} w-10 h-10 md:w-8 md:h-8 p-1 `}),e(Y,{className:`${t?"text-dark":"text-white rounded-lg bg-secondary"} w-10 h-10 md:w-8 md:h-8 p-1 `})]})})})]}),e("ul",{className:t?"card-grid":"min-h-[200px]",children:l==null?void 0:l.filter(s=>{if(!r||s.auto_name.toLowerCase().includes(r.toLowerCase()))return!0}).map(s=>e("li",{className:`${t?"card-view":"list-view"} py-2`,children:e(F,{device:s})},s.device_id))})]})},f=({children:t,bytes:i})=>a("div",{className:"flex-1 px-4 py-3 bg-white border border-gray-200 rounded-lg shadow-sm",children:[e("div",{className:"block",children:e("span",{className:"h1",children:N(i)})}),t]}),P=h`
  query Query {
    devices {
      auto_name
      ip
      outbound_byte_count
    }
  }
`,U=h`
  query Query($currentTime: Int) {
    adsAndTrackerBytes(current_time: $currentTime) {
      _sum
    }
  }
`,z=h`
  query Query($currentTime: Int) {
    unencryptedHttpTrafficBytes(current_time: $currentTime) {
      _sum
    }
  }
`,K=h`
  query Query($currentTime: Int) {
    weakEncryptionBytes(current_time: $currentTime) {
      _sum
    }
  }
`,M=()=>{var y,l,n,m,s,d,x,v,b,_,w,T,D,E,k,A,B,C;const t=u(U,null,5e3),i=u(z,null,5e3),c=u(K,null,5e3),r=u(P,null,2e4);return(y=r==null?void 0:r.data)!=null&&y.devices&&((l=r.data)==null||l.devices.sort((o,g)=>g.outbound_byte_count-o.outbound_byte_count),r.data.devices=(m=(n=r==null?void 0:r.data)==null?void 0:n.devices)==null?void 0:m.slice(0,3)),a(I,{children:[a("section",{className:"flex flex-col gap-4",children:[e("h1",{children:"Network Activity"}),e(q,{})]}),e("section",{className:"flex flex-col gap-4 bg-gray-50",children:a("div",{className:"grid gap-6 py-8 lg:grid-cols-2 md:py-4",children:[a("div",{children:[a("p",{children:["High data usage devices in the past 24 hours",e("br",{}),e("a",{href:"#inspecting-devices",children:"View all devices"})]}),e("div",{className:"grid grid-cols-2 gap-2 py-4",children:((s=r==null?void 0:r.data)==null?void 0:s.devices)&&((d=r==null?void 0:r.data)==null?void 0:d.devices.map((o,g)=>a(f,{bytes:o.outbound_byte_count,children:[e("span",{className:"text-xs",children:o.auto_name}),e("br",{}),e("span",{className:"text-xs",children:o.ip})]},g)))})]}),a("div",{children:[a("p",{children:["Monitored devices sent/recieved",e("br",{}),e("strong",{children:N(((v=(x=t==null?void 0:t.data)==null?void 0:x.adsAndTrackerBytes)==null?void 0:v._sum)+((_=(b=i==null?void 0:i.data)==null?void 0:b.unencryptedHttpTrafficBytes)==null?void 0:_._sum)+((T=(w=c==null?void 0:c.data)==null?void 0:w.weakEncryptionBytes)==null?void 0:T._sum))})]}),a("div",{className:"grid grid-cols-2 gap-2 py-4",children:[e(f,{bytes:(E=(D=t==null?void 0:t.data)==null?void 0:D.adsAndTrackerBytes)==null?void 0:E._sum,children:e("span",{className:"text-xs",children:"Ads & Trackers"})}),e(f,{bytes:(A=(k=i==null?void 0:i.data)==null?void 0:k.unencryptedHttpTrafficBytes)==null?void 0:A._sum,children:e("span",{className:"text-xs",children:"Unencrypted HTTP Traffic"})}),e(f,{bytes:(C=(B=c==null?void 0:c.data)==null?void 0:B.weakEncryptionBytes)==null?void 0:C._sum,children:e("span",{className:"text-xs",children:"Weak Encryption"})})]})]})]})})]})},X=()=>a(I,{children:[e(M,{}),e(L,{})]});export{X as default};
