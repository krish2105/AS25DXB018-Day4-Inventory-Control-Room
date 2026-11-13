import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from scipy.stats import norm

from common import kpis, load, note, section, style, tok

d = load(); t = tok()
P = ["A", "B", "C"]
levels = np.array(d["partB"]["service_levels"])
DEF = {p["Product"]: dict(mean=float(p["Avg_Demand"]), cv=float(p["Demand_Std"]) / float(p["Avg_Demand"]) * 100, lead=int(p["Lead_Time"]), h=float(p["Holding_Cost"])) for p in d["partB"]["parameters"]}
TOL0 = d["partB"]["recommendation"]["tolerance"]
pcol = {"A": t["A"], "B": t["B"], "C": t["C"]}


def reset():
    for p in P:
        for k, v in DEF[p].items():
            st.session_state[f"{p}_{k}"] = v
    st.session_state["sl"] = 95; st.session_state["tol"] = TOL0


if "sl" not in st.session_state:
    reset()

section("What-if parameters", "Change any product’s demand, variability, lead time or holding cost. Everything below recalculates instantly with Safety stock = Z × σ × √Lead time and Holding cost = Safety stock × cost per unit.")
st.button("↺ Reset to notebook values", on_click=reset)
cols = st.columns(3, gap="large")
params = {}
for p, c in zip(P, cols):
    with c:
        with st.container(border=True):
            st.markdown(f"**<span style='color:{pcol[p]}'>●</span> Product {p}**", unsafe_allow_html=True)
            mean = st.slider("Mean demand (units / period)", 50.0, 800.0, step=5.0, key=f"{p}_mean")
            cv = st.slider("Demand variability (CV %)", 1.0, 40.0, step=0.01, key=f"{p}_cv", format="%.1f")
            lead = st.slider("Lead time (periods)", 1, 12, step=1, key=f"{p}_lead")
            h = st.slider("Holding cost (per unit / period)", 0.5, 5.0, step=0.05, key=f"{p}_h", format="%.2f")
            params[p] = dict(mean=mean, cv=cv, lead=lead, h=h)
            sig = mean * cv / 100
            st.caption(f"σ = {sig:,.1f} · σ√L = {sig*np.sqrt(lead):,.1f}")
g1, g2 = st.columns(2, gap="large")
slp = g1.slider("Service level (marker on the charts)", 80, 99, step=1, key="sl", format="%d%%")
tol = g2.slider("Recommendation tolerance (extra holding cost allowed per +1 pp)", 2, 60, step=1, key="tol")
sl = slp / 100


def curve(q):
    sigma = q["mean"] * q["cv"] / 100
    z = norm.ppf(levels)
    ss = z * sigma * np.sqrt(q["lead"])
    return z, ss, ss * q["h"]


C = {p: curve(params[p]) for p in P}
ymax = max(max(C[p][1].max(), C[p][2].max()) for p in P)
at = lambda p, s: int(np.argmin(np.abs(levels - s)))
is_default = all(abs(params[p][k] - DEF[p][k]) < 1e-9 for p in P for k in DEF[p])
# match against the notebook's B4 table (JSON stores 4 decimals)
curves = pd.DataFrame(d["partB"]["curves"]); maxdiff = 0.0
for p in P:
    z0, ss0, hc0 = curve(DEF[p]); r = curves[curves.Product == p].sort_values("Service_Level")
    maxdiff = max(maxdiff, np.abs(ss0 - r["Safety_Stock"].values).max(), np.abs(hc0 - r["Holding_Cost"].values).max())

section("Service Level Trade-offs in Inventory Optimization", "Product A | B | C on one y-scale. Blue = safety stock (units), green = holding cost. The dashed line is the selected service level.")
if is_default:
    (st.success if maxdiff < 1e-4 else st.warning)(f"{'✓ Matches notebook' if maxdiff < 1e-4 else 'Δ vs notebook'} (max Δ {maxdiff:.0e}, JSON rounding)")
else:
    st.caption("Custom parameters – reset to compare with the notebook.")
fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=[f"Product {p}" for p in P], horizontal_spacing=0.03)
ymaxr = int(np.ceil(ymax * 1.08 / 50) * 50)
for i, p in enumerate(P, start=1):
    z, ss, hc = C[p]
    lg = "legend" if i == 1 else f"legend{i}"
    fig.add_trace(go.Scatter(x=levels, y=ss, mode="lines", name="Safety Stock", line=dict(color=t["ss"], width=3), legend=lg, hovertemplate="%{x:.0%}: %{y:.1f} units<extra>Safety stock</extra>"), row=1, col=i)
    fig.add_trace(go.Scatter(x=levels, y=hc, mode="lines", name="Holding Cost", line=dict(color=t["hc"], width=3), legend=lg, hovertemplate="%{x:.0%}: %{y:.1f}<extra>Holding cost</extra>"), row=1, col=i)
    k = at(p, sl)
    fig.add_trace(go.Scatter(x=[sl, sl], y=[ss[k], hc[k]], mode="markers", marker=dict(size=9, color=[t["ss"], t["hc"]], line=dict(color=t["ring"], width=2)), showlegend=False, hoverinfo="skip"), row=1, col=i)
    fig.add_vline(x=sl, line=dict(color=t["line"], dash="dash", width=1), opacity=0.5, row=1, col=i)
    fig.update_xaxes(range=[0.795, 0.995], tickvals=[0.8, 0.85, 0.9, 0.95, 0.99], ticktext=["80%", "85%", "90%", "95%", "99%"], title_text="Service Level", row=1, col=i)
