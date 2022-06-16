import{G as Q,j as a,a as e,g as m,r as C,R as V,H as $,c as j,b as H,d as Y,F as S}from"./main.cd399812.js";import{d as y,u as n}from"./useIntervalQuery.98a17ea1.js";import{B as q}from"./BarChart.795448fe.js";function I(t){return Q({tag:"svg",attr:{viewBox:"0 0 24 24"},child:[{tag:"path",attr:{d:"M7 20h2V8h3L8 4 4 8h3zm13-4h-3V4h-2v12h-3l4 4z"}}]})(t)}const F=({device:t})=>a("div",{className:"device-item status-empty",children:[a("div",{className:"device-info",children:[e("img",{src:"https://via.placeholder.com/150",alt:t?t.auto_name:"Unknown Device",className:"hidden w-auto h-12 lg:block md:h-16"}),a("div",{className:"grid px-4 overflow-scroll",children:[e("h3",{children:t?t.auto_name:"Unknown Device"}),e("div",{className:"flex justify-between text-xs md:block",children:e("div",{children:a("p",{children:[t&&t.ip,e("br",{}),t&&t.mac]})})})]})]}),e("div",{className:"device-tags",children:e("div",{className:"px-4 py-1 text-sm text-white bg-gray-600 rounded-full h-fit",children:"tag"})}),a("div",{className:"device-details",children:[t&&e("div",{className:"flex items-center justify-center px-4 text-sm border-r border-gray-300 w-fit",children:y(t.outbound_byte_count)}),e("div",{className:"flex items-center justify-center px-4 text-sm w-fit",children:e("a",{href:`/device-activity?deviceid=${t.device_id}`,className:"",children:"Details"})})]})]}),G=m`
  query Query {
    devices {
      device_id
      auto_name
      ip
      mac
      outbound_byte_count
    }
  }
`,L=()=>{var d;const[t,c]=C.exports.useState(!1),s=n(G,null,5e3),[r,u]=C.exports.useState("");return a("section",{className:"bg-gray-50 flex-flex-col-gap-4",id:"inspecting-devices",children:[a("div",{className:"flex items-center w-full gap-4 md:gap-5",children:[a("div",{className:"",children:[e("h2",{className:"h1",children:"Inspecting Devices"}),e("p",{className:"py-2",children:"Naming & tagging helps with our research"})]}),e("div",{className:"w-8 h-8 md:w-10 md:h-10 animate-spin-slow",children:e(V,{})})]}),a("div",{className:"grid grid-cols-4 gap-4 py-4 md:flex md:items-center",children:[a("form",{className:"flex flex-1 order-last col-span-4 md:order-first",children:[e("input",{type:"text",name:"search",id:"searchDevices",value:r,onChange:i=>u(i.target.value),className:"w-full px-4 py-2 text-gray-600 bg-white border border-gray-400 rounded-md",placeholder:"Search devices by name or tag"}),a("label",{htmlFor:"searchDevices",className:"sr-only",children:[e($,{}),"Search devices by name or tag"]})]}),a("button",{className:"flex items-center justify-center gap-1 p-2 text-sm",children:["Name",e(I,{className:"w-4 h-4 text-gray-400"})]}),a("button",{className:"flex items-center justify-center gap-1 p-2 text-sm",children:["Traffic",e(I,{className:"w-4 h-4 text-gray-400"})]}),e("div",{className:"flex items-center justify-center gap-3 px-2",children:e(j,{checked:t,onChange:c,children:a("span",{className:"flex",children:[e(H,{className:`${t?"text-white rounded-lg bg-secondary":"text-dark"} w-10 h-10 md:w-8 md:h-8 p-1 `}),e(Y,{className:`${t?"text-dark":"text-white rounded-lg bg-secondary"} w-10 h-10 md:w-8 md:h-8 p-1 `})]})})})]}),e("ul",{className:t?"card-grid":"min-h-[200px]",children:(d=s==null?void 0:s.data)==null?void 0:d.devices.filter(i=>{if(!r||i.auto_name.toLowerCase().includes(r.toLowerCase()))return!0}).map(i=>e("li",{className:`${t?"card-view":"list-view"} py-2`,children:e(F,{device:i})},i.device_id))})]})},o=({children:t,bytes:c})=>a("div",{className:"flex-1 p-2 bg-white border border-gray-200 rounded-lg shadow-sm",children:[e("div",{className:"block",children:e("span",{className:"h1",children:y(c)})}),t]}),P=m`
  query Query {
    devices {
      auto_name
      ip
      outbound_byte_count
    }
  }
`,U=m`
  query Query($currentTime: Int) {
    adsAndTrackerBytes(current_time: $currentTime) {
      _sum
    }
  }
`,z=m`
  query Query($currentTime: Int) {
    unencryptedHttpTrafficBytes(current_time: $currentTime) {
      _sum
    }
  }
`,K=m`
  query Query($currentTime: Int) {
    weakEncryptionBytes(current_time: $currentTime) {
      _sum
    }
  }
`,M=()=>{var u,d,i,x,p,v,N,g,f,b,_,w,T,D,E,A,B,k;const t=n(U,null,5e3),c=n(z,null,5e3),s=n(K,null,5e3),r=n(P,null,2e4);return(u=r==null?void 0:r.data)!=null&&u.devices&&((d=r.data)==null||d.devices.sort((l,h)=>h.outbound_byte_count-l.outbound_byte_count),r.data.devices=(x=(i=r==null?void 0:r.data)==null?void 0:i.devices)==null?void 0:x.slice(0,3)),a(S,{children:[a("section",{className:"flex flex-col gap-4",children:[e("h1",{children:"Network Activity"}),e(q,{})]}),e("section",{className:"flex flex-col gap-4 bg-gray-50",children:a("div",{className:"grid gap-6 py-8 lg:grid-cols-2 md:py-4",children:[a("div",{children:[a("p",{children:["High data usage devices in the past 24 hours",e("br",{}),e("a",{href:"#inspecting-devices",children:"View all devices"})]}),e("div",{className:"grid grid-cols-2 gap-2 py-4",children:((p=r==null?void 0:r.data)==null?void 0:p.devices)&&((v=r==null?void 0:r.data)==null?void 0:v.devices.map((l,h)=>a(o,{bytes:l.outbound_byte_count,children:[e("span",{className:"text-xs",children:l.auto_name}),e("br",{}),e("span",{className:"text-xs",children:l.ip})]},h)))})]}),a("div",{children:[a("p",{children:["Monitored devices sent/recieved",e("br",{}),e("strong",{children:y(((g=(N=t==null?void 0:t.data)==null?void 0:N.adsAndTrackerBytes)==null?void 0:g._sum)+((b=(f=c==null?void 0:c.data)==null?void 0:f.unencryptedHttpTrafficBytes)==null?void 0:b._sum)+((w=(_=s==null?void 0:s.data)==null?void 0:_.weakEncryptionBytes)==null?void 0:w._sum))})]}),a("div",{className:"grid grid-cols-2 gap-2 py-4",children:[e(o,{bytes:(D=(T=t==null?void 0:t.data)==null?void 0:T.adsAndTrackerBytes)==null?void 0:D._sum,children:e("span",{className:"text-xs",children:"Ads & Trackers"})}),e(o,{bytes:(A=(E=c==null?void 0:c.data)==null?void 0:E.unencryptedHttpTrafficBytes)==null?void 0:A._sum,children:e("span",{className:"text-xs",children:"Unencrypted HTTP Traffic"})}),e(o,{bytes:(k=(B=s==null?void 0:s.data)==null?void 0:B.weakEncryptionBytes)==null?void 0:k._sum,children:e("span",{className:"text-xs",children:"Weak Encryption"})})]})]})]})})]})},X=()=>a(S,{children:[e(M,{}),e(L,{})]});export{X as default};
