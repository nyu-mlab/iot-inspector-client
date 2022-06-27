const r=a=>a>=1e6?`${parseFloat(a/1e6).toFixed(2)} MB`:a>=1e3?`${parseFloat(a/1e3).toFixed(2)} KB`:`${parseFloat(a).toFixed(2)} BYTES`;export{r as d};