fig.update_yaxes(range=[0, ymaxr], title_text="Units / Cost", row=1, col=1)
style(fig, 430)
fig.update_layout(showlegend=True, legend=dict(x=0.0, y=0.98, xanchor="left", yanchor="top", bgcolor="rgba(0,0,0,0)"), legend2=dict(x=0.355, y=0.98, xanchor="left", yanchor="top", bgcolor="rgba(0,0,0,0)"),
                  legend3=dict(x=0.71, y=0.98, xanchor="left", yanchor="top", bgcolor="rgba(0,0,0,0)"), margin=dict(t=50))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.caption("Both curves bend upward: safety stock grows with Z, and Z grows faster the closer the service level gets to 100%. Products differ because σ√L and the holding cost per unit differ.")

section("Comparison at 80 / 90 / 95 / 99%", "Safety stock (SS, units) and holding cost (HC) with the increase from 95% to 99%.")
rows = []
for p in P:
    z, ss, hc = C[p]; r = {"Product": p}
    for s in (0.8, 0.9, 0.95, 0.99): r[f"SS {int(s*100)}%"] = ss[at(p, s)]
    for s in (0.8, 0.9, 0.95, 0.99): r[f"HC {int(s*100)}%"] = hc[at(p, s)]
    r["SS 95→99%"] = (ss[at(p, 0.99)] / ss[at(p, 0.95)] - 1) * 100
    rows.append(r)
st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, column_config={**{k: st.column_config.NumberColumn(format="%.1f") for k in rows[0] if k[:2] in ("SS", "HC")}, "SS 95→99%": st.column_config.NumberColumn(format="+%.1f%%")})
st.caption("The relative increase is the same for every product (Z(99%)/Z(95%) − 1); only the absolute amounts differ.")


def rec_level(hc):
    best = 0.8
    for i in range(1, len(levels)):
        if hc[i] - hc[i - 1] <= tol: best = float(levels[i])
    return best


rec = {p: rec_level(C[p][2]) for p in P}
def policy(lv): return sum(C[p][1][at(p, lv[p])] for p in P), sum(C[p][2][at(p, lv[p])] for p in P)
u95, rc, u99 = policy({p: 0.95 for p in P}), policy(rec), policy({p: 0.99 for p in P})
section("Portfolio policies", "Total safety stock and holding cost for the three products.")
st.dataframe(pd.DataFrame({"Policy": ["Uniform 95%", f"Recommended ({' / '.join(str(round(rec[p]*100)) for p in P)}%)", "Uniform 99%"],
                           "Safety stock": [u95[0], rc[0], u99[0]], "Holding cost / period": [u95[1], rc[1], u99[1]]}), hide_index=True, use_container_width=True,
             column_config={"Safety stock": st.column_config.NumberColumn(format="%.1f"), "Holding cost / period": st.column_config.NumberColumn(format="%.1f")})
st.caption(f"Recommended is {(1-rc[1]/u99[1])*100:.0f}% cheaper than a uniform 99% policy and {rc[1]-u95[1]:.1f} dearer than uniform 95%.")

section("Recommended service level per product", f"Rule: raise the service level while the next +1 percentage point costs at most {tol} holding-cost units.")
cs = st.columns(3, gap="large")
notes = {"A": "Stable, high volume: protect it while the price per point stays low.", "B": "Volatile and long lead time – every point is costly. Cut variability rather than add buffer.", "C": "Small buffer, so high service is cheap in absolute terms."}
for p, c in zip(P, cs):
    k = at(p, rec[p]); z, ss, hc = C[p]; extra = hc[at(p, 0.99)] - hc[k]
    c.markdown(f"""<div class="rec"><span class="bar" style="background:{pcol[p]}"></span><div class="lab">Product {p}</div>
<div class="big">{round(rec[p]*100)}%</div><div class="row"><div>Safety stock<br><b>{ss[k]:.1f}</b></div><div>Holding cost<br><b>{hc[k]:.1f}</b></div>
<div>+ to reach 99%<br><b>{extra:.1f}</b></div></div><div class="txt">{notes[p]}</div></div>""", unsafe_allow_html=True)
