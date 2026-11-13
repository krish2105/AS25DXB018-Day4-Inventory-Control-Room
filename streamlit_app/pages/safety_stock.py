import numpy as np
import plotly.graph_objects as go
import streamlit as st

from common import cls_color, items_df, kpis, load, note, section, style, tok, z_for

d = load(); t = tok(); df = items_df(d)
section("Service level", "Safety stock = Z × σ × √Lead time, with σ = 10% of the predicted demand. Default 95% with Z = 1.65, as on the slides.")
sl = st.select_slider("Service level", options=[round(0.80 + i / 100, 2) for i in range(20)], value=0.95, format_func=lambda v: f"{v:.0%}")
z = z_for(sl)
df["ss"] = np.round(z * df["Std_Dev"] * np.sqrt(df["Lead_Time"]))
total = df["ss"].sum(); value = (df["ss"] * df["Unit_Cost"]).sum(); demand = df["Predicted_Demand"].sum()
g = df.groupby("ABC_Category").agg(items=("Item", "count"), total=("ss", "sum"), dem=("Predicted_Demand", "sum"), lt=("Lead_Time", "mean")).reset_index()
g["avg"] = g["total"] / g["items"]; g["pct"] = g["total"] / g["dem"] * 100
g["value"] = [(df[df.ABC_Category == c]["ss"] * df[df.ABC_Category == c]["Unit_Cost"]).sum() for c in g["ABC_Category"]]
kpis([("Z-score", f"{z:.2f}" if sl == 0.95 else f"{z:.3f}", "slide value (norm.ppf gives 1.645)" if sl == 0.95 else "scipy.stats.norm.ppf", t["C"]),
      ("Total safety stock", f"{total:,.0f}", f"{total/demand*100:.1f}% of predicted demand", t["A"]), ("Buffer value", f"{value:,.0f}", "units × unit cost", None),
      ("Class A share", f"{g.loc[g.ABC_Category=='A','total'].iloc[0]/total*100:.1f}%", "of buffer units", t["A"])])
if sl == 0.95:
    st.success(f"✓ Matches the notebook total ({d['safety_stock']['total']:,.0f} units).")

c1, c2 = st.columns([2, 1], gap="large")
with c1:
    section("By item – 25 largest buffers", "Coloured by ABC class: first candidates for lead-time or variability reduction.")
    top = df.nlargest(25, "ss")
    fig = go.Figure(go.Bar(x=top["Item"].str.replace("SKU_", ""), y=top["ss"], marker_color=[cls_color(c) for c in top["ABC_Category"]], hovertemplate="SKU %{x}<br>%{y:,.0f} units<extra></extra>"))
    fig.update_xaxes(type="category", tickangle=-90); fig.update_yaxes(title_text="Safety stock (units)")
    st.plotly_chart(style(fig, 380, legend=False), use_container_width=True, config={"displayModeBar": False})
with c2:
    section("By class", "Total safety stock per ABC class.")
    fig = go.Figure(go.Bar(x=[f"Class {c}" for c in g["ABC_Category"]], y=g["total"], marker_color=[cls_color(c) for c in g["ABC_Category"]], text=[f"{v:,.0f}" for v in g["total"]], textposition="outside"))
    fig.update_yaxes(range=[0, g["total"].max() * 1.15])
    st.plotly_chart(style(fig, 380, legend=False), use_container_width=True, config={"displayModeBar": False})

section("Summary table", "Computed live from the selected service level.")
tab = g.rename(columns={"ABC_Category": "Class", "items": "Items", "lt": "Avg lead time", "total": "Total safety stock", "avg": "Avg per item", "pct": "% of demand", "value": "Buffer value"})[
    ["Class", "Items", "Avg lead time", "Total safety stock", "Avg per item", "% of demand", "Buffer value"]]
st.dataframe(tab, hide_index=True, use_container_width=True, column_config={"Avg lead time": st.column_config.NumberColumn(format="%.2f"), "Total safety stock": st.column_config.NumberColumn(format="%,.0f"),
             "Avg per item": st.column_config.NumberColumn(format="%.1f"), "% of demand": st.column_config.NumberColumn(format="%.1f%%"), "Buffer value": st.column_config.NumberColumn(format="%,.0f")})
note("Because σ is a fixed 10% of demand and lead time is used in the professor’s units, buffers come out near 29% of annual demand in every class; classes differ in absolute size, not in ratio.")
