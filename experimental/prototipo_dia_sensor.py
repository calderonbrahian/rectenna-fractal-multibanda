import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""
PROTOTIPO (experimental) — "Cómo funciona la rectena" (ilustración animada a 60 fps).

Escena de canvas: la torre emite ondas, la antena capta (parte se refleja), el
rectificador y el PMIC convierten (parte se pierde como calor), el supercondensador
se carga y, al llegar al umbral, el nodo IoT envía un mensaje LoRa al gateway, que
queda registrado. Valores canónicos del proyecto. NO es la app oficial.
"""

import math
import streamlit as st
import streamlit.components.v1 as components

from configs.parametros import CANONICAL
from _proto_ui import poster_style

poster_style()

LORA = {
    "SF7 · rápido":   47.0,
    "SF9 · medio":    110.0,
    "SF12 · alcance": CANONICAL['E_ciclo_mJ'],
}

st.title(":material/sensors: Cómo funciona la rectena — ilustración animada")
st.caption("Prototipo experimental — no forma parte de la aplicación oficial del trabajo.")
st.markdown(
    "Sigue la energía de izquierda a derecha: la **torre** emite ondas, la **antena** las "
    "capta (parte **se refleja**), el **rectificador** y el **PMIC** convierten (parte **se "
    "pierde como calor**), el **supercondensador** se carga y, al llenarse, el **nodo IoT** "
    "envía un mensaje al **gateway**. Mueve los controles."
)
st.info(
    "**Pregunta que responde:** ¿qué ocurre con la energía de radio después de que la "
    "antena la capta?  ·  Prototipo **conceptual** (ilustra el flujo; las pérdidas y "
    "las ondas son representativas, no un modelo físico).",
    icon=":material/help:",
)

c1, c2 = st.columns([3, 2])
with c1:
    dist = st.slider("Distancia del sensor a la torre TDT [m]", 50, 600, 100, 10)
with c2:
    sf = st.segmented_control("Perfil de radio", options=list(LORA.keys()),
                              default="SF12 · alcance") or "SF12 · alcance"

E_ciclo_mJ = LORA[sf]
R_load = CANONICAL['R_load_ohm']
P_DC = CANONICAL['p_dc_uW'] * (100.0 / dist) ** 2 if 'p_dc_uW' in CANONICAL else \
    CANONICAL['P_dc_uW'] * (100.0 / dist) ** 2
V_dc = math.sqrt(max(P_DC * 1e-6 * R_load, 0.0))
cold_ok = V_dc >= CANONICAL['V_cs_mV'] / 1000.0
T_ciclo = (E_ciclo_mJ * 1e-3) / max(P_DC * 1e-6, 1e-15)
msg_dia = (86400.0 / T_ciclo) if cold_ok else 0.0
P_in_dBm = CANONICAL['P_in_dBm'] - 20.0 * math.log10(dist / 100.0)
amp = math.sqrt(min(1.0, P_DC / (CANONICAL['P_dc_uW'] * 4.0)))

k1, k2, k3, k4 = st.columns(4)
k1.metric("P_in en la antena", f"{P_in_dBm:+.1f} dBm")
k2.metric("Potencia útil P_DC", f"{P_DC:,.0f} µW".replace(",", " ") if P_DC >= 1
          else f"{P_DC*1000:.0f} nW")
k3.metric("Un mensaje cada", f"{T_ciclo/60:.1f} min" if cold_ok else "—")
k4.metric("Mensajes al día", f"≈ {msg_dia:,.0f}".replace(",", " ") if cold_ok else "0")

HTML = r"""
<div style="position:relative;width:100%;font-family:'Segoe UI',system-ui,sans-serif;">
  <button id="cv_dl" title="Descargar imagen para póster / diapositiva" style="position:absolute;top:10px;right:12px;z-index:6;background:rgba(255,255,255,0.92);border:1px solid #CBD5E1;border-radius:8px;padding:5px 11px;font:600 12px 'Segoe UI';color:#0F172A;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,0.18);">⬇ PNG</button>
  <canvas id="cv" style="width:100%;height:560px;display:block;border-radius:12px;"></canvas>
