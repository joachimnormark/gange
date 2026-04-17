import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Matematikværktøj", layout="wide")
st.title("📐 Matematikværktøj")

mode = st.selectbox(
    "Vælg type:",
    options=["Areal lille", "Areal stor", "Omkreds lille", "Omkreds stor"]
)

# (kolonner, rækker, type)
configs = {
    "Areal lille":   (17, 12, "areal"),
    "Areal stor":    (22, 17, "areal"),
    "Omkreds lille": (17, 12, "omkreds"),
    "Omkreds stor":  (22, 17, "omkreds"),
}

grid_cols, grid_rows, mode_type = configs[mode]
is_omkreds = "true" if mode_type == "omkreds" else "false"

CELL = 30                        # pixels per grid cell
SVG_W = grid_cols * CELL
SVG_H = grid_rows * CELL
sc = (grid_cols - 5) // 2        # start column for initial 5×5 rektangel
sr = (grid_rows - 5) // 2        # start row

html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=no">
<style>
  body {{
    margin: 0;
    padding: 30px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    background: #f0f2f6;
    touch-action: none;
  }}
  #wrap {{
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,.1);
    padding: 36px;          /* extra room for Omkreds-labels udenfor SVG */
  }}
  svg {{
    border: 2px solid #ddd;
    border-radius: 5px;
    background: white;
    display: block;
    overflow: visible;      /* labels må gerne stikke ud */
    touch-action: none;
    cursor: default;
  }}
  .grid-line  {{ stroke:#000; stroke-width:1; }}
  .rectangle  {{ fill:rgba(250,245,192,.5); stroke:#4285f4; stroke-width:3; }}
  .corner     {{ fill:#4285f4; stroke:white; stroke-width:2; cursor:pointer; }}
  .corner:hover, .corner.dragging {{ fill:#1a73e8; }}
  .dim-text   {{ font-weight:bold; fill:#333; text-anchor:middle;
                 pointer-events:none; user-select:none; }}
  .dim-bg     {{ fill:white; stroke:white; stroke-width:4; pointer-events:none; }}
  .tick       {{ stroke:#4285f4; stroke-width:4; pointer-events:none; }}
</style>
</head>
<body>
<div id="wrap">
  <svg id="canvas" width="{SVG_W}" height="{SVG_H}"></svg>
</div>
<script>
const SVG_W      = {SVG_W};
const SVG_H      = {SVG_H};
const GCOLS      = {grid_cols};
const GROWS      = {grid_rows};
const CELL       = {CELL};
const IS_OMKREDS = {is_omkreds};
const FONT       = 14;
const CR         = 7;     // corner radius
const TICK_HALF  = 4.5;   // 9 px tick / 2  (= 3 × blå stroke-width 3)
const LABEL_OFF  = 22;    // afstand fra rektangel til label

const NS = 'http://www.w3.org/2000/svg';

let R = {{ x1:{sc}, y1:{sr}, x2:{sc+5}, y2:{sr+5} }};
let drag = {{ on:false, corner:null }};

const svg = document.getElementById('canvas');

/* ── hjælper ─────────────────────────────────────────────── */
function mk(tag, attrs) {{
  const e = document.createElementNS(NS, tag);
  for (const [k,v] of Object.entries(attrs||{{}})) e.setAttribute(k,v);
  return e;
}}
function show(e) {{ e.setAttribute('display',''); }}
function hide(e) {{ e.setAttribute('display','none'); }}

/* ── tegn gitter ──────────────────────────────────────────── */
for (let i=0; i<=GCOLS; i++)
  svg.appendChild(mk('line',{{class:'grid-line',
    x1:i*CELL,y1:0,x2:i*CELL,y2:SVG_H}}));
for (let j=0; j<=GROWS; j++)
  svg.appendChild(mk('line',{{class:'grid-line',
    x1:0,y1:j*CELL,x2:SVG_W,y2:j*CELL}}));

/* ── rektangel ────────────────────────────────────────────── */
const rect = mk('rect',{{class:'rectangle'}});
svg.appendChild(rect);

/* ── tick-gruppe (Omkreds) ────────────────────────────────── */
const ticks = mk('g',{{}});
svg.appendChild(ticks);

/* ── labels: baggrunde + tekster (alle 4 sider) ──────────── */
// rækkefølge: bg før text, så bg er bag teksten
const wTopBg  = mk('rect',{{class:'dim-bg',rx:3}}); svg.appendChild(wTopBg);
const wBotBg  = mk('rect',{{class:'dim-bg',rx:3}}); svg.appendChild(wBotBg);
const hLftBg  = mk('rect',{{class:'dim-bg',rx:3}}); svg.appendChild(hLftBg);
const hRgtBg  = mk('rect',{{class:'dim-bg',rx:3}}); svg.appendChild(hRgtBg);

const wTopTxt = mk('text',{{class:'dim-text','font-size':FONT}}); svg.appendChild(wTopTxt);
const wBotTxt = mk('text',{{class:'dim-text','font-size':FONT}}); svg.appendChild(wBotTxt);
const hLftTxt = mk('text',{{class:'dim-text','font-size':FONT}}); svg.appendChild(hLftTxt);
const hRgtTxt = mk('text',{{class:'dim-text','font-size':FONT}}); svg.appendChild(hRgtTxt);

/* ── hjørne-cirkler ───────────────────────────────────────── */
function mkCorner(id) {{
  const c = mk('circle',{{class:'corner',r:CR,'data-corner':id}});
  svg.appendChild(c); return c;
}}
const C = {{
  tl: mkCorner('tl'), tr: mkCorner('tr'),
  bl: mkCorner('bl'), br: mkCorner('br')
}};

/* ── hjælper: placér et label + baggrund ─────────────────── */
function placeLabel(bgEl, txtEl, x, y, val) {{
  txtEl.setAttribute('x', x);
  txtEl.setAttribute('y', y);
  txtEl.textContent = val;
  const digits = String(val).length;
  const bw = digits === 1 ? 20 : 28;
  const bh = 20;
  bgEl.setAttribute('x', x - bw/2);
  bgEl.setAttribute('y', y - bh + 5);
  bgEl.setAttribute('width',  bw);
  bgEl.setAttribute('height', bh);
}}

/* ── hoved-opdatering ─────────────────────────────────────── */
function update() {{
  const x1 = Math.min(R.x1,R.x2), x2 = Math.max(R.x1,R.x2);
  const y1 = Math.min(R.y1,R.y2), y2 = Math.max(R.y1,R.y2);
  const px = x1*CELL, py = y1*CELL;
  const pw = (x2-x1)*CELL, ph = (y2-y1)*CELL;
  const gw = x2-x1, gh = y2-y1;

  /* rektangel */
  rect.setAttribute('x',px); rect.setAttribute('y',py);
  rect.setAttribute('width',pw); rect.setAttribute('height',ph);

  /* hjørner */
  C.tl.setAttribute('cx',x1*CELL); C.tl.setAttribute('cy',y1*CELL);
  C.tr.setAttribute('cx',x2*CELL); C.tr.setAttribute('cy',y1*CELL);
  C.bl.setAttribute('cx',x1*CELL); C.bl.setAttribute('cy',y2*CELL);
  C.br.setAttribute('cx',x2*CELL); C.br.setAttribute('cy',y2*CELL);

  /* ryd ticks */
  while (ticks.firstChild) ticks.removeChild(ticks.firstChild);

  if (IS_OMKREDS) {{
    /* ── Omkreds: labels på alle 4 sider ── */
    // Bredde øverst
    placeLabel(wTopBg, wTopTxt, px+pw/2, py-LABEL_OFF, gw);
    // Bredde nederst
    placeLabel(wBotBg, wBotTxt, px+pw/2, py+ph+LABEL_OFF+5, gw);
    // Højde venstre
    placeLabel(hLftBg, hLftTxt, px-LABEL_OFF, py+ph/2+5, gh);
    // Højde højre
    placeLabel(hRgtBg, hRgtTxt, px+pw+LABEL_OFF, py+ph/2+5, gh);

    show(wTopBg); show(wTopTxt);
    show(wBotBg); show(wBotTxt);
    show(hLftBg); show(hLftTxt);
    show(hRgtBg); show(hRgtTxt);

    /* ── tick-markeringer på blå linjer ── */
    // Øverste vandret kant: lodrette ticks
    for (let xi=x1+1; xi<x2; xi++) {{
      const t = mk('line',{{class:'tick',
        x1:xi*CELL, y1:y1*CELL-TICK_HALF,
        x2:xi*CELL, y2:y1*CELL+TICK_HALF}});
      ticks.appendChild(t);
    }}
    // Nederste vandret kant: lodrette ticks
    for (let xi=x1+1; xi<x2; xi++) {{
      const t = mk('line',{{class:'tick',
        x1:xi*CELL, y1:y2*CELL-TICK_HALF,
        x2:xi*CELL, y2:y2*CELL+TICK_HALF}});
      ticks.appendChild(t);
    }}
    // Venstre lodret kant: vandrette ticks
    for (let yi=y1+1; yi<y2; yi++) {{
      const t = mk('line',{{class:'tick',
        x1:x1*CELL-TICK_HALF, y1:yi*CELL,
        x2:x1*CELL+TICK_HALF, y2:yi*CELL}});
      ticks.appendChild(t);
    }}
    // Højre lodret kant: vandrette ticks
    for (let yi=y1+1; yi<y2; yi++) {{
      const t = mk('line',{{class:'tick',
        x1:x2*CELL-TICK_HALF, y1:yi*CELL,
        x2:x2*CELL+TICK_HALF, y2:yi*CELL}});
      ticks.appendChild(t);
    }}

  }} else {{
    /* ── Areal: kun bredde nedenunder og højde til højre ── */
    hide(wTopBg); hide(wTopTxt);
    hide(hLftBg); hide(hLftTxt);

    // Bredde: nedenunder, men over kant hvis rektangel går til bunden
    const wby = (y2 === GROWS) ? py-10 : py+ph+LABEL_OFF+5;
    placeLabel(wBotBg, wBotTxt, px+pw/2, wby, gw);
    show(wBotBg); show(wBotTxt);

    // Højde: til højre, men til venstre hvis rektangel går til kanten
    const hrx = (x2 === GCOLS) ? px-LABEL_OFF : px+pw+LABEL_OFF;
    placeLabel(hRgtBg, hRgtTxt, hrx, py+ph/2+5, gh);
    show(hRgtBg); show(hRgtTxt);
  }}
}}

/* ── koordinat-hjælpere ───────────────────────────────────── */
function toGrid(svgX, svgY) {{
  return {{
    x: Math.max(0, Math.min(GCOLS, Math.round(svgX/CELL))),
    y: Math.max(0, Math.min(GROWS, Math.round(svgY/CELL)))
  }};
}}
function evCoords(e) {{
  const r = svg.getBoundingClientRect();
  const s = e.touches ? e.touches[0] : e;
  return {{ x: s.clientX-r.left, y: s.clientY-r.top }};
}}

/* ── træk-logik ───────────────────────────────────────────── */
function onDown(e) {{
  if (!e.target.classList.contains('corner')) return;
  e.preventDefault();
  drag = {{ on:true, corner:e.target.getAttribute('data-corner') }};
  e.target.classList.add('dragging');
}}
function onMove(e) {{
  if (!drag.on) return;
  e.preventDefault();
  const g = toGrid(...Object.values(evCoords(e)));
  switch(drag.corner) {{
    case 'tl': if (g.x<R.x2&&g.y<R.y2){{R.x1=g.x;R.y1=g.y;}} break;
    case 'tr': if (g.x>R.x1&&g.y<R.y2){{R.x2=g.x;R.y1=g.y;}} break;
    case 'bl': if (g.x<R.x2&&g.y>R.y1){{R.x1=g.x;R.y2=g.y;}} break;
    case 'br': if (g.x>R.x1&&g.y>R.y1){{R.x2=g.x;R.y2=g.y;}} break;
  }}
  update();
}}
function onUp(e) {{
  if (!drag.on) return;
  e.preventDefault();
  Object.values(C).forEach(c=>c.classList.remove('dragging'));
  drag.on = false;
}}

svg.addEventListener('mousedown',  onDown);
svg.addEventListener('mousemove',  onMove);
svg.addEventListener('mouseup',    onUp);
svg.addEventListener('mouseleave', onUp);
svg.addEventListener('touchstart', onDown, {{passive:false}});
svg.addEventListener('touchmove',  onMove, {{passive:false}});
svg.addEventListener('touchend',   onUp,   {{passive:false}});
svg.addEventListener('touchcancel',onUp,   {{passive:false}});

update();
</script>
</body>
</html>"""

# Højde: SVG + plads til labels udenfor + wrap-padding
component_height = SVG_H + 180
components.html(html_code, height=component_height, scrolling=False)
