import plotly.graph_objects as go
import streamlit as st

from common import CLS, cls_color, confusion_fig, items_df, kpis, load, note, section, style, tok

d = load(); t = tok(); T = d["tree"]; F = d["forecast"]; df = items_df(d)
kpis([
    ("Test accuracy", f"{T['acc_test']*100:.1f}%", f"train {T['acc_train']*100:.1f}% · mild overfit", t["A"]),
    ("Split", f"{T['train_n']}/{T['test_n']}", "stratified 70 / 30 · seed 42", None),
    ("Tree depth · leaves", f"{T['depth']} · {T['leaves']}", "depth chosen by 5-fold CV", None),
    ("Forecast R² (test)", f"{F['r2_test']:.3f}", f"MAE {F['mae_test']:.1f} · RMSE {F['rmse_test']:.1f}", t["C"]),
])
c1, c2 = st.columns(2, gap="large")
with c1:
    section("Decision tree – confusion matrix", "Test set (150 items). Every mistake is between neighbouring classes.")
    st.plotly_chart(confusion_fig(T["confusion"], t["primary"], "Decision tree, test set"), use_container_width=True, config={"displayModeBar": False})
with c2:
    section("Feature importances", "Lead time barely matters because ABC depends on usage × cost.")
    names = {"Annual_Usage": "Annual usage", "Unit_Cost": "Unit cost", "Lead_Time": "Lead time", "Past_Demand": "Past demand"}
    imp = sorted(T["importances"], key=lambda x: x["importance"])
    fig = go.Figure(go.Bar(x=[x["importance"] for x in imp], y=[names[x["feature"]] for x in imp], orientation="h", marker_color=[t["primary"] if i == len(imp) - 1 else t["soft"] for i in range(len(imp))],
                           text=[f"{x['importance']:.2f}" for x in imp], textposition="outside", marker_line=dict(color=t["primary"], width=1.5)))
    fig.update_xaxes(range=[0, 0.6])
    st.plotly_chart(style(fig, 330, legend=False), use_container_width=True, config={"displayModeBar": False})

c3, c4 = st.columns(2, gap="large")
with c3:
    section("Classification report (test)")
    rows = [{"Class": c, "Precision": T["report"][c]["precision"], "Recall": T["report"][c]["recall"], "F1": T["report"][c]["f1-score"], "Support": int(T["report"][c]["support"])} for c in CLS]
    mac = T["report"]["macro avg"]; rows.append({"Class": "Macro avg", "Precision": mac["precision"], "Recall": mac["recall"], "F1": mac["f1-score"], "Support": T["test_n"]})
    st.dataframe(rows, hide_index=True, use_container_width=True, column_config={k: st.column_config.NumberColumn(format="%.3f") for k in ("Precision", "Recall", "F1")})
with c4:
    section("Choosing the tree depth", "5-fold CV accuracy on the training set only.")
    cv = T["depth_cv"]
    fig = go.Figure(go.Scatter(x=[x["max_depth"] for x in cv], y=[x["CV_accuracy"] for x in cv], mode="lines+markers", line=dict(color=t["primary"], width=3), marker=dict(size=9, color=t["ring"], line=dict(color=t["primary"], width=2))))
    fig.add_vline(x=T["depth"], line=dict(color=t["primary"], dash="dash")); fig.update_xaxes(title_text="max_depth", dtick=1); fig.update_yaxes(range=[0.6, 0.95])
    st.plotly_chart(style(fig, 280, legend=False), use_container_width=True, config={"displayModeBar": False})

section("Demand forecast – actual vs predicted", f"Linear regression Annual_Usage = {F['intercept']:.2f} + {F['coef']:.4f} × Past_Demand, evaluated on {d['metrics']['lr_test_n']:.0f} unseen items.")
test = df[df["LR_Split"] == "test"]
a, b = st.columns([2, 1], gap="large")
with a:
    fig = go.Figure(go.Scatter(x=test["Annual_Usage"], y=test["Predicted_Demand"], mode="markers", marker=dict(color=t["primary"], size=8, opacity=0.7), text=test["Item"], hovertemplate="%{text}<br>actual %{x:,.0f} · predicted %{y:,.0f}<extra></extra>", name="Item"))
    fig.add_shape(type="line", x0=0, y0=0, x1=5600, y1=5600, line=dict(color=t["line"], dash="dash"))
    fig.update_xaxes(title_text="Actual annual demand (units)"); fig.update_yaxes(title_text="Predicted (units)")
    st.plotly_chart(style(fig, 400, legend=False), use_container_width=True, config={"displayModeBar": False})
with b:
    for k, v in [("R² (test)", f"{F['r2_test']:.4f}"), ("R² (train)", f"{F['r2_train']:.4f}"), ("MAE (test)", f"{F['mae_test']:.2f} units"), ("RMSE (test)", f"{F['rmse_test']:.2f} units"), ("Slope", f"{F['coef']:.4f}"), ("Intercept", f"{F['intercept']:.3f}")]:
        st.metric(k, v)
note("R² is high partly because the synthetic usage was generated as a noisy copy of past demand; real data with trend and seasonality would fit less well.")
