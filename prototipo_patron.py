"""
PROTOTIPO (experimental) — "Patrón de radiación: dirigir vs omni".

Compara la directividad de la FLPDA Koch (B, lóbulo) con la cuasi-omni del
Sierpinski (A, círculo), superpuestas. Al desapuntar la FLPDA de la torre, la
ganancia captada cae y, con ella, P_DC y los mensajes/día. Canvas 60 fps. Cifras
canónicas. NO es la app oficial.
"""

import math
import streamlit as st
import streamlit.components.v1 as components

from configs.parametros import CANONICAL
from _proto_ui import poster_style

poster_style()

st.title(":material/wifi_tethering: Patrón de radiación — dirigir vs omni")
st.caption("Prototipo experimental — no forma parte de la aplicación oficial del trabajo.")
st.markdown(
    "Una antena **dirigida** concentra su ganancia hacia donde apunta; una **omni** la "
    "reparte. Aquí ves **las dos a la vez** (lóbulo = FLPDA, círculo = Sierpinski). La torre "
    "está fija arriba: gira la FLPDA y observa cómo, al desapuntar, **cae la ganancia "
    "captada y con ella P_DC y los mensajes**."
)
st.info(
    "**Pregunta que responde:** ¿por qué una antena dirigida capta más energía, y por qué "
    "hay que apuntarla?  ·  Prototipo **conceptual** en el patrón; la **consecuencia** (P_DC "
    "y mensajes al desapuntar) escala con la ganancia captada del modelo.",
    icon=":material/help:",
)

c1, c2 = st.columns([2, 3])
with c1:
    ant = st.segmented_control("Antena resaltada", ["B · FLPDA (dirigida)", "A · Sierpinski (omni)"],
                               default="B · FLPDA (dirigida)") or "B · FLPDA (dirigida)"
with c2:
    orient = st.slider("Orientación de la FLPDA [°]  (0 = apuntando a la torre)", 0, 360, 0, 5)

is_B = ant.startswith("B")
PEAK_B, PEAK_A = CANONICAL['gain_dBi'], 3.0


def gB(phi):
    return max(0.0, math.cos(math.radians(phi) / 2.0)) ** 6


cap_B = PEAK_B + 10.0 * math.log10(max(gB(orient), 1e-3))
P_DC_canon = CANONICAL['p_dc_uW'] if 'p_dc_uW' in CANONICAL else CANONICAL['P_dc_uW']
MSG_canon = 86400.0 / CANONICAL['T_ciclo_s']
pdc_eff = P_DC_canon * 10 ** ((cap_B - PEAK_B) / 10.0)
msg_eff = MSG_canon * pdc_eff / P_DC_canon

# Toda la consecuencia IoT escala con la ganancia captada (mecanismo → efecto)
P_in_eff_dBm = CANONICAL['P_in_dBm'] + (cap_B - PEAK_B)
P_in_eff_uW = CANONICAL['P_in_mW'] * 1000.0 * 10 ** ((cap_B - PEAK_B) / 10.0)
T_ciclo_eff = CANONICAL['T_ciclo_s'] * (P_DC_canon / max(pdc_eff, 1e-9))

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Ganancia captada", f"{cap_B:.1f} dBi",
          delta="apuntada" if cap_B > PEAK_B - 1.5 else "desapuntada",
          delta_color="normal" if cap_B > PEAK_B - 1.5 else "inverse")
m2.metric("P_RF disponible", f"{P_in_eff_uW:,.0f} µW".replace(",", " "))
m3.metric("P_DC útil", f"{pdc_eff:,.0f} µW".replace(",", " "))
m4.metric("T_ciclo", f"{T_ciclo_eff/60:.1f} min")
m5.metric("Mensajes/día", f"≈ {msg_eff:,.0f}".replace(",", " "))

