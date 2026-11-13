import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import CLS, confusion_fig, items_df, load, note, section, style, tok

d = load(); t = tok(); m = d["metrics"]; ba = d["before_after"]; df = items_df(d)
cls, fc = ba["classification"], ba["forecast"]
PILL = {"clear": "Clear gain", "marginal": "Marginal gain", "tradeoff": "Trade-off"}
pt = lambda k: f"{m[k]*100:.1f}%"
score = [
    ("Classification", "Accuracy (150 test items)", pt("ba_cls_acc_before"), pt("ba_cls_acc_after"), "clear"),
    ("Classification", "Class-A items flagged", f"{m['ba_cls_a_total']-m['ba_cls_a_missed_before']:.0f} of {m['ba_cls_a_total']:.0f}", f"{m['ba_cls_a_total']-m['ba_cls_a_missed_after']:.0f} of {m['ba_cls_a_total']:.0f}", "clear"),
    ("Forecast", "MAE (units)", f"{m['ba_fc_mae_before']:.1f}", f"{m['ba_fc_mae_after']:.1f}", "marginal"),
    ("Forecast", "Bias (units)", f"+{m['ba_fc_bias_before']:.1f}", f"+{m['ba_fc_bias_after']:.1f}", "marginal"),
    ("Safety stock", "Items below 90% service (same budget)", f"{m['ba_ss_below90_before']:.0f}", f"{m['ba_ss_below90_after']:.0f}", "clear"),
    ("Safety stock", "Lowest item service level", pt("ba_ss_csl_min_before"), pt("ba_ss_csl_min_after"), "clear"),
    ("Service levels (Part B)", "Holding cost per period", f"{m['ba_B_b95_hc']:.1f}", f"{m['ba_B_after_hc']:.1f}", "tradeoff"),
    ("Service levels (Part B)", "Expected units short per cycle", f"{m['ba_B_b95_short']:.2f}", f"{m['ba_B_after_short']:.2f}", "tradeoff"),
]
section("Before AI vs after AI – scorecard", "Before = the traditional way of working; after = the models built in this lab. Same items, same data. The verdict column is honest: not every comparison is a big win.")
body = "".join(f"<tr><td style='color:var(--muted)'>{a}</td><td>{b}</td><td class='r' style='color:var(--before)'>{c}</td><td class='r' style='color:var(--primary);font-weight:600'>{e}</td><td class='r'><span class='pill {v}'>{PILL[v]}</span></td></tr>" for a, b, c, e, v in score)
st.markdown(f"<div class='card' style='padding:.4rem .6rem'><table class='t'><tr><th>Area</th><th>Metric</th><th class='r'>Before AI</th><th class='r'>After AI</th><th class='r'>Verdict</th></tr>{body}</table></div>", unsafe_allow_html=True)

st.divider()
section("1 · Classification", "Before: rank items by annual usage only (top 20% = A, next 30% = B, rest = C), ignoring unit cost. After: decision tree. Both are scored against the value-based ABC class.")
c1, c2, c3 = st.columns(3, gap="medium")
c1.plotly_chart(confusion_fig(cls["before"]["confusion"], t["before"], "Before AI – usage-only rule", 320), use_container_width=True, config={"displayModeBar": False})
c2.plotly_chart(confusion_fig(cls["after"]["confusion"], t["after"], "After AI – decision tree", 320), use_container_width=True, config={"displayModeBar": False})
names = ["Accuracy", "Macro-F1", "Class-A recall"]; bv = [cls["before"]["accuracy"], cls["before"]["macro_f1"], cls["before"]["recall_A"]]; av = [cls["after"]["accuracy"], cls["after"]["macro_f1"], cls["after"]["recall_A"]]
fig = go.Figure([go.Bar(x=names, y=bv, name="Before AI", marker_color=t["before"], text=[f"{v:.2f}" for v in bv], textposition="outside"), go.Bar(x=names, y=av, name="After AI", marker_color=t["after"], text=[f"{v:.2f}" for v in av], textposition="outside")])
fig.update_layout(barmode="group"); fig.update_yaxes(range=[0, 1.1])
c3.plotly_chart(style(fig, 320), use_container_width=True, config={"displayModeBar": False})
st.caption(f"The usage-only rule misses {m['ba_cls_a_missed_before']:.0f} of {m['ba_cls_a_total']:.0f} class-A items; the tree misses {m['ba_cls_a_missed_after']:.0f}. The exact value-based ABC is perfect by definition but must be recomputed for the whole catalogue; the tree labels new items instantly.")

