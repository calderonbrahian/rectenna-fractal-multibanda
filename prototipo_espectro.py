"""
PROTOTIPO (experimental) — "El espectro urbano: qué hay en el aire".

Por qué el trabajo apunta a la TDT en UHF: el espectro urbano tiene muchas señales,
pero la de TV digital es potente, estable y caracterizada (Escenario B), mientras
las de alta frecuencia (Wi-Fi, 5G) son bajas y variables (Escenario A). Con la sonda
de sintonía se ve que la rectena solo capta bien en su banda (UHF). Canvas 60 fps.
Fuentes canónicas (RF_UHF). NO es la app oficial.
"""

import streamlit as st
import streamlit.components.v1 as components

from configs.parametros import RF_UHF, CANONICAL
from _proto_ui import poster_style

poster_style()

st.title(":material/cell_tower: El espectro urbano — qué hay en el aire")
st.caption("Prototipo experimental — no forma parte de la aplicación oficial del trabajo.")
st.markdown(
    "En la ciudad conviven muchas señales. La rectena **cosecha en UHF** (la franja verde), "
    "donde la **TV digital del Cerro Nutibara** es fuerte y estable. Las de alta frecuencia "
    "(Wi-Fi, 5G) están ahí, pero son **bajas y variables**. Mueve la **sonda de sintonía** y "
    "comprueba que la rectena solo capta bien dentro de su banda."
)
st.info(
    "**Pregunta que responde:** ¿por qué el estudio cosecha de la TV digital (UHF) y no de "
    "Wi-Fi o 5G?  ·  Prototipo **conceptual**: esquema basado en las **bandas de interés del "
    "estudio**, no una medición del espectro real de una ciudad.",
    icon=":material/help:",
)

st.markdown("#### Modo «¿Qué pasa si…?» — sintoniza la rectena")
st.caption(
    "Mueve la sonda y observa qué capta la rectena en esa frecuencia. La **potencia "
    "disponible** es la fracción de la potencia de diseño (P_in = 2 427 µW en banda, 550 MHz) "
    "que sobrevive a esa sintonía."
)
probe = st.slider("Frecuencia de sintonía de la rectena [MHz]", 400, 6000, 550, 10)
pf = probe / 1000.0
# respuesta de banda (cosecha alta solo en UHF 470–900)
import math
capture = 100.0 / (1.0 + ((pf - 0.66) / 0.28) ** 6)
# potencia disponible = fracción de la P_in canónica de diseño que sobrevive a la sintonía
P_in_canon_uW = CANONICAL['P_in_mW'] * 1000.0
P_disp_uW = P_in_canon_uW * capture / 100.0
# estado de adaptación
if capture >= 80.0:
    adap_lbl, adap_col, adap_ico = "Adaptada", "#16A34A", "✅"
elif capture >= 30.0:
    adap_lbl, adap_col, adap_ico = "Parcial", "#F59E0B", "⚠️"
else:
    adap_lbl, adap_col, adap_ico = "Desadaptada", "#EF4444", "⛔"

sources = []
for name, d in RF_UHF.items():
    f = d['freq_ghz']
    sources.append((name, f, d['eirp_dbm'], 0.47 <= f <= 0.92, False))
for n, f in [("GSM 1800", 1.84), ("Wi-Fi 2,4", 2.45), ("5G 3,5", 3.30), ("Wi-Fi 5,8", 5.80)]:
    sources.append((n, f, 22.0, False, True))
src_js = "[" + ",".join("{n:'%s',f:%.3f,e:%.0f,h:%s,v:%s}" % (n, f, e, str(h).lower(), str(v).lower())
                        for n, f, e, h, v in sources) + "]"

k1, k2, k3 = st.columns(3)
k1.metric("Captación en esa sintonía", f"{capture:.0f} %")
k2.metric("Potencia disponible", f"{P_disp_uW:,.0f} µW".replace(",", " "),
          delta=f"de 2 427 µW en banda", delta_color="off")
k3.metric("Banda de cosecha", "470–900 MHz (UHF)")
# indicador visual de adaptación
st.markdown(
    f"<div style='margin:2px 0 14px 0;'>"
    f"<div style='display:flex;justify-content:space-between;font-size:0.8rem;color:#64748B;'>"
    f"<span>desadaptada</span><span>adaptación de la rectena</span><span>adaptada</span></div>"
    f"<div style='position:relative;height:14px;border-radius:7px;margin-top:4px;"
    f"background:linear-gradient(90deg,#EF4444 0%,#F59E0B 50%,#16A34A 100%);'>"
    f"<div style='position:absolute;left:calc({capture:.0f}% - 9px);top:-3px;width:18px;height:20px;"
    f"border-radius:5px;background:#0F172A;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);'></div></div>"
    f"<div style='text-align:center;margin-top:8px;font-weight:600;color:{adap_col};'>"
    f"{adap_ico} {adap_lbl} — {capture:.0f}% de captación a {probe} MHz</div></div>",
    unsafe_allow_html=True,
)

