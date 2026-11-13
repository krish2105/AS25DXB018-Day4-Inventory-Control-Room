"""Shared design system + data loading for the Streamlit dashboard (mirrors the Next.js app)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "dashboard_data.json"
if not DATA.exists():                       # fallback when the folder is deployed on its own
    DATA = Path(__file__).resolve().parent / "data" / "dashboard_data.json"

# Mode-neutral series colours for Plotly (>= 3:1 on both the light and the dark surface).
# Text, grid and surfaces come from the CSS variables below / Streamlit's own theme, which flip instantly with the Settings toggle.
P = dict(A="#1a9468", B="#cf8a17", C="#6b8cab", before="#8393a1", after="#1a9468", ss="#2f7de1", hc="#22a552", primary="#1a9468",
         ring="rgba(128,128,128,0.28)", line="#7f948a", soft="rgba(26,148,104,0.22)", grid="rgba(128,128,128,0.18)")
CLS = ["A", "B", "C"]


def tok() -> dict:
    return P


@st.cache_data(show_spinner="Loading results…")
def load() -> dict:
    with open(DATA) as f:
        return json.load(f)


def setup(title: str, icon: str = "📦"):
    st.set_page_config(page_title=f"{title} · Inventory Control Room", page_icon=icon, layout="wide", initial_sidebar_state="expanded")
    css()


def css():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@500;600&display=swap');
/* Tokens use light-dark(): they follow Streamlit's own theme switch instantly (no script rerun needed). */
.stApp {
  --bg: light-dark(#f5faf7, #07130e); --card: light-dark(#ffffff, #0e1d16); --fg: light-dark(#0b1f17, #e8f4ed); --muted: light-dark(#4d665a, #93ae9f);
  --border: light-dark(#d8e6de, #1f382c); --primary: light-dark(#0e7a55, #3dd598); --on-primary: light-dark(#ffffff, #04140d); --soft: light-dark(#e6f4ec, #14281f);
  --forest: light-dark(#0a3d2c, #0a2519); --cA: light-dark(#0e7a55, #3dd598); --cB: light-dark(#c98a1d, #f0b34a); --cC: light-dark(#5c7c99, #8fb0cc);
  --before: light-dark(#7a8a99, #8a9aa8);
  --shadow: light-dark(0 1px 2px rgb(11 31 23 / .05), 0 1px 2px rgb(0 0 0 / .4)), light-dark(0 8px 24px -12px rgb(14 122 85 / .18), 0 12px 32px -16px rgb(0 0 0 / .7));
}
html, body, [class*="css"], .stApp, .stMarkdown, p, label, li { font-family:'Geist', system-ui, sans-serif !important; }
.stApp { background:var(--bg); color:var(--fg); transition:background-color .3s ease, color .3s ease; }
.block-container { padding-top:0 !important; padding-bottom:3rem; max-width:1280px; }
header[data-testid="stHeader"] { background:transparent; }
.stAppDeployButton, [data-testid="stAppDeployButton"] { display:none !important; }
h1,h2,h3 { letter-spacing:-0.02em; color:var(--fg); }
.num { font-family:'Geist Mono', ui-monospace, monospace !important; font-variant-numeric:tabular-nums; letter-spacing:-0.02em; }
.band { margin:0 -4rem 1.5rem -4rem; padding:1.25rem 4rem; color:#e9f7ef; display:flex; flex-wrap:wrap; gap:1rem; align-items:center; justify-content:space-between;
  background-color:var(--forest); background-image:radial-gradient(ellipse at 85% -20%, rgba(61,213,152,.28), transparent 55%), radial-gradient(rgba(255,255,255,.07) 1px, transparent 1px); background-size:auto,18px 18px; }
.band .eyebrow { font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:#a7e8c9; font-weight:500; }
.band h1 { margin:0; padding:0; font-size:1.7rem; font-weight:600; color:#fff; line-height:1.15; }
.band .who { text-align:right; font-size:12.5px; line-height:1.5; color:#cdeede; } .band .who b { color:#fff; }
.band .brand { display:flex; gap:.8rem; align-items:center; }
.card { background:var(--card); border:1px solid var(--border); border-radius:18px; padding:1.25rem 1.4rem; box-shadow:var(--shadow); }
.kgrid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1rem; margin:.5rem 0 1.25rem; }
.kpi { position:relative; overflow:hidden; background:var(--card); border:1px solid var(--border); border-radius:18px; padding:1.1rem 1.25rem; box-shadow:var(--shadow); }
.kpi .bar { position:absolute; left:0; top:0; bottom:0; width:4px; }
.kpi .l { font-size:12px; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); font-weight:500; }
.kpi .v { font-family:'Geist Mono',monospace; font-size:2rem; font-weight:600; color:var(--fg); margin-top:.5rem; line-height:1; letter-spacing:-0.03em; }
.kpi .s { font-size:13.5px; color:var(--muted); margin-top:.5rem; }
.hero { background:var(--card); border:1px solid var(--border); border-radius:18px; padding:1.4rem 1.6rem; box-shadow:var(--shadow); margin-bottom:1.25rem; }
.hero .e { font-size:12px; letter-spacing:.07em; text-transform:uppercase; color:var(--primary); font-weight:600; }
.hero h2 { font-size:1.9rem; margin:.3rem 0 .4rem 0; padding:0; font-weight:600; }
.hero h2 .hl { color:var(--primary); font-family:'Geist Mono',monospace; } .hero p { color:var(--muted); margin:0; max-width:46rem; }
.insight { display:flex; gap:.75rem; background:var(--soft); border:1px solid var(--border); border-radius:12px; padding:.7rem .9rem; margin-bottom:.55rem; font-size:.95rem; line-height:1.5; }
.insight i { margin-top:.5rem; width:8px; height:8px; border-radius:99px; flex:0 0 8px; }
.note { border:1px dashed var(--border); background:var(--soft); color:var(--muted); border-radius:12px; padding:.55rem .85rem; font-size:.8rem; margin:.6rem 0; }
.pill { display:inline-block; padding:.15rem .6rem; border-radius:99px; font-size:.75rem; font-weight:600; }
.pill.clear { background:color-mix(in srgb, var(--primary) 18%, transparent); color:var(--primary); }
.pill.marginal { background:color-mix(in srgb, var(--cB) 20%, transparent); color:var(--cB); }
.pill.tradeoff { background:color-mix(in srgb, var(--cC) 22%, transparent); color:var(--cC); }
table.t { width:100%; border-collapse:collapse; font-size:.9rem; }
table.t th { text-align:left; font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); background:var(--soft); padding:.55rem .7rem; }
table.t td { padding:.55rem .7rem; border-top:1px solid var(--border); }
table.t td.r, table.t th.r { text-align:right; font-family:'Geist Mono',monospace; }
.rec { position:relative; overflow:hidden; background:var(--card); border:1px solid var(--border); border-radius:18px; padding:1.2rem 1.3rem; box-shadow:var(--shadow); height:100%; }
.rec .bar { position:absolute; left:0; top:0; bottom:0; width:4px; }
.rec .big { font-family:'Geist Mono',monospace; font-size:2.6rem; font-weight:600; color:var(--primary); line-height:1.1; }
.rec .lab { font-size:12px; letter-spacing:.07em; text-transform:uppercase; color:var(--muted); }
.rec .row { display:flex; gap:1.2rem; margin:.6rem 0; font-size:12px; color:var(--muted); } .rec .row b { font-family:'Geist Mono',monospace; font-size:15px; color:var(--fg); }
.rec .txt { color:var(--muted); font-size:.92rem; }
.foot { margin-top:3rem; padding-top:1.1rem; border-top:1px solid var(--border); display:flex; flex-wrap:wrap; justify-content:space-between; gap:.5rem; color:var(--muted); font-size:.85rem; }
.foot b { color:var(--fg); }
div[data-testid="stMetric"] { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:.6rem .9rem; }
section[data-testid="stSidebar"] { border-right:1px solid var(--border); }
.stButton>button, .stDownloadButton>button { border-radius:10px; font-weight:600; min-height:2.6rem; }
@media (max-width:760px) { .band { margin:0 -1rem 1rem -1rem; padding:1rem; } .band .who { text-align:left; } }
</style>
""",
        unsafe_allow_html=True,
    )


