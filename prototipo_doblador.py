"""
PROTOTIPO (experimental) — "El doblador Greinacher en acción".

Muestra la rectificación semiciclo a semiciclo: cada diodo conduce en su turno,
C1 y C2 se cargan, el nodo X alcanza ~2·V_pico y la salida tiende a V_DC ≈
2·(V_pico − V_f). Incluye la curva I-V del diodo con el punto de operación en
vivo. Valores canónicos (V_DC ≈ 1.459 mV). NO es la app oficial.
"""

import streamlit as st
import streamlit.components.v1 as components

from configs.parametros import CANONICAL
from _proto_ui import poster_style

poster_style()

st.title(":material/bolt: El doblador Greinacher en acción")
st.caption("Prototipo experimental — no forma parte de la aplicación oficial del trabajo.")
st.markdown(
    "El rectificador es el corazón de la conversión RF→DC. Mira cómo, **semiciclo a "
    "semiciclo**, conduce un diodo distinto (lo confirma la **curva I-V** abajo): en el "
    "negativo se carga C1, en el positivo la tensión se **suma** (nodo X ≈ 2·V_pico) y "
    "carga C2, de modo que la salida tiende al **doble** del pico."
)
st.info(
    "**Pregunta que responde:** ¿cómo convierte el rectificador la señal de radio (alterna) "
    "en corriente continua?  ·  Prototipo **conceptual** en las formas de onda; el valor de "
    "**V_DC ≈ 1.459 mV es canónico**.",
    icon=":material/help:",
)

c1, c2 = st.columns([3, 2])
with c1:
    vel = st.slider("Velocidad de la animación", 0.2, 3.0, 1.0, 0.1)
with c2:
    show_help = st.toggle("Mostrar rótulos (C1/C2/D1/D2)", value=True)

V_DC = CANONICAL['V_dc_mV'] / 1000.0
V_F = 0.15
V_PK = V_DC / 2.0 + V_F

k1, k2, k3 = st.columns(3)
k1.metric("V_pico de la RF", f"{V_PK*1000:.0f} mV")
k2.metric("Caída por diodo V_f", f"{V_F*1000:.0f} mV")
k3.metric("V_DC ≈ 2·(V_pico − V_f)", f"{V_DC*1000:.0f} mV")

