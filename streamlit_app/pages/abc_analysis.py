import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import CLS, cls_color, items_df, kpis, load, note, section, style, tok

d = load(); t = tok(); df = items_df(d)

section("Pareto chart – annual consumption value", "Bars: annual value per item, ranked. Line: cumulative share of total value. Dashed lines mark the 70% (A/B) and 90% (B/C) cut-offs.")
hl = st.radio("Highlight class", ["All", "A", "B", "C"], horizontal=True, label_visibility="collapsed")
colors = [cls_color(c) if hl in ("All", c) else "rgba(128,128,128,0.18)" for c in df["ABC_Category"]]
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=df["Rank"], y=df["Annual_Value"], marker_color=colors, name="Annual value", hovertemplate="Rank %{x}<br>%{y:,.0f}<extra></extra>"), secondary_y=False)
fig.add_trace(go.Scatter(x=df["Rank"], y=df["Cumulative%"], mode="lines", line=dict(color=t["line"], width=2.5), name="Cumulative % of value", hovertemplate="Rank %{x}<br>%{y:.1f}%<extra></extra>"), secondary_y=True)
for y in (70, 90):
    fig.add_hline(y=y, line=dict(color=t["line"], dash="dash", width=1), secondary_y=True, annotation_text=f"{y}%", annotation_position="top left")
fig.update_yaxes(title_text="Annual value", secondary_y=False); fig.update_yaxes(title_text="Cumulative % of value", range=[0, 102], ticksuffix="%", secondary_y=True, showgrid=False)
fig.update_xaxes(title_text="Items ranked by annual value (1 = highest)")
fig.update_layout(bargap=0)
st.plotly_chart(style(fig, 420), use_container_width=True, config={"displayModeBar": False})

c1, c2 = st.columns([2, 3], gap="large")
with c1:
    section("Category distribution", "Number of items per class.")
    s = d["abc_summary"]
    fig = go.Figure(go.Pie(labels=[f"Class {x['Category']}" for x in s], values=[x["Items"] for x in s], hole=0.55, sort=False,
                           marker=dict(colors=[cls_color(x["Category"]) for x in s], line=dict(color=t["ring"], width=3)), textinfo="label+value"))
    st.plotly_chart(style(fig, 300, legend=False), use_container_width=True, config={"displayModeBar": False})
with c2:
    section("Share of items vs share of value", "The ‘vital few, trivial many’ pattern.")
    fig = go.Figure()
    fig.add_bar(x=[f"Class {x['Category']}" for x in s], y=[x["Items_%"] for x in s], name="% of items", marker_color=t["before"], text=[f"{x['Items_%']:.1f}%" for x in s], textposition="outside")
    fig.add_bar(x=[f"Class {x['Category']}" for x in s], y=[x["Value_%"] for x in s], name="% of annual value", marker_color=[cls_color(x["Category"]) for x in s], text=[f"{x['Value_%']:.1f}%" for x in s], textposition="outside")
    fig.update_layout(barmode="group"); fig.update_yaxes(ticksuffix="%", range=[0, 82])
    st.plotly_chart(style(fig, 300), use_container_width=True, config={"displayModeBar": False})

section("Items", "Search, filter and sort; the table downloads as CSV.")
f1, f2 = st.columns([1, 3])
cls_sel = f1.multiselect("Class", CLS, default=CLS)
q = f2.text_input("Search SKU", placeholder="e.g. SKU_210")
view = df[df["ABC_Category"].isin(cls_sel)]
if q.strip():
    view = view[view["Item"].str.contains(q.strip(), case=False)]
show = view[["Rank", "Item", "Annual_Usage", "Unit_Cost", "Lead_Time", "Annual_Value", "Cumulative%", "ABC_Category", "Predicted_ABC"]].rename(
    columns={"Annual_Usage": "Usage", "Unit_Cost": "Unit cost", "Lead_Time": "Lead time", "Annual_Value": "Annual value", "Cumulative%": "Cum. %", "ABC_Category": "Class", "Predicted_ABC": "AI class"})
st.caption(f"{len(show):,} of {len(df):,} items shown")
if show.empty:
    st.info("No items match. Clear the search or choose another class.")
else:
    st.dataframe(show, hide_index=True, use_container_width=True, height=420,
                 column_config={"Annual value": st.column_config.NumberColumn(format="%,.0f"), "Usage": st.column_config.NumberColumn(format="%,d"),
                                "Unit cost": st.column_config.NumberColumn(format="%.2f"), "Cum. %": st.column_config.NumberColumn(format="%.1f%%")})
    st.download_button("⬇ Export CSV", show.to_csv(index=False).encode(), file_name="abc_items.csv", mime="text/csv", type="primary")