st.divider()
section("2 · Demand forecast", "Before: next year = last year (naive). After: linear regression. Same 150 test items; dashed line = perfect forecast.")
pts = pd.DataFrame(fc["points"])
c1, c2, c3 = st.columns(3, gap="medium")
for col, key, ttl, colr in ((c1, "before", "Before AI – naive (last year)", t["before"]), (c2, "after", "After AI – linear regression", t["after"])):
    f = go.Figure(go.Scatter(x=pts["actual"], y=pts[key], mode="markers", marker=dict(color=colr, size=7, opacity=0.65), text=pts["item"], hovertemplate="%{text}<br>actual %{x:,.0f} · forecast %{y:,.0f}<extra></extra>"))
    f.add_shape(type="line", x0=0, y0=0, x1=5600, y1=5600, line=dict(color=t["line"], dash="dash")); f.update_xaxes(title_text="Actual (units)", range=[0, 5600]); f.update_yaxes(range=[0, 5600])
    f.update_layout(title=dict(text=ttl, font=dict(size=13), x=0))
    col.plotly_chart(style(f, 330, legend=False), use_container_width=True, config={"displayModeBar": False})
mb = [fc["before"]["MAE"], fc["before"]["RMSE"], abs(fc["before"]["Bias"])]; ma = [fc["after"]["MAE"], fc["after"]["RMSE"], abs(fc["after"]["Bias"])]
f = go.Figure([go.Bar(x=["MAE", "RMSE", "|Bias|"], y=mb, name="Before AI", marker_color=t["before"], text=[f"{v:.1f}" for v in mb], textposition="outside"), go.Bar(x=["MAE", "RMSE", "|Bias|"], y=ma, name="After AI", marker_color=t["after"], text=[f"{v:.1f}" for v in ma], textposition="outside")])
f.update_layout(barmode="group"); f.update_yaxes(range=[0, 125])
c3.plotly_chart(style(f, 330), use_container_width=True, config={"displayModeBar": False})
st.caption(f"Honest result: MAE falls only {(1-m['ba_fc_mae_after']/m['ba_fc_mae_before'])*100:.1f}% and MAPE is slightly worse ({m['ba_fc_mape_before']:.2f}% → {m['ba_fc_mape_after']:.2f}%). The regression mainly removes the systematic under-forecast (bias {m['ba_fc_bias_before']:.1f} → {m['ba_fc_bias_after']:.1f} units).")

st.divider()
section("3 · Safety stock at the same budget", f"Before: one flat rule – buffer = {ba['safety_stock']['flat_pct']:.1f}% of last year’s demand for every item, lead time ignored. After: Z × σ × √LT. Both hold {m['ba_ss_units_after']:,.0f} units.")
bins = np.round(np.arange(0.80, 1.0001, 0.01), 2)
hb, _ = np.histogram(df["CSL_Before"], bins=bins); ha, _ = np.histogram(df["CSL_After"], bins=bins)
lab = [f"{int(b*100)}%" for b in bins[:-1]]
a, b = st.columns([2, 1], gap="large")
f = go.Figure([go.Bar(x=lab, y=hb, name="Before AI (flat rule)", marker_color=t["before"]), go.Bar(x=lab, y=ha, name="After AI (Z·σ·√LT)", marker_color=t["after"])])
f.update_layout(barmode="group", bargap=0.15); f.update_xaxes(title_text="Achieved service level of an item"); f.update_yaxes(title_text="Items")
a.plotly_chart(style(f, 360), use_container_width=True, config={"displayModeBar": False})
tab = pd.DataFrame({"Metric": ["Mean service level", "Lowest item", "Items < 90%", "Spread (sd, pp)", "Buffer units"],
                    "Before": [pt("ba_ss_csl_mean_before"), pt("ba_ss_csl_min_before"), f"{m['ba_ss_below90_before']:.0f}", f"{m['ba_ss_csl_sd_before']:.2f}", f"{m['ba_ss_units_before']:,.0f}"],
                    "After": [pt("ba_ss_csl_mean_after"), pt("ba_ss_csl_min_after"), f"{m['ba_ss_below90_after']:.0f}", f"{m['ba_ss_csl_sd_after']:.2f}", f"{m['ba_ss_units_after']:,.0f}"]})