HTML = r"""
<div style="position:relative;width:100%;font-family:'Segoe UI',system-ui,sans-serif;">
  <button id="pr_dl" title="Descargar imagen para póster / diapositiva" style="position:absolute;top:10px;right:12px;z-index:6;background:rgba(255,255,255,0.92);border:1px solid #CBD5E1;border-radius:8px;padding:5px 11px;font:600 12px 'Segoe UI';color:#0F172A;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,0.18);">⬇ PNG</button>
  <canvas id="pr" style="width:100%;height:500px;display:block;border-radius:12px;"></canvas>
</div>
<script>
(function(){
  const ISB=__ISB__,PEAKB=__PEAKB__,PEAKA=__PEAKA__,ORIENT=__ORIENT__,CAP=__CAP__,PDC=__PDC__,MSG=__MSG__,PRF=__PRF__,TCIC=__TCIC__;
  const cv=document.getElementById('pr'),ctx=cv.getContext('2d');
  {const _b=document.getElementById('pr_dl');if(_b)_b.addEventListener('click',function(){const a=document.createElement('a');a.download='patron_radiacion.png';a.href=cv.toDataURL('image/png');a.click();});}
  let W=1180,H=500,dpr=Math.max(2,window.devicePixelRatio||1);
  function resize(){const w=cv.clientWidth||1180;W=w;H=500;cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
  window.addEventListener('resize',resize);resize();
  const C={tinta:'#0F172A',gris:'#64748B',verde:'#16A34A',verde2:'#22C55E',viol:'#7C3AED',violb:'#A78BFA',ambar:'#F59E0B'};
  let t=0,last=performance.now()/1000;
  const cx=W/2,cy=H/2+10,Rmax=Math.min(180,H/2-50),GMIN=-15,GMAX=9;
  const rOf=db=>Math.max(0,(db-GMIN)/(GMAX-GMIN))*Rmax;
  function gpatB(phi){phi=phi*Math.PI/180;return Math.pow(Math.max(0,Math.cos(phi/2)),6);}
  function gpatA(phi){phi=phi*Math.PI/180;return 0.85+0.10*Math.cos(2*phi);}
  function gdbB(a){return PEAKB+10*Math.log10(Math.max(gpatB(a-ORIENT),1e-3));}
  function gdbA(a){return PEAKA+10*Math.log10(Math.max(gpatA(a),1e-3));}
  function pt(a,r){const rad=(a-90)*Math.PI/180;return [cx+r*Math.cos(rad),cy+r*Math.sin(rad)];}

  function lobe(gd,col,fillA,bold){ctx.beginPath();for(let a=0;a<=360;a+=2){const p=pt(a,rOf(gd(a)));if(a===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);}ctx.closePath();ctx.fillStyle=fillA;ctx.strokeStyle=col;ctx.lineWidth=bold?2.8:1.4;ctx.fill();ctx.stroke();}

  function draw(){
    ctx.clearRect(0,0,W,H);const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#0B1220');g.addColorStop(1,'#0F1A2E');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='rgba(148,163,184,0.25)';ctx.fillStyle='#64748B';ctx.font='10px Segoe UI';ctx.textAlign='center';
    for(const db of [-10,-5,0,5]){const r=rOf(db);ctx.beginPath();ctx.arc(cx,cy,r,0,6.3);ctx.stroke();ctx.fillText(db+' dBi',cx,cy-r-2);}
    for(let a=0;a<360;a+=30){const p=pt(a,Rmax);ctx.strokeStyle='rgba(148,163,184,0.18)';ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(p[0],p[1]);ctx.stroke();}

    // ambos patrones (el resaltado en negrita)
    lobe(gdbA,'#A78BFA','rgba(124,58,237,0.10)',!ISB);
    lobe(gdbB,'#22C55E','rgba(34,197,94,0.22)',ISB);

    // antena que gira (flecha de la FLPDA)
    const ap=pt(ORIENT,40);ctx.strokeStyle=C.verde2;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(ap[0],ap[1]);ctx.stroke();
    const a2=pt(ORIENT,40);ctx.fillStyle=C.verde2;ctx.beginPath();ctx.arc(a2[0],a2[1],4,0,6.3);ctx.fill();

    // torre arriba
    const tp=pt(0,Rmax+26);ctx.fillStyle=C.ambar;ctx.font='600 13px Segoe UI';ctx.textAlign='center';ctx.fillText('📡 Torre',tp[0],tp[1]-6);
    // rayo de ganancia captada (FLPDA) hacia la torre
    const cp=pt(0,rOf(gdbB(0)));ctx.strokeStyle=C.ambar;ctx.lineWidth=3;ctx.shadowColor=C.ambar;ctx.shadowBlur=12;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(cp[0],cp[1]);ctx.stroke();ctx.shadowBlur=0;
    ctx.fillStyle=C.ambar;ctx.beginPath();ctx.arc(cp[0],cp[1],5,0,6.3);ctx.fill();
    ctx.fillStyle='#FDE68A';ctx.font='600 13px Segoe UI';ctx.textAlign='left';ctx.fillText(CAP.toFixed(1)+' dBi hacia la torre',cp[0]+10,cp[1]);

    const sa=(t*60)%360,sp=pt(sa,Rmax);ctx.strokeStyle='rgba(56,189,248,0.5)';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(sp[0],sp[1]);ctx.stroke();

    ctx.textAlign='center';ctx.fillStyle='#E2E8F0';ctx.font='600 11px Segoe UI';
    // leyenda
    ctx.textAlign='left';ctx.fillStyle=C.verde2;ctx.fillText('■ FLPDA (dirigida)',24,30);ctx.fillStyle=C.violb;ctx.fillText('■ Sierpinski (omni)',24,48);
    ctx.fillStyle='#CBD5E1';ctx.font='12px Segoe UI';
    ctx.fillText('Consecuencia IoT:  P_RF ≈ '+PRF.toFixed(0)+' µW  →  P_DC ≈ '+PDC.toFixed(0)+' µW  →  T_ciclo ≈ '+(TCIC/60).toFixed(1)+' min  →  ≈ '+Math.round(MSG)+' msg/día',24,H-18);
  }
  function loop(now){now/=1000;let dt=Math.min(0.05,now-last);last=now;t+=dt;draw();requestAnimationFrame(loop);}
  requestAnimationFrame(loop);
})();
</script>
"""
for kk, vv in {"__ISB__": "true" if is_B else "false", "__PEAKB__": f"{PEAK_B:.3f}",
               "__PEAKA__": f"{PEAK_A:.3f}", "__ORIENT__": f"{orient}", "__CAP__": f"{cap_B:.3f}",
               "__PDC__": f"{pdc_eff:.1f}", "__MSG__": f"{msg_eff:.1f}",
               "__PRF__": f"{P_in_eff_uW:.1f}", "__TCIC__": f"{T_ciclo_eff:.1f}"}.items():
    HTML = HTML.replace(kk, vv)
components.html(HTML, height=520, scrolling=False)

st.caption(
    "Patrones ilustrativos (lóbulo directivo para la FLPDA, cuasi-omni para el Sierpinski). "
    "La ganancia máxima de la FLPDA, 7,10 dBi, es canónica a 550 MHz. P_DC y mensajes "
    "escalan con la ganancia captada al desapuntar (ilustrativo). §2.4.4."
)
st.success(
    "**¿Qué pregunta responde esta simulación?**  \nPor qué importa la orientación: la FLPDA "
    "concentra la ganancia y hay que apuntarla a la torre; al desapuntar, caen la ganancia "
    "captada, P_DC y los mensajes. El Sierpinski capta desde cualquier lado, pero con menos "
    "techo."
)
