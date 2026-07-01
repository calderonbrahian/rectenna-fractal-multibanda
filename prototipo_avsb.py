"""
PROTOTIPO (experimental) — "Escenario A vs B, lado a lado".

La imagen central del trabajo: el Sierpinski (A) es multibanda en GEOMETRÍA pero
solo se adapta en 1 de sus 7 bandas (exploratorio, sin cifra firme); la FLPDA Koch
(B) apunta a una sola fuente y la capta limpiamente (cuantitativo, P_DC firme,
≈546 mensajes/día). Canvas 60 fps. Cifras canónicas. NO es la app oficial.
"""

import streamlit as st
import streamlit.components.v1 as components

from configs.parametros import CANONICAL
from _proto_ui import poster_style

poster_style()

st.title(":material/compare: Escenario A vs B — por qué hay dos")
st.caption("Prototipo experimental — no forma parte de la aplicación oficial del trabajo.")
st.markdown(
    "A la izquierda, el **Sierpinski** intenta captar sus **7 bandas** urbanas: la energía "
    "**rebota en 6** y solo **1 se adapta** (5G-3,5 GHz). A la derecha, la **FLPDA Koch** "
    "apunta a la **torre de TV** y la capta limpio, con cifra firme. Por eso hay dos "
    "escenarios: uno explora, el otro cuantifica."
)
st.info(
    "**Pregunta que responde:** ¿por qué el trabajo necesita dos escenarios, uno exploratorio "
    "y otro cuantitativo?  ·  Prototipo **analítico**: S₁₁ (1/7 bandas), P_DC y los "
    "mensajes/día (= 86.400 s ÷ T_ciclo) salen del modelo canónico.",
    icon=":material/help:",
)

PDC = CANONICAL['p_dc_uW'] if 'p_dc_uW' in CANONICAL else CANONICAL['P_dc_uW']
GAIN_B = CANONICAL['gain_dBi']
MSG_B = 86400.0 / CANONICAL['T_ciclo_s']

