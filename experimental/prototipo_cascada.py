import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
"""
PROTOTIPO (experimental) — "La cascada de energía".

Arriba, el viaje de la señal por el aire en dB (EIRP → FSPL → corrección urbana →
ganancia → P_in), donde el grueso se pierde en el espacio libre. Abajo, el río de
energía que se estrecha al convertirse (P_in × η_mm × η_IMN × PCE × η_PMIC = P_DC),
con el cuello de botella en PCE y PMIC. Canvas 60 fps. Cifras canónicas. NO es la
app oficial.
"""

import streamlit as st
import streamlit.components.v1 as components

from configs.parametros import CANONICAL
from _proto_ui import poster_style

poster_style()

st.title(":material/water_drop: La cascada de energía — de la torre al nodo")
st.caption("Prototipo experimental — no forma parte de la aplicación oficial del trabajo.")
st.markdown(
    "El resultado de referencia (P_DC ≈ 1.638 µW) es lo que **queda** tras un largo viaje. "
    "Arriba, la señal cae con la distancia (el grueso se pierde en el aire) y se recupera "
    "con la antena. Abajo, el río de energía **se estrecha** en cada conversión: el "
    "**cuello de botella** está en la rectificación (PCE) y la gestión (PMIC)."
)
st.info(
    "**Pregunta que responde:** ¿dónde se pierde la energía entre la torre y el nodo, y "
    "cuánta llega útil?  ·  Prototipo **analítico**: todas las cifras (dB, η, µW) son "
    "canónicas.",
    icon=":material/help:",
)
st.markdown(
    "> *La eficiencia total es el **producto** de múltiples eficiencias parciales: basta con "
    "que una etapa rinda poco para que caiga todo el sistema.*"
)

EIRP = 70.0
FSPL = CANONICAL['FSPL_dB']
URB = CANONICAL['L_urb_dB']
G = CANONICAL['gain_dBi']
P_in_uW = CANONICAL['P_in_mW'] * 1000.0
chain = [("η_mm", CANONICAL['eta_mm']), ("η_IMN", CANONICAL['eta_imn']),
         ("PCE", CANONICAL['PCE']), ("η_PMIC", CANONICAL['eta_pmic'])]
p = P_in_uW
river = []
for name, f in chain:
    p2 = p * f
    river.append((name, f, p - p2, p2))
    p = p2
P_DC_uW = p
eta_op = P_DC_uW / P_in_uW * 100.0
lost_total = P_in_uW - P_DC_uW
msg_dia = 86400.0 / CANONICAL['T_ciclo_s']

k1, k2, k3 = st.columns(3)
k1.metric("Entra a la antena (P_in)", f"{P_in_uW:,.0f} µW".replace(",", " "))
k2.metric("Sale útil (P_DC)", f"{P_DC_uW:,.0f} µW".replace(",", " "))
k3.metric("Se conserva", f"{eta_op:.1f} % de P_in")

stair = [("EIRP", EIRP, None), ("−FSPL", EIRP - FSPL, -FSPL),
         ("−urbano", EIRP - FSPL - URB, -URB), ("+ganancia", EIRP - FSPL - URB + G, +G)]
stair_js = "[" + ",".join("{l:'%s',lv:%.2f,d:%s}" % (l, lv, ("null" if d is None else f"{d:.2f}"))
                          for l, lv, d in stair) + "]"
river_js = "[" + ",".join("{n:'%s',f:%.4f,lost:%.0f,rem:%.0f,pct:%.1f}" %
                          (n, f, lost, rem, rem / P_in_uW * 100.0) for n, f, lost, rem in river) + "]"