LOGO = """<svg width="42" height="42" viewBox="0 0 48 48" fill="none"><rect width="48" height="48" rx="12" fill="rgba(61,213,152,.16)" stroke="rgba(61,213,152,.5)"/>
<path d="M24 9 36 15.5v13L24 35 12 28.5v-13L24 9Z" fill="#3dd598"/><path d="M24 9v13m0 0 12-6.5M24 22 12 15.5" stroke="#0a3d2c" stroke-width="1.8" stroke-linejoin="round"/>
<rect x="10" y="33" width="28" height="5" rx="2.5" fill="#e8f4ed"/><rect x="10" y="33" width="17" height="5" rx="2.5" fill="#3dd598" opacity=".55"/></svg>"""


def header(d: dict, subtitle: str = "AI in Operations · Day 4"):
    m = d["meta"]
    st.markdown(
        f"""<div class="band"><div class="brand">{LOGO}<div><div class="eyebrow">{subtitle}</div><h1>Inventory Control Room</h1></div></div>
<div class="who"><b>{m['name']} · <span class="num">{m['enrollment_id']}</span></b><br>{m['program']} · {m['professor']}</div></div>""",
        unsafe_allow_html=True,
    )


def footer(d: dict):
    m = d["meta"]
    st.markdown(
        f"""<div class="foot"><span><b>{m['name']}</b> | <span class="num">{m['enrollment_id']}</span> | MAIB Sept 2025</span>
<span>{m['task']} · {m['date']}. Part A data are synthetic (seed 42); Part B parameters are assumptions.</span></div>""",
        unsafe_allow_html=True,
    )