HTML = r"""
<div style="position:relative;width:100%;font-family:'Segoe UI',system-ui,sans-serif;">
  <button id="dv_dl" title="Descargar imagen para póster / diapositiva" style="position:absolute;top:10px;right:12px;z-index:6;background:rgba(255,255,255,0.92);border:1px solid #CBD5E1;border-radius:8px;padding:5px 11px;font:600 12px 'Segoe UI';color:#0F172A;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,0.18);">⬇ PNG</button>
  <canvas id="dv" style="width:100%;height:540px;display:block;border-radius:12px;"></canvas>
</div>
<script>
(function(){
  const VDC=__VDC__,VF=__VF__,VPK=__VPK__,VEL=__VEL__,HELP=__HELP__;
  const cv=document.getElementById('dv'),ctx=cv.getContext('2d');
  {const _b=document.getElementById('dv_dl');if(_b)_b.addEventListener('click',function(){const a=document.createElement('a');a.download='doblador_greinacher.png';a.href=cv.toDataURL('image/png');a.click();});}
  let W=1180,H=540,dpr=Math.max(2,window.devicePixelRatio||1);
  function resize(){const w=cv.clientWidth||1180;W=w;H=540;cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
  window.addEventListener('resize',resize);resize();
  const C={tinta:'#0F172A',gris:'#64748B',linea:'#475569',azul:'#0EA5E9',ambar:'#F59E0B',
           verde:'#16A34A',viol:'#7C3AED',rojo:'#EF4444'};
  const yTop=250,yGnd=400,xSrc=110,xC1=250,xX=430,xD2=560,xVo=690,xLoad=860;
  let t=0,last=performance.now()/1000,c1=0,vout=0;

  function rr(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
  function wire(p,col,wd){ctx.strokeStyle=col;ctx.lineWidth=wd||3;ctx.beginPath();ctx.moveTo(p[0][0],p[0][1]);for(let i=1;i<p.length;i++)ctx.lineTo(p[i][0],p[i][1]);ctx.stroke();}
  function plen(p){let L=0;for(let i=1;i<p.length;i++)L+=Math.hypot(p[i][0]-p[i-1][0],p[i][1]-p[i-1][1]);return L;}
  function pat(p,f){let L=plen(p)*f,a=0;for(let i=1;i<p.length;i++){const d=Math.hypot(p[i][0]-p[i-1][0],p[i][1]-p[i-1][1]);if(a+d>=L){const r=(L-a)/d;return [p[i-1][0]+r*(p[i][0]-p[i-1][0]),p[i-1][1]+r*(p[i][1]-p[i-1][1])];}a+=d;}return p[p.length-1];}
  function flow(p,col,ph,n){for(let k=0;k<(n||4);k++){const pt=pat(p,((ph+k/(n||4))%1));ctx.fillStyle=col;ctx.beginPath();ctx.arc(pt[0],pt[1],3.4,0,6.3);ctx.fill();}}
  function scope(x0,y0,w,h,fn,col,label){ctx.fillStyle='rgba(255,255,255,0.92)';ctx.strokeStyle='#CBD5E1';ctx.lineWidth=1;rr(x0,y0,w,h,8);ctx.fill();ctx.stroke();
    ctx.save();rr(x0+1,y0+1,w-2,h-2,7);ctx.clip();ctx.strokeStyle='rgba(148,163,184,0.3)';ctx.beginPath();ctx.moveTo(x0,y0+h/2);ctx.lineTo(x0+w,y0+h/2);ctx.stroke();
    ctx.strokeStyle=col;ctx.lineWidth=2;ctx.beginPath();for(let px=0;px<=w;px+=2){const v=fn(px/w);const py=y0+h/2-v*(h*0.4);if(px===0)ctx.moveTo(x0+px,py);else ctx.lineTo(x0+px,py);}ctx.stroke();ctx.restore();
    ctx.fillStyle=C.gris;ctx.font='11px Segoe UI';ctx.textAlign='left';ctx.fillText(label,x0+4,y0-5);}
  function capV(cx,cy,vertical,fill,col,label,vtxt){
    ctx.strokeStyle=col;ctx.lineWidth=4;
    if(vertical){ctx.beginPath();ctx.moveTo(cx-16,cy-3);ctx.lineTo(cx+16,cy-3);ctx.stroke();ctx.beginPath();ctx.moveTo(cx-16,cy+3);ctx.lineTo(cx+16,cy+3);ctx.stroke();}
    else{ctx.beginPath();ctx.moveTo(cx-3,cy-16);ctx.lineTo(cx-3,cy+16);ctx.stroke();ctx.beginPath();ctx.moveTo(cx+3,cy-16);ctx.lineTo(cx+3,cy+16);ctx.stroke();}
    const bw=10,bh=34,bx=cx+22,by=cy-17;ctx.strokeStyle='#94A3B8';ctx.lineWidth=1;ctx.strokeRect(bx,by,bw,bh);ctx.fillStyle=col;ctx.fillRect(bx,by+bh-bh*fill,bw,bh*fill);
    if(HELP){ctx.fillStyle=C.gris;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText(label,cx,vertical?cy+30:cy-24);}
    ctx.fillStyle=col;ctx.font='10px Segoe UI';ctx.textAlign='center';ctx.fillText(vtxt,cx+34,cy);}
  function diode(cx,cy,dir,active){ctx.save();ctx.translate(cx,cy);if(dir==='down')ctx.rotate(Math.PI/2);const col=active?C.ambar:'#9CA3AF';if(active){ctx.shadowColor=C.ambar;ctx.shadowBlur=16;}ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(-12,-11);ctx.lineTo(-12,11);ctx.lineTo(10,0);ctx.closePath();ctx.fill();ctx.strokeStyle=col;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(10,-12);ctx.lineTo(10,12);ctx.stroke();ctx.shadowBlur=0;ctx.restore();}

  function ivCurve(vin){   // mini curva I-V del diodo, con punto de operación
    const x0=40,y0=400,w=300,h=120,Is=5e-6,n=1.05,Vt=0.02585;
    ctx.fillStyle='rgba(255,255,255,0.95)';ctx.strokeStyle='#CBD5E1';ctx.lineWidth=1;rr(x0,y0,w,h,8);ctx.fill();ctx.stroke();
    const vx=v=>x0+ (v+0.2)/(0.45)*w;            // V de -0.2 a 0.25
    const iy=i=>y0+h-10-Math.min(1,Math.max(0,(i)/0.002))*(h-20);  // I 0..2mA
    // ejes
    ctx.strokeStyle='rgba(148,163,184,0.4)';ctx.beginPath();ctx.moveTo(vx(0),y0+8);ctx.lineTo(vx(0),y0+h-8);ctx.stroke();
    ctx.beginPath();ctx.moveTo(x0+6,iy(0));ctx.lineTo(x0+w-6,iy(0));ctx.stroke();
    // curva
    ctx.strokeStyle=C.azul;ctx.lineWidth=2;ctx.beginPath();let first=true;
    for(let v=-0.2;v<=0.25;v+=0.004){const I=Is*(Math.exp(v/(n*Vt))-1);const X=vx(v),Yy=iy(I);if(first){ctx.moveTo(X,Yy);first=false;}else ctx.lineTo(X,Yy);}ctx.stroke();
    // punto de operación: V_D ≈ vin (sobre el diodo que conduce)
    const vd=Math.max(-0.2,Math.min(0.25,vin));const I=Is*(Math.exp(vd/(n*Vt))-1);
    const cond=vd>VF*0.6;ctx.fillStyle=cond?C.verde:'#9CA3AF';if(cond){ctx.shadowColor=C.verde;ctx.shadowBlur=12;}
    ctx.beginPath();ctx.arc(vx(vd),iy(I),6,0,6.3);ctx.fill();ctx.shadowBlur=0;
    ctx.fillStyle=C.gris;ctx.font='11px Segoe UI';ctx.textAlign='left';ctx.fillText('Curva I-V del diodo (Shockley)',x0+6,y0-6);
    ctx.fillText(cond?'conduce ▶':'bloquea ✕',x0+w-70,y0+16);
    ctx.fillStyle=C.gris;ctx.font='10px Segoe UI';ctx.fillText('V_D',vx(0.22),iy(0)+12);ctx.fillText('I_D',vx(0)+4,y0+16);}

  function draw(){
    ctx.clearRect(0,0,W,H);const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#F8FBFF');g.addColorStop(1,'#F1F8F4');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    const phase=t*2*Math.PI*0.55,vin=VPK*Math.sin(phase),pos=vin>=0,xnode=vin+c1;

    // badge de semiciclo
    ctx.textAlign='center';ctx.fillStyle=pos?'rgba(34,197,94,0.15)':'rgba(14,165,233,0.15)';rr(W/2-220,18,440,30,8);ctx.fill();
    ctx.fillStyle=pos?C.verde:C.azul;ctx.font='600 14px Segoe UI';
    ctx.fillText(pos?'Semiciclo +  ·  D2 conduce  ·  carga C2  ·  X ≈ 2·V_pico':'Semiciclo −  ·  D1 conduce  ·  carga C1',W/2,38);

    // cables
    wire([[xSrc,yTop],[xC1-18,yTop]],C.linea);wire([[xC1+18,yTop],[xX,yTop]],C.linea);
    wire([[xX,yTop],[xD2-14,yTop]],pos?C.ambar:C.linea, pos?4:3);wire([[xD2+12,yTop],[xVo,yTop]],C.linea);wire([[xVo,yTop],[xLoad,yTop]],C.linea);
    wire([[xX,yTop],[xX,yGnd-100]],C.linea);wire([[xSrc,yTop],[xSrc,yGnd]],C.linea);wire([[xSrc,yGnd],[xLoad,yGnd]],C.linea);
    wire([[xX,yGnd-60],[xX,yGnd]],!pos?C.ambar:C.linea,!pos?4:3);wire([[xVo,yTop],[xVo,yGnd-60]],C.linea);wire([[xVo,yGnd-30],[xVo,yGnd]],C.linea);wire([[xLoad,yTop],[xLoad,yGnd]],C.linea);

    // fuente
    ctx.strokeStyle=C.azul;ctx.lineWidth=2.5;ctx.beginPath();ctx.arc(xSrc,(yTop+yGnd)/2,22,0,6.3);ctx.stroke();
    ctx.beginPath();for(let a=-14;a<=14;a++){const xx=xSrc+a,yy=(yTop+yGnd)/2-9*Math.sin(a/14*Math.PI);if(a===-14)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy);}ctx.stroke();
    ctx.fillStyle=pos?C.rojo:C.azul;ctx.font='600 13px Segoe UI';ctx.textAlign='center';ctx.fillText(pos?'+':'−',xSrc,(yTop+yGnd)/2-30);
    if(HELP){ctx.fillStyle=C.gris;ctx.font='12px Segoe UI';ctx.fillText('RF in',xSrc,yGnd+18);}

    capV(xC1,yTop,false,Math.min(1,c1/VPK),'#0369A1','C1',(c1*1000).toFixed(0)+' mV');
    diode(xX,(yGnd-100+yGnd-60)/2,'down',!pos);if(HELP){ctx.fillStyle=C.gris;ctx.font='600 12px Segoe UI';ctx.fillText('D1',xX-22,yGnd-78);}
    diode(xD2,yTop,'right',pos);if(HELP){ctx.fillStyle=C.gris;ctx.font='600 12px Segoe UI';ctx.fillText('D2',xD2,yTop-22);}
    capV(xVo,yGnd-45,true,Math.min(1,vout/VDC),C.viol,'C2',(vout*1000).toFixed(0)+' mV');
    // nodo X con su tensión
    ctx.fillStyle=C.tinta;ctx.beginPath();ctx.arc(xX,yTop,4,0,6.3);ctx.fill();
    ctx.fillStyle=pos?C.verde:C.tinta;ctx.font='600 12px Segoe UI';ctx.fillText('X = '+(xnode*1000).toFixed(0)+' mV',xX,yTop-14);
    ctx.strokeStyle='#94A3B8';ctx.lineWidth=2;ctx.strokeRect(xLoad-8,(yTop+yGnd)/2-22,16,44);if(HELP){ctx.fillStyle=C.gris;ctx.font='12px Segoe UI';ctx.fillText('R_L',xLoad+22,(yTop+yGnd)/2);}
    ctx.fillStyle=C.verde;ctx.beginPath();ctx.arc(xVo,yTop,4,0,6.3);ctx.fill();ctx.fillStyle=C.verde;ctx.font='600 12px Segoe UI';ctx.fillText('V_DC',xVo,yTop-12);

    const ph=(t*0.8)%1;
    if(pos)flow([[xX,yTop],[xD2,yTop],[xVo,yTop],[xVo,yGnd-45]],C.ambar,ph,5);
    else flow([[xSrc,yTop],[xC1,yTop],[xX,yTop],[xX,yGnd-80],[xX,yGnd]],C.ambar,ph,5);

    scope(40,60,300,120,u=>Math.sin(u*6.283*2-phase),C.azul,'Entrada: RF alterna (AC)');
    scope(W-340,60,300,120,u=>(vout/VDC)*0.9-0.45+0.03*Math.sin(u*60),C.viol,'Salida: V_DC (×2)');
    ivCurve(vin);

    ctx.textAlign='left';ctx.font='13px Segoe UI';
    const items=[['V_in',(vin>=0?'+':'')+(vin*1000).toFixed(0)+' mV'],['V_DC',(vout*1000).toFixed(0)+' mV'],['Objetivo','2(V_pk−V_f)='+(VDC*1000).toFixed(0)+' mV']];
    let x=W-360,y=H-20;for(const [k,v] of items){ctx.fillStyle=C.gris;ctx.fillText(k+': ',x,y);const kw=ctx.measureText(k+': ').width;ctx.fillStyle=C.tinta;ctx.font='600 13px Segoe UI';ctx.fillText(v,x+kw,y);ctx.font='13px Segoe UI';x+=kw+ctx.measureText(v).width+22;}
  }
  function loop(now){now/=1000;let dt=Math.min(0.05,now-last);last=now;t+=dt*VEL;
    const phase=t*2*Math.PI*0.55,vin=VPK*Math.sin(phase),pos=vin>=0;
    if(!pos)c1+=(VPK-c1)*Math.min(1,dt*VEL*4);
    if(pos&&(vin+c1)>vout+VF)vout+=(VDC-vout)*Math.min(1,dt*VEL*1.2);
    draw();requestAnimationFrame(loop);}
  requestAnimationFrame(loop);
})();
</script>
"""
for kk, vv in {"__VDC__": f"{V_DC:.4f}", "__VF__": f"{V_F:.4f}", "__VPK__": f"{V_PK:.4f}",
               "__VEL__": f"{vel:.3f}", "__HELP__": "true" if show_help else "false"}.items():
    HTML = HTML.replace(kk, vv)
components.html(HTML, height=560, scrolling=False)

st.caption(
    "Doblador Greinacher de media onda con dos diodos Schottky SMS7630. La curva I-V "
    "confirma que el diodo solo conduce en directo (punto verde) y bloquea en inverso. "
    "En régimen permanente, V_DC ≈ 2·(V_pico − V_f) ≈ 1.459 mV (canónico, §3.5, Apéndice E.8)."
)
st.success(
    "**¿Qué pregunta responde esta simulación?**  \nCómo se convierte la RF en corriente "
    "continua: por qué cada diodo conduce en su semiciclo y por qué la tensión de salida "
    "termina siendo el doble del pico."
)
