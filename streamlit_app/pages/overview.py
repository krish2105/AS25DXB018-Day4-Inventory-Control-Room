import plotly.graph_objects as go
import streamlit as st

from common import CLS, cls_color, insight, kpis, load, note, section, style, tok

d = load(); m = d["metrics"]; t = tok()
st.markdown(f"""<div class="hero"><div class="e">Retail chain · 500 SKUs</div>
<h2><span class="hl">{m['abc_A_items']}</span> items carry <span class="hl">{m['abc_A_value_pct']:.0f}%</span> of annual value.</h2>
<p>Two models classify items and forecast demand, then size each buffer at a 95% service level. Part B shows what every extra point of service costs.</p></div>""", unsafe_allow_html=True)

kpis([
    ("Total items", f"{m['n_items']:,}", "synthetic SKUs, seed 42", None),
    ("Class A", f"{m['abc_A_items']}", f"{m['abc_A_items_pct']:.1f}% of items · {m['abc_A_value_pct']:.1f}% of value", t["A"]),
    ("Class B", f"{m['abc_B_items']}", f"{m['abc_B_items_pct']:.1f}% of items · {m['abc_B_value_pct']:.1f}% of value", t["B"]),
    ("Class C", f"{m['abc_C_items']}", f"{m['abc_C_items_pct']:.1f}% of items · {m['abc_C_value_pct']:.1f}% of value", t["C"]),
    ("Decision tree accuracy", f"{d['tree']['acc_test']*100:.1f}%", f"test set, {d['tree']['test_n']} items · macro-F1 {m['tree_macro_f1']:.3f}", None),
    ("Forecast R²", f"{d['forecast']['r2_test']:.3f}", f"MAE {d['forecast']['mae_test']:.1f} · RMSE {d['forecast']['rmse_test']:.1f} units", None),
    ("Total safety stock", f"{d['safety_stock']['total']:,.0f}", f"units at 95% (Z = 1.65) · {m['ss_pct_demand']:.1f}% of demand", None),
    ("Total holding cost", f"{m['ba_B_after_hc']:.1f}", "per period, Part B policy A 97% · B 95% · C 98%", None),
])

c1, c2 = st.columns([2, 3], gap="large")
with c1:
    section("Value share by class", "Share of annual consumption value (usage × unit cost).")
    s = d["abc_summary"]
    fig = go.Figure(go.Pie(labels=[f"Class {x['Category']}" for x in s], values=[x["Value_%"] for x in s], hole=0.58, sort=False,
                           marker=dict(colors=[cls_color(x["Category"]) for x in s], line=dict(color=t["ring"], width=3)), textinfo="label+percent", textfont=dict(size=13)))
    st.plotly_chart(style(fig, 330, legend=False), use_container_width=True, config={"displayModeBar": False})
with c2:
    section("What the numbers say", "Insights drawn from the executed notebook.")
    insight(f"<b>Focus on class A.</b> {m['abc_A_items']} items ({m['abc_A_items_pct']:.0f}%) give {m['abc_A_value_pct']:.0f}% of value; class C ({m['abc_C_items_pct']:.0f}% of items) gives only {m['abc_C_value_pct']:.0f}%.", t["A"])
    insight(f"<b>The tree makes only neighbour mistakes.</b> {d['tree']['acc_test']*100:.1f}% accuracy; no A item was called C and no C item A. Class B is the hardest (F1 {m['tree_f1_B']:.2f}).", t["C"])
    insight(f"<b>Forecast gain is small.</b> Regression beats “same as last year” by only {m['mae_reduction_pct']:.1f}% in MAE on this synthetic data; it mainly reduces bias.", t["B"])
    insight(f"<b>Buffers follow value.</b> Class A holds {m['ss_A_share']:.0f}% of buffer units and {m['ss_A_value']/m['ss_total_value']*100:.0f}% of buffer value.", t["C"])
    insight(f"<b>Service is not free.</b> Going from 95% to 99% adds {m['B_inc_pct']:.1f}% to safety stock and holding cost for every product; the last point costs ≈ {m['marg_ratio']:.1f}× the first.", t["B"])
    insight(f"<b>Differentiate.</b> A 97% · B 95% · C 98% is {(1 - m['pol_Recommended_hc']/m['pol_Uniform_99_hc'])*100:.0f}% cheaper than a uniform 99% policy.", t["A"])
note(d["meta"]["note"] + " Every number on this dashboard is read from the executed notebook’s export (data/dashboard_data.json).")