b.dataframe(tab, hide_index=True, use_container_width=True)
st.caption("With the same inventory the AI rule moves units from short-lead-time items to long-lead-time, high-risk ones. Both rules are judged with the same assumed σ model, so this shows consistency of protection, not measured stock-outs.")

st.divider()
section("4 · Part B – one service level for everyone vs a differentiated policy", "Before: uniform 95% for all products. After: 97% / 95% / 98% for A / B / C. Grey square = before, green dot = after.")
curves = pd.DataFrame(d["partB"]["curves"]); rec = d["partB"]["recommendation"]["levels"]; ymax = float(np.ceil(curves[["Safety_Stock", "Holding_Cost"]].values.max() * 1.08 / 50) * 50)
fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=[f"Product {p}: 95% → {rec[p]:.0%}" for p in "ABC"], horizontal_spacing=0.03)
for i, p in enumerate("ABC", start=1):
    c = curves[curves.Product == p].sort_values("Service_Level")
    fig.add_trace(go.Scatter(x=c["Service_Level"], y=c["Safety_Stock"], mode="lines", line=dict(color=t["ss"], width=2.5), name="Safety Stock", showlegend=i == 1, legendgroup="s"), row=1, col=i)
    fig.add_trace(go.Scatter(x=c["Service_Level"], y=c["Holding_Cost"], mode="lines", line=dict(color=t["hc"], width=2.5), name="Holding Cost", showlegend=i == 1, legendgroup="h"), row=1, col=i)
    hc = lambda s: float(c.loc[np.isclose(c["Service_Level"], s), "Holding_Cost"].iloc[0])
    fig.add_trace(go.Scatter(x=[0.95], y=[hc(0.95)], mode="markers", marker=dict(symbol="square", size=13, color=t["before"], line=dict(color=t["ring"], width=2)), name="Before AI: 95%", showlegend=i == 1, legendgroup="b"), row=1, col=i)
    fig.add_trace(go.Scatter(x=[rec[p]], y=[hc(rec[p])], mode="markers", marker=dict(symbol="circle", size=14, color=t["after"], line=dict(color=t["ring"], width=2)), name="After AI: recommended", showlegend=i == 1, legendgroup="a"), row=1, col=i)
    fig.update_xaxes(range=[0.795, 0.995], tickvals=[0.8, 0.85, 0.9, 0.95, 0.99], ticktext=["80%", "85%", "90%", "95%", "99%"], row=1, col=i)
fig.update_yaxes(range=[0, ymax])
style(fig, 430)
fig.update_layout(legend=dict(orientation="h", y=-0.16, x=0))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
c1, c2, c3 = st.columns(3, gap="medium")
tot = d["partB"]["before_after_totals"]
for col, key, ttl, dec in ((c1, "Total_Safety_Stock", "Safety stock", 0), (c2, "Total_Holding_Cost", "Holding cost per period", 0), (c3, "Total_Units_Short_per_Cycle", "Expected units short / cycle", 2)):
    vals = [x[key] for x in tot]
    f = go.Figure(go.Bar(x=["Uniform 95%", "Differentiated", "Uniform 99%"], y=vals, marker_color=[t["before"], t["after"], t["C"]], text=[f"{v:.{dec}f}" for v in vals], textposition="outside"))
    f.update_layout(title=dict(text=ttl, font=dict(size=13), x=0)); f.update_yaxes(range=[0, max(vals) * 1.2])
    col.plotly_chart(style(f, 300, legend=False), use_container_width=True, config={"displayModeBar": False})
st.caption(f"Trade-off, not a free win: the differentiated policy costs {m['ba_B_after_hc']-m['ba_B_b95_hc']:.0f} more per period ({(m['ba_B_after_hc']/m['ba_B_b95_hc']-1)*100:.0f}%) and cuts expected shortage by {(1-m['ba_B_after_short']/m['ba_B_b95_short'])*100:.0f}%. Product B keeps {m['ba_B_after_B_short']/m['ba_B_after_short']*100:.0f}% of the remaining shortage – reduce its variability instead of adding buffer.")
note("“After AI” for Part B means a data-driven, simulation-based policy built on assumed parameters and a 15-unit cost tolerance, not a model trained on real data.")