</div>
<script>
(function(){
  const PDC=__PDC__, TCICLO=__TCICLO__, COLD=__COLD__, DIST=__DIST__, PIN=__PIN__,
        AMP=__AMP__, SF="__SF__", VMAX=3.3;
  const cv=document.getElementById('cv'), ctx=cv.getContext('2d');
  {const _b=document.getElementById('cv_dl');if(_b)_b.addEventListener('click',function(){const a=document.createElement('a');a.download='rectena_flujo.png';a.href=cv.toDataURL('image/png');a.click();});}
  let W=1180,H=560,dpr=Math.max(2,window.devicePixelRatio||1);
  function resize(){const w=cv.clientWidth||1180;W=w;H=560;cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
  window.addEventListener('resize',resize);resize();
  const C={azul:'#0369A1',verde:'#059669',verde2:'#22C55E',ambar:'#FBBF24',ambar2:'#F59E0B',
           viol:'#7C3AED',viol2:'#A78BFA',rojo:'#EF4444',gris:'#64748B',linea:'#94A3B8',tinta:'#0F172A'};
  const CYCLE=4.0;
  let t=0,last=performance.now()/1000,charge=0,msgs=0,clock=0,tx=-1,log=[];
  let parts=[];for(let i=0;i<22;i++)parts.push(Math.random());
  function fmt(n){return Math.round(n).toLocaleString('es').replace(/,/g,' ');}
  function xs(){const m=70,span=W-2*m;return [0.06,0.24,0.42,0.59,0.76,0.93].map(f=>m+f*span);}
  const Y=300, SCY=150, SCH=84, SCW=118;

  function roundRect(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
  function scope(cx,fn,col,label){
    const x0=cx-SCW/2,y0=SCY;ctx.fillStyle='rgba(255,255,255,0.92)';ctx.strokeStyle='#CBD5E1';ctx.lineWidth=1;roundRect(x0,y0,SCW,SCH,8);ctx.fill();ctx.stroke();
    ctx.save();ctx.beginPath();ctx.rect(x0+1,y0+1,SCW-2,SCH-2);ctx.clip();
    ctx.strokeStyle='rgba(148,163,184,0.25)';ctx.beginPath();ctx.moveTo(x0,y0+SCH/2);ctx.lineTo(x0+SCW,y0+SCH/2);ctx.stroke();
    ctx.strokeStyle=col;ctx.lineWidth=2;ctx.beginPath();const mid=y0+SCH/2,A=SCH*0.34;
    for(let px=0;px<=SCW;px+=2){const v=fn(px/SCW);const py=mid-v*A;if(px===0)ctx.moveTo(x0+px,py);else ctx.lineTo(x0+px,py);}ctx.stroke();ctx.restore();
    ctx.fillStyle=C.gris;ctx.font='11px Segoe UI';ctx.textAlign='center';ctx.fillText(label,cx,y0-6);
  }
  function stageIcon(cx,label){ctx.fillStyle=C.tinta;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText(label,cx,Y+62);}
  function heat(cx,pctLost,lbl){   // partículas rojas de pérdida cayendo
    const n=Math.max(2,Math.round(pctLost*0.5));
    for(let k=0;k<n;k++){const ph=((t*0.7+k/n)%1);const yy=Y+22+ph*70;const op=1-ph;
      ctx.fillStyle='rgba(239,68,68,'+(0.2+0.55*op).toFixed(2)+')';ctx.beginPath();ctx.arc(cx+(k-n/2)*5,yy,2.6,0,6.3);ctx.fill();}
    ctx.fillStyle=C.rojo;ctx.font='10px Segoe UI';ctx.textAlign='center';ctx.fillText('−'+lbl+' (calor)',cx,Y+98);
  }

  function draw(){
    ctx.clearRect(0,0,W,H);
    const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#EAF6FF');g.addColorStop(1,'#F4FBFF');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    ctx.fillStyle='rgba(220,252,231,0.7)';ctx.fillRect(0,Y+78,W,H-(Y+78));
    const cx=xs();

    // cable + partículas
    ctx.strokeStyle=C.linea;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(cx[1],Y);ctx.lineTo(cx[5],Y);ctx.stroke();
    if(COLD)for(let i=0;i<parts.length;i++){const px=cx[1]+parts[i]*(cx[5]-cx[1]);ctx.fillStyle=C.ambar;ctx.beginPath();ctx.arc(px,Y,3.2,0,7);ctx.fill();}

    drawTower(cx[0]); drawGauge(cx[0],Y+150,AMP,'campo RF');
    // onda incidente torre→antena + reflexión (parte rebota)
    for(let k=0;k<5;k++){const ph=((t*0.4+k/5)%1);
      ctx.fillStyle='rgba(251,191,36,0.85)';ctx.beginPath();ctx.arc(cx[0]+ph*(cx[1]-cx[0]),3.9*0+ (3.9*0)+ (110+30)+ph*(Y-140),2.6,0,6.3);ctx.fill();}
    const refl=Math.max(0.08,1-AMP);
    for(let k=0;k<Math.round(refl*5);k++){const ph=((t*0.5+k/5)%1);
      ctx.fillStyle='rgba(239,68,68,0.7)';ctx.beginPath();ctx.arc(cx[1]-ph*60,Y-ph*70,2.4,0,6.3);ctx.fill();}

    drawAntenna(cx[1]); scope(cx[1],u=>AMP*Math.sin(u*6.283*3 - t*6.0),'#38BDF8','RF captada (AC)'); stageIcon(cx[1],'Antena');
    drawDiode(cx[2]); scope(cx[2],u=>AMP*(1.6*Math.abs(Math.sin(u*6.283*3 - t*6.0))-0.5),C.ambar2,'rectificada'); stageIcon(cx[2],'Rectificador');
    if(COLD) heat(cx[2],14,'14 %');
    drawChip(cx[3],'PMIC'); scope(cx[3],u=>0.55+0.04*Math.sin(u*6.283*8 - t*10),C.verde,'DC estable'); stageIcon(cx[3],'Filtro / PMIC');
    if(COLD) heat(cx[3],12,'12 %');
    drawSupercap(cx[4],charge); stageIcon(cx[4],'Supercondensador');
    drawNode(cx[5]); drawGateway(W-46);
    if(tx>=0){const pr=Math.min(1,tx/0.9);const x=cx[5]+pr*((W-46)-cx[5]);const y=Y-10-80*Math.sin(pr*Math.PI);ctx.font='22px Segoe UI';ctx.textAlign='center';ctx.fillText('📨',x,y);}

    msgPanel();
    readouts();
    if(!COLD){ctx.fillStyle='rgba(15,23,42,0.04)';ctx.fillRect(0,0,W,H);ctx.fillStyle=C.gris;ctx.font='600 16px Segoe UI';ctx.textAlign='center';
      ctx.fillText('El sensor no recibe energía suficiente para arrancar — acércalo a la torre',W/2,Y+120);}
  }
  function drawTower(cx){const top=110,base=Y+60;
    for(let k=0;k<4;k++){const r=((t*70+k*60)%240);ctx.strokeStyle='rgba(2,132,199,'+Math.max(0.04,0.4*(1-r/240)).toFixed(3)+')';ctx.lineWidth=2;ctx.beginPath();ctx.arc(cx,top+30,r,0,6.283);ctx.stroke();}
    ctx.strokeStyle=C.azul;ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(cx,top);ctx.lineTo(cx-16,base);ctx.moveTo(cx,top);ctx.lineTo(cx+16,base);ctx.stroke();ctx.lineWidth=2;
    for(let i=1;i<=5;i++){const yy=top+(base-top)*i/6,w=4+i*2.2;ctx.beginPath();ctx.moveTo(cx-w,yy);ctx.lineTo(cx+w,yy);ctx.stroke();}
    if(Math.floor(t*2)%2===0){ctx.fillStyle=C.rojo;ctx.beginPath();ctx.arc(cx,top-4,5,0,6.283);ctx.fill();}
    ctx.fillStyle=C.azul;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText('📡 Torre TDT',cx,base+22);}
  function drawAntenna(cx){ctx.strokeStyle=C.azul;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(cx,Y-2);ctx.lineTo(cx,Y+40);ctx.stroke();
    for(let i=0;i<5;i++){const yy=Y-2-i*7,w=22-i*4;ctx.beginPath();ctx.moveTo(cx-w,yy);ctx.lineTo(cx+w,yy);ctx.stroke();}}
  function drawDiode(cx){ctx.fillStyle=C.ambar2;ctx.strokeStyle=C.ambar2;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(cx-14,Y-12);ctx.lineTo(cx-14,Y+12);ctx.lineTo(cx+10,Y);ctx.closePath();ctx.fill();ctx.beginPath();ctx.moveTo(cx+10,Y-13);ctx.lineTo(cx+10,Y+13);ctx.stroke();}
  function drawChip(cx,txt){ctx.fillStyle='#0F172A';roundRect(cx-22,Y-18,44,36,5);ctx.fill();for(let i=0;i<4;i++){ctx.fillRect(cx-27,Y-12+i*9,5,4);ctx.fillRect(cx+22,Y-12+i*9,5,4);}ctx.fillStyle='#E2E8F0';ctx.font='9px Segoe UI';ctx.textAlign='center';ctx.fillText(txt,cx,Y+3);}
  function drawSupercap(cx,ch){ctx.strokeStyle=C.viol;ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(cx-26,Y-26);ctx.lineTo(cx-26,Y+26);ctx.stroke();ctx.beginPath();ctx.moveTo(cx+26,Y-26);ctx.lineTo(cx+26,Y+26);ctx.stroke();ctx.beginPath();ctx.moveTo(cx-40,Y);ctx.lineTo(cx-26,Y);ctx.moveTo(cx+26,Y);ctx.lineTo(cx+40,Y);ctx.stroke();
    const bx=cx-12,bw=24,by0=Y+44,by1=Y-40;ctx.strokeStyle='#334155';ctx.lineWidth=1.5;ctx.strokeRect(bx,by1,bw,by0-by1);const fh=(by0-by1)*ch;ctx.fillStyle=ch>0.88?C.verde:C.viol2;ctx.fillRect(bx,by0-fh,bw,fh);
    ctx.fillStyle=C.viol;ctx.font='600 11px Segoe UI';ctx.textAlign='center';ctx.fillText((VMAX*Math.sqrt(Math.max(0,ch))).toFixed(2)+' V',cx,by1-6);}
  function drawNode(cx){const glow=(tx>=0&&tx<0.25);ctx.fillStyle=glow?C.verde2:'#10B981';if(glow){ctx.shadowColor=C.verde2;ctx.shadowBlur=22;}roundRect(cx-22,Y-18,44,36,6);ctx.fill();ctx.shadowBlur=0;ctx.fillStyle='#fff';ctx.font='16px Segoe UI';ctx.textAlign='center';ctx.fillText('📟',cx,Y+5);ctx.fillStyle=C.verde;ctx.font='600 12px Segoe UI';ctx.fillText('Nodo IoT',cx,Y+62);}
  function drawGateway(cx){ctx.fillStyle='rgba(124,58,237,0.12)';ctx.strokeStyle=C.viol;ctx.lineWidth=2;roundRect(cx-26,Y-6,52,60,5);ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(cx,Y-6);ctx.lineTo(cx,Y-44);ctx.stroke();ctx.fillStyle=C.viol2;ctx.beginPath();ctx.arc(cx,Y-46,6,0,6.283);ctx.fill();ctx.fillStyle=C.viol;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText('🛰 Gateway',cx,Y+70);
    // nube
    ctx.fillStyle='rgba(124,58,237,0.10)';ctx.beginPath();ctx.arc(cx-8,Y-70,9,0,6.3);ctx.arc(cx+4,Y-74,11,0,6.3);ctx.arc(cx+16,Y-70,9,0,6.3);ctx.fill();ctx.fillStyle=C.viol;ctx.font='9px Segoe UI';ctx.fillText('☁ datos',cx+2,Y-67);}
  function drawGauge(cx,cy,val,label){const r=30;ctx.strokeStyle='#CBD5E1';ctx.lineWidth=6;ctx.beginPath();ctx.arc(cx,cy,r,Math.PI,2*Math.PI);ctx.stroke();
    ctx.strokeStyle=val>0.5?C.verde:(val>0.2?C.ambar2:C.rojo);ctx.beginPath();ctx.arc(cx,cy,r,Math.PI,Math.PI+Math.PI*Math.min(1,val));ctx.stroke();
    const a=Math.PI+Math.PI*Math.min(1,val);ctx.strokeStyle=C.tinta;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(cx+r*0.8*Math.cos(a),cy+r*0.8*Math.sin(a));ctx.stroke();
    ctx.fillStyle=C.gris;ctx.font='10px Segoe UI';ctx.textAlign='center';ctx.fillText(label,cx,cy+16);}
  function msgPanel(){
    const x=W-250,y=44,w=210,h=92;ctx.fillStyle='rgba(255,255,255,0.9)';ctx.strokeStyle='#CBD5E1';ctx.lineWidth=1;roundRect(x,y,w,h,8);ctx.fill();ctx.stroke();
    ctx.fillStyle=C.tinta;ctx.font='600 12px Segoe UI';ctx.textAlign='left';ctx.fillText('🛰 Mensajes recibidos',x+10,y+18);
    ctx.font='11px Segoe UI';ctx.fillStyle=C.gris;
    const lines=log.slice(-3);for(let i=0;i<lines.length;i++){ctx.fillText('#'+lines[i].n+' · t='+lines[i].clk.toFixed(1)+' min',x+10,y+38+i*16);}
    if(lines.length===0)ctx.fillText('(esperando el primero…)',x+10,y+38);
  }
  function readouts(){const y=H-22;ctx.textAlign='left';ctx.font='13px Segoe UI';
    const items=[['P_in',(PIN>=0?'+':'')+PIN.toFixed(1)+' dBm'],['P_DC',PDC>=1?fmt(PDC)+' µW':Math.round(PDC*1000)+' nW'],['Mensajes',msgs.toString()],['Tiempo',(clock/60).toFixed(1)+' min'],['Cadencia real',COLD?(TCICLO/60).toFixed(1)+' min/msg':'no arranca']];
    let x=24;for(const [k,v] of items){ctx.fillStyle=C.gris;ctx.fillText(k+': ',x,y);const kw=ctx.measureText(k+': ').width;ctx.fillStyle=C.tinta;ctx.font='600 13px Segoe UI';ctx.fillText(v,x+kw,y);ctx.font='13px Segoe UI';x+=kw+ctx.measureText(v).width+30;}}

  function loop(now){now/=1000;let dt=Math.min(0.05,now-last);last=now;t+=dt;
    if(COLD){charge+=dt/CYCLE;if(charge>=1){charge-=1;msgs++;tx=0;clock+=0;log.push({n:msgs,clk:clock/60});}clock+=dt/CYCLE*TCICLO;if(tx>=0){tx+=dt;if(tx>0.95)tx=-1;}for(let i=0;i<parts.length;i++){parts[i]+=dt*0.18;if(parts[i]>1)parts[i]-=1;}}
    draw();requestAnimationFrame(loop);}
  requestAnimationFrame(loop);
})();
</script>
"""
for kk, vv in {"__PDC__": f"{P_DC:.4f}", "__TCICLO__": f"{T_ciclo:.4f}",
               "__COLD__": "true" if cold_ok else "false", "__DIST__": f"{dist}",
               "__PIN__": f"{P_in_dBm:.3f}", "__AMP__": f"{max(0.12, amp):.4f}",
               "__SF__": sf}.items():
    HTML = HTML.replace(kk, vv)
components.html(HTML, height=580, scrolling=False)

st.caption(
    "Las señales (AC, rectificada, DC) son ilustrativas; los números (P_in, P_DC, cadencia) "
    "y la física 1/d² de Friis son canónicos. El calor rojo es una **representación "
    "conceptual** de las pérdidas (no un modelo térmico); el **rebote** en la antena ilustra "
    "la **desadaptación de impedancias** (S₁₁/η_mm), no una simulación electromagnética. El "
    "tiempo está comprimido."
)
st.success(
    "**¿Qué pregunta responde esta simulación?**  \nQué ocurre con la energía de radio "
    "después de capturarla: cómo recorre la cadena RF→DC, se almacena y se gasta en cada "
    "mensaje (y dónde se pierde más, en el rectificador y el PMIC)."
)