HTML = r"""
<div style="position:relative;width:100%;font-family:'Segoe UI',system-ui,sans-serif;">
  <button id="ab_dl" title="Descargar imagen para póster / diapositiva" style="position:absolute;top:10px;right:12px;z-index:6;background:rgba(255,255,255,0.92);border:1px solid #CBD5E1;border-radius:8px;padding:5px 11px;font:600 12px 'Segoe UI';color:#0F172A;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,0.18);">⬇ PNG</button>
  <canvas id="ab" style="width:100%;height:580px;display:block;border-radius:12px;"></canvas>
</div>
<script>
(function(){
  const PDC=__PDC__,GB=__GB__,MSGB=__MSGB__;
  const cv=document.getElementById('ab'),ctx=cv.getContext('2d');
  {const _b=document.getElementById('ab_dl');if(_b)_b.addEventListener('click',function(){const a=document.createElement('a');a.download='escenario_a_vs_b.png';a.href=cv.toDataURL('image/png');a.click();});}
  let W=1180,H=580,dpr=Math.max(2,window.devicePixelRatio||1);
  function resize(){const w=cv.clientWidth||1180;W=w;H=580;cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
  window.addEventListener('resize',resize);resize();
  const C={tinta:'#0F172A',gris:'#64748B',azul:'#0EA5E9',verde:'#16A34A',verde2:'#22C55E',ambar:'#F59E0B',rojo:'#EF4444',viol:'#7C3AED'};
  const BANDS=[['GSM1800',0],['LTE2,0',0],['WiFi2,4',0],['5G2,6',0],['5G3,5',1],['5G4,9',0],['WiFi5,8',0]];
  let t=0,last=performance.now()/1000,meterB=0;
  function rr(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
  function sierp(cx,cy,s,d){function tri(x,y,sz,dd){if(dd===0){ctx.beginPath();ctx.moveTo(x,y-sz);ctx.lineTo(x-sz*0.87,y+sz*0.5);ctx.lineTo(x+sz*0.87,y+sz*0.5);ctx.closePath();ctx.fillStyle='rgba(96,165,250,0.5)';ctx.fill();ctx.strokeStyle='#3B82F6';ctx.lineWidth=1;ctx.stroke();return;}tri(x,y-sz*0.5,sz*0.5,dd-1);tri(x-sz*0.43,y+sz*0.25,sz*0.5,dd-1);tri(x+sz*0.43,y+sz*0.25,sz*0.5,dd-1);}tri(cx,cy,s,d);}
  function meter(x,y,w,h,frac,col,label,val){ctx.strokeStyle='#94A3B8';ctx.lineWidth=1.5;ctx.strokeRect(x,y,w,h);ctx.fillStyle=col;ctx.fillRect(x+2,y+h-2-(h-4)*Math.min(1,frac),w-4,(h-4)*Math.min(1,frac));ctx.fillStyle=C.gris;ctx.font='11px Segoe UI';ctx.textAlign='center';ctx.fillText(label,x+w/2,y+h+14);ctx.fillStyle=C.tinta;ctx.font='600 12px Segoe UI';ctx.fillText(val,x+w/2,y-6);}

  function panelA(x0,x1){const cx=(x0+x1)/2,cyAnt=300;
    ctx.fillStyle=C.tinta;ctx.font='700 15px Segoe UI';ctx.textAlign='center';ctx.fillText('Escenario A · Sierpinski',cx,40);
    ctx.fillStyle=C.gris;ctx.font='12px Segoe UI';ctx.fillText('multibanda · exploratorio',cx,58);
    const srcs=[['WiFi',x0+70,110,'#0EA5E9'],['LTE',x1-70,110,'#F59E0B'],['5G',cx,86,'#7C3AED']];
    for(const [nm,sx,sy,col] of srcs){ctx.fillStyle=col;ctx.font='600 12px Segoe UI';ctx.fillText('📶 '+nm,sx,sy-12);
      for(let k=0;k<3;k++){const r=((t*60+k*40)%120);ctx.strokeStyle=col+'66';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(sx,sy,r*0.4+6,0,6.3);ctx.stroke();}
      for(let k=0;k<5;k++){const ph=((t*0.5+k/5)%1);const reb=(k!==0);let f=reb?(ph<0.5?ph*2:(1-ph)*2):ph;const px=sx+f*(cx-sx),py=sy+f*(cyAnt-sy);ctx.fillStyle=reb?'rgba(239,68,68,0.8)':'rgba(34,197,94,0.9)';ctx.beginPath();ctx.arc(px,py,2.8,0,6.3);ctx.fill();}}
    sierp(cx,cyAnt,42,2);
    // 7 bandas explícitas
    const n=BANDS.length,bw=(x1-x0-40)/n,by=cyAnt+70;
    for(let i=0;i<n;i++){const bx=x0+20+i*bw,ok=BANDS[i][1];ctx.fillStyle=ok?'rgba(34,197,94,0.18)':'rgba(239,68,68,0.12)';ctx.strokeStyle=ok?C.verde:C.rojo;ctx.lineWidth=1.5;rr(bx+3,by,bw-6,30,5);ctx.fill();ctx.stroke();
      ctx.fillStyle=ok?C.verde:C.rojo;ctx.font='600 10px Segoe UI';ctx.textAlign='center';ctx.fillText((ok?'✓':'✗'),bx+bw/2,by+13);ctx.fillStyle=C.gris;ctx.font='9px Segoe UI';ctx.fillText(BANDS[i][0],bx+bw/2,by+25);}
    ctx.fillStyle=C.rojo;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText('S₁₁ < −10 dB en 1 de 7 bandas (5G-3,5)',cx,by+50);
    const fr=0.12+0.05*Math.abs(Math.sin(t*2));
    meter(cx-30,by+62,60,40,fr,C.ambar,'energía captada','cotas superiores');
    ctx.fillStyle=C.gris;ctx.font='11px Segoe UI';ctx.fillText('mensajes/día firmes: ≈ 0',cx,by+128);
  }
  function panelB(x0,x1){const cx=(x0+x1)/2,cyAnt=320,twx=cx,twy=104;
    ctx.fillStyle=C.tinta;ctx.font='700 15px Segoe UI';ctx.textAlign='center';ctx.fillText('Escenario B · FLPDA Koch',cx,40);
    ctx.fillStyle=C.gris;ctx.font='12px Segoe UI';ctx.fillText('dirigida · cuantitativo',cx,58);
    ctx.strokeStyle=C.viol;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(twx-12,twy+44);ctx.lineTo(twx,twy);ctx.lineTo(twx+12,twy+44);ctx.stroke();
    ctx.fillStyle=C.viol;ctx.font='600 12px Segoe UI';ctx.fillText('📡 Torre TDT',twx,twy-8);
    for(let k=0;k<3;k++){const r=((t*60+k*40)%120);ctx.strokeStyle='rgba(124,58,237,0.4)';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(twx,twy,r*0.5+6,0,6.3);ctx.stroke();}
    ctx.fillStyle='rgba(34,197,94,0.10)';ctx.beginPath();ctx.moveTo(cx,cyAnt);ctx.lineTo(twx-40,twy+50);ctx.lineTo(twx+40,twy+50);ctx.closePath();ctx.fill();
    ctx.strokeStyle=C.verde;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(cx,cyAnt);ctx.lineTo(cx,cyAnt+66);ctx.stroke();
    for(let i=0;i<6;i++){const yy=cyAnt+8+i*10,w=32-i*4;ctx.beginPath();ctx.moveTo(cx-w,yy);ctx.lineTo(cx+w,yy);ctx.stroke();}
    for(let k=0;k<7;k++){const ph=((t*0.45+k/7)%1);ctx.fillStyle='rgba(34,197,94,0.9)';ctx.beginPath();ctx.arc(twx+(cx-twx)*ph,(twy+50)+(cyAnt-(twy+50))*ph,2.8,0,6.3);ctx.fill();}
    ctx.fillStyle=C.verde;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText('S₁₁ < −10 dB en TODA la banda · G ≈ '+GB.toFixed(1)+' dBi',cx,cyAnt+90);
    meter(cx-30,cyAnt+104,60,40,meterB,C.verde2,'energía captada',PDC.toFixed(0)+' µW');
    ctx.fillStyle=C.verde;ctx.font='600 11px Segoe UI';ctx.fillText('mensajes/día firmes: ≈ '+Math.round(MSGB),cx,cyAnt+170);
  }
  function loop(now){now/=1000;let dt=Math.min(0.05,now-last);last=now;t+=dt;meterB+=(0.92-meterB)*Math.min(1,dt*0.8);
    ctx.clearRect(0,0,W,H);const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#F8FBFF');g.addColorStop(1,'#F4FAF6');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    panelA(0,W/2);panelB(W/2,W);
    ctx.strokeStyle='#CBD5E1';ctx.lineWidth=1.5;ctx.setLineDash([6,5]);ctx.beginPath();ctx.moveTo(W/2,70);ctx.lineTo(W/2,H-46);ctx.stroke();ctx.setLineDash([]);
    ctx.fillStyle=C.tinta;ctx.font='600 13px Segoe UI';ctx.textAlign='center';ctx.fillText('La geometría multibanda (A) no equivale a recolección multibanda. La captación firme la da una antena dirigida a una fuente fuerte (B).',W/2,H-16);
    requestAnimationFrame(loop);}
  requestAnimationFrame(loop);
})();
</script>
"""
for kk, vv in {"__PDC__": f"{PDC:.1f}", "__GB__": f"{GAIN_B:.2f}", "__MSGB__": f"{MSG_B:.1f}"}.items():
    HTML = HTML.replace(kk, vv)
components.html(HTML, height=600, scrolling=False)

st.caption(
    "A: Sierpinski it.3 sobre FR-4, S₁₁ < −10 dB en 1 de 7 bandas (5G-3,5 GHz, −16,4 dB) → "
    "exploratorio, sin cifra firme. B: FLPDA Koch, S₁₁ < −10 dB continuo, G ≈ 7,10 dBi, "
    "P_DC = 1.638 µW → ≈546 mensajes/día (= 86.400 s ÷ T_ciclo de 158,3 s). El Escenario A no "
    "fija una cifra firme. Cifras canónicas · §4.1, §4.2, §4.4."
)
st.success(
    "**¿Qué pregunta responde esta simulación?**  \nPor qué existen dos escenarios: A "
    "(Sierpinski) explora la multibanda pero solo se adapta en 1 de 7; B (FLPDA) apunta a "
    "una fuente fuerte y cuantifica la energía. Ser multibanda no equivale a recolectar."
)