HTML = r"""
<div style="position:relative;width:100%;font-family:'Segoe UI',system-ui,sans-serif;">
  <button id="cc_dl" title="Descargar imagen para póster / diapositiva" style="position:absolute;top:10px;right:12px;z-index:6;background:rgba(255,255,255,0.92);border:1px solid #CBD5E1;border-radius:8px;padding:5px 11px;font:600 12px 'Segoe UI';color:#0F172A;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,0.18);">⬇ PNG</button>
  <canvas id="cc" style="width:100%;height:600px;display:block;border-radius:12px;"></canvas>
</div>
<script>
(function(){
  const STAIR=__STAIR__,RIVER=__RIVER__,PIN=__PIN__,PDC=__PDC__,ETA=__ETA__,LOST=__LOST__,MSG=__MSG__;
  const cv=document.getElementById('cc'),ctx=cv.getContext('2d');
  {const _b=document.getElementById('cc_dl');if(_b)_b.addEventListener('click',function(){const a=document.createElement('a');a.download='cascada_energia.png';a.href=cv.toDataURL('image/png');a.click();});}
  let W=1180,H=600,dpr=Math.max(2,window.devicePixelRatio||1);
  function resize(){const w=cv.clientWidth||1180;W=w;H=600;cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
  window.addEventListener('resize',resize);resize();
  const C={tinta:'#0F172A',gris:'#64748B',azul:'#0EA5E9',verde:'#16A34A',verde2:'#22C55E',rojo:'#EF4444',rojo2:'#FCA5A5',ambar:'#F59E0B'};
  let t=0,last=performance.now()/1000,parts=[];for(let i=0;i<60;i++)parts.push(Math.random());

  function dbSection(){
    const x0=70,x1=W-90,yTop=64,yBot=232,lvMax=78,lvMin=-12;
    const y=lv=>yBot-(lv-lvMin)/(lvMax-lvMin)*(yBot-yTop);
    ctx.fillStyle=C.gris;ctx.font='600 13px Segoe UI';ctx.textAlign='left';ctx.fillText('1.  El viaje por el aire (en dB)',x0,yTop-12);
    ctx.strokeStyle='rgba(148,163,184,0.4)';ctx.lineWidth=1;
    for(const lv of [70,40,10,-10]){ctx.beginPath();ctx.moveTo(x0,y(lv));ctx.lineTo(x1,y(lv));ctx.stroke();ctx.fillStyle=C.gris;ctx.font='10px Segoe UI';ctx.fillText(lv+' dBm',x1+2,y(lv)+3);}
    const n=STAIR.length,dx=(x1-x0)/(n-1);
    for(let i=0;i<n;i++){const cx=x0+i*dx,lv=STAIR[i].lv;
      if(i>0){const px=x0+(i-1)*dx,plv=STAIR[i-1].lv,up=STAIR[i].d>0;
        ctx.strokeStyle=up?C.verde:C.rojo;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(px,y(plv));ctx.lineTo(cx,y(plv));ctx.lineTo(cx,y(lv));ctx.stroke();
        ctx.fillStyle=up?C.verde:C.rojo;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText((up?'+':'')+STAIR[i].d.toFixed(1)+' dB',(px+cx)/2,y(Math.max(plv,lv))-8);
        if(i===1){ctx.fillStyle=C.rojo;ctx.font='600 11px Segoe UI';ctx.fillText('↓ el grueso se pierde aquí, en el aire',(px+cx)/2,y(Math.min(plv,lv))+16);}
      }
      ctx.fillStyle=C.tinta;ctx.beginPath();ctx.arc(cx,y(lv),4,0,6.3);ctx.fill();
      ctx.fillStyle=C.tinta;ctx.font='600 11px Segoe UI';ctx.textAlign='center';ctx.fillText(STAIR[i].l,cx,yBot+16);
      ctx.fillStyle=C.gris;ctx.font='11px Segoe UI';ctx.fillText(lv.toFixed(1)+' dBm',cx,yBot+30);}
    const tau=(t*0.45)%1,seg=tau*(n-1),i0=Math.min(n-2,Math.floor(seg)),fr=seg-i0;
    const cx0=x0+i0*dx,cx1=x0+(i0+1)*dx;let dxp,dyp;
    if(fr<0.5){dxp=cx0+(fr/0.5)*(cx1-cx0);dyp=y(STAIR[i0].lv);}else{dxp=cx1;dyp=y(STAIR[i0].lv)+((fr-0.5)/0.5)*(y(STAIR[i0+1].lv)-y(STAIR[i0].lv));}
    ctx.fillStyle=C.ambar;ctx.shadowColor=C.ambar;ctx.shadowBlur=14;ctx.beginPath();ctx.arc(dxp,dyp,6,0,6.3);ctx.fill();ctx.shadowBlur=0;
    // conector P_in → río
    const ex=x0+(n-1)*dx, ey=y(STAIR[n-1].lv);
    ctx.fillStyle=C.azul;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText('P_in = '+PIN.toFixed(0)+' µW',ex,ey-12);
    ctx.strokeStyle=C.azul;ctx.lineWidth=2;ctx.setLineDash([5,4]);ctx.beginPath();ctx.moveTo(ex,ey+6);ctx.bezierCurveTo(ex,ey+60,110,300,110,318);ctx.stroke();ctx.setLineDash([]);
    ctx.fillStyle=C.azul;ctx.beginPath();ctx.moveTo(110,326);ctx.lineTo(104,314);ctx.lineTo(116,314);ctx.closePath();ctx.fill();
  }

  function riverSection(){
    const x0=110,x1=W-90,yc=430,HWmax=70;
    ctx.fillStyle=C.gris;ctx.font='600 13px Segoe UI';ctx.textAlign='left';ctx.fillText('2.  El río de energía que se estrecha (la conversión)',x0,yc-118);
    const n=RIVER.length,ax=[x0];for(let i=0;i<n;i++)ax.push(x0+(i+1)*(x1-x0)/(n+1));
    const pct=[100];for(const r of RIVER)pct.push(r.pct);const hw=pct.map(p=>p/100*HWmax);
    const grad=ctx.createLinearGradient(x0,0,x1,0);grad.addColorStop(0,'rgba(14,165,233,0.85)');grad.addColorStop(0.55,'rgba(34,197,94,0.6)');grad.addColorStop(1,'rgba(22,163,74,0.9)');
    ctx.fillStyle=grad;ctx.beginPath();ctx.moveTo(ax[0],yc-hw[0]);
    for(let i=1;i<ax.length;i++)ctx.lineTo(ax[i],yc-hw[i]);ctx.lineTo(x1,yc-hw[hw.length-1]);ctx.lineTo(x1,yc+hw[hw.length-1]);
    for(let i=ax.length-1;i>=0;i--)ctx.lineTo(ax[i],yc+hw[i]);ctx.closePath();ctx.fill();
    for(let i=0;i<parts.length;i++){const f=parts[i],x=x0+f*(x1-x0);let seg=0;while(seg<ax.length-1&&ax[seg+1]<x)seg++;const fr=(x-ax[seg])/((ax[Math.min(seg+1,ax.length-1)]-ax[seg])||1);const h=hw[seg]+(hw[Math.min(seg+1,hw.length-1)]-hw[seg])*Math.min(1,fr);const yy=yc+Math.sin(i*12.9+f*30)*h*0.6;ctx.fillStyle='rgba(255,255,255,0.55)';ctx.beginPath();ctx.arc(x,yy,2.4,0,6.3);ctx.fill();}
    ctx.fillStyle=C.azul;ctx.font='600 13px Segoe UI';ctx.textAlign='center';ctx.fillText('P_in',ax[0],yc-hw[0]-10);ctx.fillText(PIN.toFixed(0)+' µW · 100%',ax[0],yc+hw[0]+22);
    ctx.fillStyle=C.verde;ctx.fillText('P_DC',x1,yc-hw[hw.length-1]-10);ctx.fillText(PDC.toFixed(0)+' µW · '+ETA.toFixed(0)+'%',x1,yc+hw[hw.length-1]+22);
    for(let i=0;i<n;i++){const xa=ax[i+1],r=RIVER[i],big=r.lost>250;
      ctx.fillStyle=C.tinta;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText('×'+r.n+'  '+r.f.toFixed(3),xa,yc-hw[i+1]-12);
      const np=Math.max(2,Math.round(r.lost/45)),phase=(t*0.6+i*0.2)%1;
      for(let k=0;k<np;k++){const yy=yc+hw[i+1]+((phase+k/np)%1)*(big?95:60),op=1-((phase+k/np)%1);ctx.fillStyle='rgba(239,68,68,'+(0.25+0.5*op).toFixed(2)+')';ctx.beginPath();ctx.arc(xa+(k-np/2)*4,yy,big?3.4:2.4,0,6.3);ctx.fill();}
      ctx.fillStyle=C.rojo;ctx.font=(big?'600 ':'')+'12px Segoe UI';ctx.fillText('−'+r.lost.toFixed(0)+' µW',xa,yc+hw[i+1]+(big?112:92));
      ctx.fillStyle=C.rojo2;ctx.font='10px Segoe UI';ctx.fillText('(calor)',xa,yc+hw[i+1]+(big?125:106));}
    ctx.fillStyle=C.rojo;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText('▲ cuello de botella',(ax[3]+ax[4])/2,yc+hw[4]+148);
    // contador
    const bx=x0,by=yc+118,bw=240,bh=44;ctx.fillStyle='rgba(255,255,255,0.9)';ctx.strokeStyle='#CBD5E1';ctx.lineWidth=1;ctx.beginPath();ctx.rect(bx,by,bw,bh);ctx.fill();ctx.stroke();
    ctx.textAlign='left';ctx.fillStyle=C.rojo;ctx.font='600 13px Segoe UI';ctx.fillText('Perdido: '+LOST.toFixed(0)+' µW',bx+12,by+18);
    ctx.fillStyle=C.verde;ctx.fillText('Útil: '+PDC.toFixed(0)+' µW ('+ETA.toFixed(1)+'%)',bx+12,by+36);
  }

  function loop(now){now/=1000;let dt=Math.min(0.05,now-last);last=now;t+=dt;
    for(let i=0;i<parts.length;i++){parts[i]+=dt*0.10;if(parts[i]>1)parts[i]-=1;}
    ctx.clearRect(0,0,W,H);const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#F8FBFF');g.addColorStop(1,'#F3FAF6');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    dbSection();riverSection();
    ctx.fillStyle=C.tinta;ctx.font='600 13px Segoe UI';ctx.textAlign='center';ctx.fillText('De '+PIN.toFixed(0)+' µW que entran, salen '+PDC.toFixed(0)+' µW útiles ('+ETA.toFixed(1)+'%)  ·  ≈ '+Math.round(MSG)+' mensajes/día',W/2,H-14);
    requestAnimationFrame(loop);}
  requestAnimationFrame(loop);
})();
</script>
"""
for kk, vv in {"__STAIR__": stair_js, "__RIVER__": river_js, "__PIN__": f"{P_in_uW:.1f}",
               "__PDC__": f"{P_DC_uW:.1f}", "__ETA__": f"{eta_op:.1f}",
               "__LOST__": f"{lost_total:.1f}", "__MSG__": f"{msg_dia:.1f}"}.items():
    HTML = HTML.replace(kk, vv)
components.html(HTML, height=620, scrolling=False)

st.caption(
    "Arriba: presupuesto de enlace en dB (EIRP 70 dBm, FSPL, corrección urbana ITU-R "
    "P.1546, ganancia FLPDA). Abajo: cadena de potencia P_DC = P_in·η_mm·η_IMN·PCE·η_PMIC "
    "(4 factores). El 67,5 % es lo que se conserva de P_in, no la figura de mérito η_total "
    "(5 factores). Cifras canónicas · §4.3.1, Figura 5, Apéndice E.12."
)
st.success(
    "**¿Qué pregunta responde esta simulación?**  \nDónde se pierde la energía: el grueso "
    "en el aire (FSPL) y, dentro del circuito, en la rectificación (PCE) y la gestión (PMIC). "
    "De 2.427 µW que entran, salen 1.638 µW útiles."
)