def kpis(items: list[tuple]):
    """items: (label, value, sub, accent_color|None)"""
    html = '<div class="kgrid">'
    for label, value, sub, accent in items:
        bar = f'<span class="bar" style="background:{accent}"></span>' if accent else ""
        html += f'<div class="kpi">{bar}<div class="l">{label}</div><div class="v">{value}</div><div class="s">{sub}</div></div>'
    st.markdown(html + "</div>", unsafe_allow_html=True)


def insight(text: str, color: str):
    st.markdown(f'<div class="insight"><i style="background:{color}"></i><span>{text}</span></div>', unsafe_allow_html=True)


def note(text: str):
    st.markdown(f'<div class="note">ⓘ {text}</div>', unsafe_allow_html=True)


def section(title: str, desc: str = ""):
    st.markdown(f"### {title}")
    if desc:
        st.caption(desc)


def cls_color(c: str) -> str:
    return P[c]


def style(fig: go.Figure, h: int = 380, legend: bool = True) -> go.Figure:
    """Neutral Plotly styling: transparent surfaces; text/axis colours are supplied by Streamlit's theme so they flip with the toggle."""
    fig.update_layout(
        height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Geist, system-ui, sans-serif", size=12),
        margin=dict(l=10, r=10, t=40, b=10), showlegend=legend, legend=dict(orientation="h", y=1.1, x=0, font=dict(size=12)),
    )
    fig.update_xaxes(gridcolor=P["grid"], zerolinecolor=P["grid"], linecolor=P["grid"])
    fig.update_yaxes(gridcolor=P["grid"], zerolinecolor=P["grid"], linecolor=P["grid"])
    return fig


def items_df(d: dict) -> pd.DataFrame:
    return pd.DataFrame(d["items"])


def z_for(sl: float) -> float:
    return 1.65 if abs(sl - 0.95) < 1e-9 else float(norm.ppf(sl))


def confusion_fig(cm, hue: str, title: str, h: int = 330) -> go.Figure:
    z = np.array(cm)
    rgb = hue.lstrip("#"); r, g, b = (int(rgb[i:i + 2], 16) for i in (0, 2, 4))
    fig = go.Figure(go.Heatmap(z=z, x=[f"Pred {c}" for c in CLS], y=[f"Actual {c}" for c in CLS], text=z, texttemplate="%{text}", textfont=dict(size=22, family="Geist Mono"),
                               colorscale=[[0, "rgba(128,128,128,0.08)"], [1, f"rgba({r},{g},{b},0.55)"]], showscale=False, xgap=5, ygap=5, hovertemplate="%{y} → %{x}: %{z}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    correct = int(np.trace(z)); total = int(z.sum())
    style(fig, h, legend=False)
    fig.update_layout(title=dict(text=f"{title} · {correct} of {total} correct ({correct / total:.1%})", font=dict(size=13), x=0))
    return fig