HTML = r"""
<div style="position:relative;width:100%;font-family:'Segoe UI',system-ui,sans-serif;">
  <button id="es_dl" title="Descargar imagen para póster / diapositiva" style="position:absolute;top:10px;right:12px;z-index:6;background:rgba(255,255,255,0.92);border:1px solid #CBD5E1;border-radius:8px;padding:5px 11px;font:600 12px 'Segoe UI';color:#0F172A;cursor:pointer;box-shadow:0 1px 4px rgba(0,0,0,0.18);">⬇ PNG</button>
  <canvas id="es" style="width:100%;height:520px;display:block;border-radius:12px;"></canvas>
</div>
<script>
(function(){
  const SRC=__SRC__, PROBE=__PROBE__, CAP=__CAP__;
  const cv=document.getElementById('es'),ctx=cv.getContext('2d');
  {const _b=document.getElementById('es_dl');if(_b)_b.addEventListener('click',function(){const a=document.createElement('a');a.download='espectro_urbano.png';a.href=cv.toDataURL('image/png');a.click();});}
  let W=1180,H=520,dpr=Math.max(2,window.devicePixelRatio||1);
  function resize(){const w=cv.clientWidth||1180;W=w;H=520;cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
  window.addEventListener('resize',resize);resize();
  const C={tinta:'#0F172A',gris:'#64748B',verde:'#16A34A',verde2:'#22C55E',azul:'#0EA5E9',ambar:'#F59E0B',rojo:'#EF4444',viol:'#7C3AED'};
  let t=0,last=performance.now()/1000;
  const FMIN=0.4,FMAX=6.5,x0=70,x1=W-40,yBase=400,yTop=110;
  const xf=f=>x0+(Math.log(f)-Math.log(FMIN))/(Math.log(FMAX)-Math.log(FMIN))*(x1-x0);
  const hOf=e=>Math.max(10,(e-15)/(72-15)*(yBase-yTop));

  function skyline(){   // silueta de ciudad
    ctx.fillStyle='rgba(30,41,59,0.9)';
    let x=0;let seed=7;
    while(x<W){const w=24+(seed%5)*10;const h=30+(seed*37%70);ctx.fillRect(x,yBase- h+ (yBase-yBase), x, 0);
      ctx.fillRect(x,H-10-h-(yBase-yBase),w,h+200);x+=w+6;seed=(seed*1103515245+12345)&0x7fffffff;}
  }

  function draw(){
    ctx.clearRect(0,0,W,H);
    const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#0B1220');g.addColorStop(1,'#111A2E');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    // skyline tenue
    ctx.fillStyle='rgba(30,41,59,0.55)';let bx=0,seed=9;
    while(bx<W){const bw=26+(seed%5)*9;const bh=24+(seed*29%60);ctx.fillRect(bx,yBase-bh,bw,bh+120);bx+=bw+5;seed=(seed*1103515245+12345)&0x7fffffff;}

    // banda de cosecha UHF
    const u0=xf(0.47),u1=xf(0.92);
    ctx.fillStyle='rgba(34,197,94,0.12)';ctx.fillRect(u0,yTop-20,u1-u0,yBase-(yTop-20));
    ctx.strokeStyle='rgba(34,197,94,0.5)';ctx.setLineDash([5,4]);ctx.lineWidth=1.5;ctx.strokeRect(u0,yTop-20,u1-u0,yBase-(yTop-20));ctx.setLineDash([]);
    ctx.fillStyle=C.verde2;ctx.font='600 12px Segoe UI';ctx.textAlign='center';ctx.fillText('🌾 la rectena cosecha aquí (UHF 470–900 MHz)',(u0+u1)/2,yTop-28);

    // ejes
    ctx.strokeStyle='rgba(148,163,184,0.25)';ctx.lineWidth=1;ctx.fillStyle=C.gris;ctx.font='10px Segoe UI';ctx.textAlign='center';
    for(const f of [0.5,0.7,1,1.8,2.4,3.5,5.8]){const x=xf(f);ctx.beginPath();ctx.moveTo(x,yTop-20);ctx.lineTo(x,yBase);ctx.stroke();ctx.fillText((f<1?(f*1000).toFixed(0)+' MHz':f+' GHz'),x,yBase+16);}
    ctx.strokeStyle='#94A3B8';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x0,yBase);ctx.lineTo(x1,yBase);ctx.stroke();

    // barras con shimmer
    for(const s of SRC){const x=xf(s.f),w=26;let h=hOf(s.e);h+= (s.v?6:3)*Math.sin(t*6+x); // shimmer
      const tdt=s.n.indexOf('TV')===0;let col=s.h?(tdt?C.verde2:C.verde):(s.v?'#6B7280':C.azul);const yb=yBase-h;
      if(tdt){ctx.shadowColor=C.verde2;ctx.shadowBlur=18;}
      if(s.v){ctx.globalAlpha=0.5;ctx.fillStyle=col;ctx.fillRect(x-w/2,yb,w,h);ctx.globalAlpha=1;ctx.strokeStyle='rgba(156,163,175,0.7)';ctx.setLineDash([3,3]);ctx.strokeRect(x-w/2,yb,w,h);ctx.setLineDash([]);}
      else{ctx.fillStyle=col;ctx.fillRect(x-w/2,yb,w,h);}ctx.shadowBlur=0;
      ctx.fillStyle=col;ctx.font='600 11px Segoe UI';ctx.textAlign='center';
      const lbl=s.v?s.n:s.n.replace(' (Colombia)','').replace('TV UHF (DVB-T)','TDT (DVB-T)').replace('LTE Macro 700 MHz','LTE 700').replace('LTE Band 28 (700 MHz)','LTE B28').replace('LoRa Gateway','LoRa GW');
      ctx.fillText(lbl,x,yb-8);ctx.fillStyle=C.gris;ctx.font='10px Segoe UI';ctx.fillText(s.v?'variable':s.e.toFixed(0)+' dBm',x,yb-22);
      if(tdt)for(let k=0;k<6;k++){const fr=((t*0.5+k/6)%1);ctx.fillStyle='rgba(34,197,94,'+(0.8*(1-fr)+0.1).toFixed(2)+')';ctx.beginPath();ctx.arc(x+Math.sin((t+k)*3)*4,yBase-fr*(yBase-(yTop-10)),2.6,0,6.3);ctx.fill();}
    }
    // antena de cosecha
    const ax=(u0+u1)/2,ay=yTop-2;ctx.strokeStyle=C.verde2;ctx.lineWidth=2.5;for(let i=0;i<4;i++){const yy=ay-i*7,w=18-i*4;ctx.beginPath();ctx.moveTo(ax-w,yy);ctx.lineTo(ax+w,yy);ctx.stroke();}ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(ax,ay+18);ctx.stroke();

    // sonda de sintonía
    const sx=xf(PROBE/1000.0);ctx.strokeStyle=C.ambar;ctx.lineWidth=2;ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(sx,yTop-20);ctx.lineTo(sx,yBase);ctx.stroke();ctx.setLineDash([]);
    ctx.fillStyle=C.ambar;ctx.font='600 12px Segoe UI';ctx.textAlign='center';
    const inb=CAP>50;ctx.fillStyle=inb?C.verde2:C.rojo;
    ctx.fillText('🎯 sonda: captación '+CAP.toFixed(0)+'%',sx,yBase+34);

    // llamadas
    ctx.textAlign='center';ctx.fillStyle=C.verde2;ctx.font='600 12px Segoe UI';ctx.fillText('fuerte · estable · caracterizada → Escenario B (cuantitativo)',xf(0.62),yBase-hOf(70)-44);
    ctx.fillStyle='#9CA3AF';ctx.fillText('baja y variable → Escenario A (exploratorio)',xf(3.0),yTop+24);
  }
  function loop(now){now/=1000;let dt=Math.min(0.05,now-last);last=now;t+=dt;draw();requestAnimationFrame(loop);}
  requestAnimationFrame(loop);
})();
</script>
"""
for kk, vv in {"__SRC__": src_js, "__PROBE__": f"{probe}", "__CAP__": f"{capture:.1f}"}.items():
    HTML = HTML.replace(kk, vv)
