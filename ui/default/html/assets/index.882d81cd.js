import{j as c,a as e,g as m,u as p,b,c as N,r as d,F as y,L as A}from"./main.2be1b207.js";import{I as k}from"./InspectingDevices.cdd09a5d.js";import{d as v}from"./utils.9f03f89a.js";import{_ as w,D as I}from"./DefaultLayout.4bc4c9b1.js";import{E}from"./EndpointDrawer.0c637a5c.js";import"./selects.5d291e59.js";import"./useUserConfigs.1a3d1d00.js";import"./index.6ed2c2c6.js";import"./NoConsentLayout.4af4afdc.js";import"./index.2e772c49.js";const h=({children:i,bytes:r})=>c("div",{className:"flex-1 px-4 py-3 bg-white border border-gray-200 rounded-lg shadow-sm",children:[e("div",{className:"block",children:e("span",{className:"h1",children:v(r)})}),i]}),U=m`
  query Query {
    chartActivity {
      xAxis
      yAxis {
        name
        data
      }
    }
  }
`,D=i=>{const r={pullInterval:(i==null?void 0:i.pullInterval)||6e5},t={deviceId:(i==null?void 0:i.deviceId)||null},{data:s,loading:a}=p(U,{variables:t,pollInterval:r.pullInterval});return{networkDownloadActivity:s,networkDownloadActivityLoading:a}},T=({deviceId:i})=>{const{networkDownloadActivity:r,networkDownloadActivityLoading:t}=D({pullInterval:6e4}),{devicesData:s,error:a}=b(),{showError:l}=N();d.exports.useEffect(()=>{a&&l(a.message)},[a]);const u=d.exports.useMemo(()=>{var n;return{chart:{id:"bar",stacked:!0},xaxis:{categories:((n=r==null?void 0:r.chartActivity)==null?void 0:n.xAxis)||[],type:"string"},options:{plotOptions:{bar:{borderRadius:"10px"}}}}},[r]),_=d.exports.useMemo(()=>{var g;if(!s||!r)return[];let n=r;return n=n.chartActivity.yAxis.map(x=>{const o=s.devices.find(f=>f.device_id===x.name);return{...x,name:(o==null?void 0:o.device_info.device_name)||(o==null?void 0:o.auto_name)||`Unknown Device - ${o==null?void 0:o.device_id}`}}),n={...r,chartActivity:{yAxis:n}},((g=n==null?void 0:n.chartActivity)==null?void 0:g.yAxis.slice(0,3))||[]},[r,s]);return e("div",{className:"network-bar-chart",children:e("div",{className:"row",children:e("div",{className:"mixed-chart",children:e(w,{options:u,series:_,type:"bar",width:"100%",height:"300"})})})})},L=m`
  query Query {
    devices {
      auto_name
      ip
      outbound_byte_count
    }
  }
`,H=()=>{const[i,r]=d.exports.useState([]),{data:t,loading:s}=p(L,{pollInterval:2e4});return d.exports.useEffect(()=>{if(t!=null&&t.devices){const a=t==null?void 0:t.devices.slice().sort((l,u)=>u.outbound_byte_count-l.outbound_byte_count);r(a)}},[t==null?void 0:t.devices]),{highUseageData:i,highUseageDataLoading:s}},Q=m`
  query Query {
    networkActivity {
      weak_encryption
      unencrypted_http_traffic
      ads_and_trackers
    }
  }
`,C=()=>{const[i,r]=d.exports.useState([]),{data:t,loading:s}=p(Q,{});return d.exports.useEffect(()=>{t!=null&&t.networkActivity&&r(t.networkActivity)},[t==null?void 0:t.networkActivity]),{networkActivityData:i,networkActivityDataLoading:s}},R=()=>{const{highUseageData:i,highUseageDataLoading:r}=H(),{networkActivityDataLoading:t,networkActivityData:s}=C();return c(y,{children:[r?e("div",{className:"h-full skeleton"}):c("section",{className:"flex flex-col gap-4",children:[e("h1",{children:"Network Activity"}),c("p",{children:["High data usage devices in the past 24 hours",e("br",{}),e(A,{to:"#inspecting-devices",children:"View all devices"})]}),e(T,{}),c("div",{className:"grid gap-2 py-4 md:grid-cols-2 lg:grid-cols-3",children:[r&&e(y,{children:e("div",{className:"skeleton h-[114px]"})}),i&&i.slice(0,3).map((a,l)=>c(h,{bytes:a.outbound_byte_count,children:[e("span",{className:"text-xs",children:a.auto_name}),e("br",{}),e("span",{className:"text-xs",children:a.ip})]},l))]}),e("hr",{}),e("div",{className:"grid gap-6 py-8 md:py-4",children:t?e("div",{className:"skeleton h-[114px]"}):c("div",{children:[c("p",{children:["All monitored devices sent/recieved \xA0",e("strong",{children:v((s==null?void 0:s.ads_and_trackers)+(s==null?void 0:s.unencrypted_http_traffic)+(s==null?void 0:s.weak_encryption))}),"\xA0 of data"]}),c("div",{className:"grid gap-2 py-4 md:grid-cols-2 lg:grid-cols-3",children:[e(h,{bytes:s==null?void 0:s.ads_and_trackers,children:e("span",{className:"text-xs",children:"Ads & Trackers"})}),e(h,{bytes:s==null?void 0:s.unencrypted_http_traffic,children:e("span",{className:"text-xs",children:"Unencrypted HTTP Traffic"})}),e(h,{bytes:s==null?void 0:s.weak_encryption,children:e("span",{className:"text-xs",children:"Weak Encryption"})})]})]})})]}),e("section",{className:"flex flex-col gap-4 bg-gray-50"})]})},B=()=>e(I,{children:c("main",{className:"flex-1 md:pr-64 lg:md:pr-80",children:[e(R,{}),e(k,{}),e(E,{})]})});export{B as default};