components.html(HTML, height=540, scrolling=False)

st.markdown("**Fundamento del escenario — por qué la TDT es la fuente elegida**")
cA, cB = st.columns(2)
with cA:
    with st.container(border=True):
        st.markdown(
            "**TDT (DVB-T)**\n"
            "- EIRP **alta** (hasta ≈ 70 dBm)\n"
            "- transmisor **fijo y continuo**\n"
            "- **cobertura amplia**\n"
            "- banda **UHF**, alineada con el Escenario B\n\n"
            "→ fuente **firme y caracterizable** (escenario cuantitativo)"
        )
with cB:
    with st.container(border=True):
        st.markdown(
            "**Wi-Fi / LTE / 5G**\n"
            "- potencia **variable**\n"
            "- tráfico **variable**\n"
            "- dependen de la **ocupación**\n"
            "- alta frecuencia\n\n"
            "→ **no caracterizable** como fuente firme (escenario exploratorio)"
        )

st.markdown("#### Comparador de fuentes — por qué la TDT gana en las tres columnas")
st.caption(
    "Una fuente sirve como base cuantitativa solo si reúne las tres condiciones: potencia "
    "suficiente, estabilidad en el tiempo y caracterización fiable. La TDT es la única que las "
    "cumple las tres; por eso es la fuente del Escenario B."
)


def _badge(txt, tone):
    col = {"alta": "#16A34A", "media": "#D97706", "baja": "#DC2626", "var": "#64748B"}[tone]
    bg = {"alta": "#DCFCE7", "media": "#FEF3C7", "baja": "#FEE2E2", "var": "#E2E8F0"}[tone]
    return (f"<span style='background:{bg};color:{col};font-weight:600;font-size:0.82rem;"
            f"padding:2px 10px;border-radius:11px;white-space:nowrap;'>{txt}</span>")


_rows = [
    ("TDT (DVB-T)", "UHF 550 MHz · 70 dBm", ("Alta", "alta"), ("Alta", "alta"), ("Alta", "alta")),
    ("LoRa GW",     "915 MHz · 27 dBm",     ("Media", "media"), ("Alta", "alta"), ("Media", "media")),
    ("LTE",         "700 MHz · 43–46 dBm",  ("Variable", "var"), ("Media", "media"), ("Baja", "baja")),
    ("Wi-Fi",       "2,4 / 5,8 GHz",        ("Variable", "var"), ("Baja", "baja"), ("Baja", "baja")),
    ("5G",          "3,5 GHz",              ("Variable", "var"), ("Baja", "baja"), ("Baja", "baja")),
]
_html = [
    "<table style='width:100%;border-collapse:collapse;font-family:Segoe UI,system-ui,sans-serif;'>",
    "<thead><tr style='border-bottom:2px solid #CBD5E1;text-align:left;color:#0F172A;'>",
    "<th style='padding:8px 6px;'>Fuente</th><th style='padding:8px 6px;'>Banda · EIRP</th>",
    "<th style='padding:8px 6px;'>Potencia</th><th style='padding:8px 6px;'>Estabilidad</th>",
    "<th style='padding:8px 6px;'>Caracterización</th></tr></thead><tbody>",
]
for name, band, pot, est, car in _rows:
    hi = name.startswith("TDT")
    bgr = "background:#F0FDF4;" if hi else ""
    nm = f"<b>{name}</b>" + (" 🏆" if hi else "")
    _html.append(
        f"<tr style='border-bottom:1px solid #E2E8F0;{bgr}'>"
        f"<td style='padding:9px 6px;'>{nm}</td>"
        f"<td style='padding:9px 6px;color:#475569;font-size:0.85rem;'>{band}</td>"
        f"<td style='padding:9px 6px;'>{_badge(*pot)}</td>"
        f"<td style='padding:9px 6px;'>{_badge(*est)}</td>"
        f"<td style='padding:9px 6px;'>{_badge(*car)}</td></tr>"
    )
_html.append("</tbody></table>")
st.markdown("".join(_html), unsafe_allow_html=True)
st.caption(
    "TDT, LoRa y LTE con EIRP canónicos (RF_UHF). Wi-Fi y 5G se valoran de forma cualitativa "
    "(potencia y ocupación variables, no caracterizables como fuente firme). La caracterización "
    "alta de la TDT es la que habilita el cálculo cuantitativo del Escenario B."
)

st.caption(
    "Fuentes UHF con EIRP canónicos (RF_UHF): TDT 70 dBm, LTE 46/43 dBm, LoRa GW 27 dBm. "
    "Las bandas de alta frecuencia (Wi-Fi, 5G) se muestran como presentes pero bajas y no "
    "caracterizadas (§1.1, Tabla 1). La sonda ilustra que la rectena solo capta dentro de su "
    "banda de diseño (UHF 470–900 MHz); fuera, la captación cae."
)
st.success(
    "**¿Qué pregunta responde esta simulación?**  \nPor qué se eligió la TDT: es la fuente "
    "fuerte, estable y caracterizada dentro de la banda de cosecha; las de alta frecuencia "
    "(Wi-Fi, 5G) son bajas y variables."
)
