# -*- coding: utf-8 -*-
import json, os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "outputs")
PDF = os.path.join(ROOT, "build", "AS25DXB018_Krishna_Mathur_Day4_Summary.pdf")
M = json.load(open(os.path.join(OUT, "metrics.json")))
COLAB_URL = "https://colab.research.google.com/drive/1gNr8Rn11V3S2_hVwtuodVttys6WtbLJ5?usp=sharing"
VERCEL_URL = "https://as25dxb018-inventory-control-room.vercel.app"

fdir = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DJ", os.path.join(fdir, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DJB", os.path.join(fdir, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DJI", os.path.join(fdir, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFontFamily("DJ", normal="DJ", bold="DJB", italic="DJI", boldItalic="DJB")

NAVY = colors.HexColor("#1F3A5F"); TEAL = colors.HexColor("#00798C"); LIGHT = colors.HexColor("#EEF3F8")
PAL = {"A": "#D1495B", "B": "#EDAE49", "C": "#00798C"}

# ---------- compact Pareto chart for the PDF (from the notebook's saved results) ----------
d = pd.read_csv(os.path.join(OUT, "abc_table.csv"))
d["Cum"] = d["Annual_Value"].cumsum() / d["Annual_Value"].sum() * 100
fig, ax = plt.subplots(figsize=(5.4, 2.55), dpi=220)
ax.bar(range(1, len(d) + 1), d["Annual_Value"] / 1000, color=d["ABC_Category"].map(PAL), width=1.0)
ax.set_xlabel("SKUs ranked by annual value (1 = highest)", fontsize=7); ax.set_ylabel("Annual value (000)", fontsize=7)
ax2 = ax.twinx(); ax2.plot(range(1, len(d) + 1), d["Cum"], color="black", lw=1.4)
for y in (70, 90): ax2.axhline(y, color="gray", ls="--", lw=0.7)
ax2.set_ylim(0, 105); ax2.yaxis.set_major_formatter(mtick.PercentFormatter()); ax2.set_ylabel("Cumulative % of value", fontsize=7)
ax2.grid(False); ax.tick_params(labelsize=6.5); ax2.tick_params(labelsize=6.5)
ax.set_title("Pareto chart – ABC classification (500 synthetic SKUs)", fontsize=8, fontweight="bold")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=PAL[c], label=f"Class {c}") for c in "ABC"], fontsize=6.5, loc="center right", frameon=False)
for s in ("top",): ax.spines[s].set_visible(False); ax2.spines[s].set_visible(False)
plt.tight_layout(); pareto_png = os.path.join(ROOT, "build", "_pareto_small.png"); plt.savefig(pareto_png); plt.close()


# ---------- compact BEFORE-AI vs AFTER-AI figure (professor's request) ----------
GREY, GRN = "#8393a1", "#12805C"
fig, ax = plt.subplots(1, 4, figsize=(11.2, 2.15), dpi=220)
def pair(a, names, b_vals, a_vals, title, fmt="%.2f", ylim=None):
    x = np.arange(len(names)); w = 0.38
    r1 = a.bar(x - w/2, b_vals, w, color=GREY, label="Before AI"); r2 = a.bar(x + w/2, a_vals, w, color=GRN, label="After AI")
    a.bar_label(r1, fmt=fmt, fontsize=6, padding=1); a.bar_label(r2, fmt=fmt, fontsize=6, padding=1)
    a.set_xticks(x); a.set_xticklabels(names, fontsize=6.5); a.set_title(title, fontsize=7.5, fontweight="bold"); a.tick_params(labelsize=6)
    if ylim: a.set_ylim(*ylim)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
pair(ax[0], ["Accuracy", "Class-A recall"], [M["ba_cls_acc_before"], M["ba_cls_recallA_before"]], [M["ba_cls_acc_after"], M["ba_cls_recallA_after"]],
     "1 Classification (usage-only rule vs tree)", ylim=(0, 1.12))
pair(ax[1], ["MAE", "RMSE", "|Bias|"], [M["ba_fc_mae_before"], M["ba_fc_rmse_before"], abs(M["ba_fc_bias_before"])], [M["ba_fc_mae_after"], M["ba_fc_rmse_after"], abs(M["ba_fc_bias_after"])],
     "2 Forecast (naive vs regression), units", fmt="%.0f", ylim=(0, 125))
bins = np.linspace(0.80, 1.0, 41)
ax[2].hist(d["CSL_Before"], bins=bins, color=GREY, alpha=0.9, label="Before AI"); ax[2].hist(d["CSL_After"], bins=bins, color=GRN, alpha=0.9, label="After AI")
ax[2].set_title("3 Service level per item (same buffer)", fontsize=7.5, fontweight="bold"); ax[2].xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0)); ax[2].tick_params(labelsize=6)
ax[2].text(0.02, 0.9, f"items < 90%: {M['ba_ss_below90_before']:.0f} → {M['ba_ss_below90_after']:.0f}", transform=ax[2].transAxes, fontsize=6.5)
for sp in ("top", "right"): ax[2].spines[sp].set_visible(False)
pair(ax[3], ["Uniform 95%\n(before)", "97/95/98%\n(after)"], [M["ba_B_b95_short"], M["ba_B_after_short"]], [0, 0], "4 Part B: expected units short / cycle", fmt="%.2f", ylim=(0, 4.6))
ax[3].cla()
bars = ax[3].bar(["Uniform 95%\n(before)", "97/95/98%\n(after)"], [M["ba_B_b95_short"], M["ba_B_after_short"]], color=[GREY, GRN], width=0.55)
ax[3].bar_label(bars, fmt="%.2f", fontsize=6.5, padding=1); ax[3].set_ylim(0, 5.2); ax[3].tick_params(labelsize=6.5)
ax[3].set_title("4 Part B: expected units short / cycle", fontsize=7.5, fontweight="bold")
ax[3].text(0.5, 0.94, f"cost +{(M['ba_B_after_hc']/M['ba_B_b95_hc']-1)*100:.0f}%  ·  shortage −{(1-M['ba_B_after_short']/M['ba_B_b95_short'])*100:.0f}%", transform=ax[3].transAxes, ha="center", fontsize=6.5)
for sp in ("top", "right"): ax[3].spines[sp].set_visible(False)
h, l = ax[0].get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=2, fontsize=6.5, frameon=False, bbox_to_anchor=(0.5, -0.02))
plt.tight_layout(rect=(0, 0.06, 1, 1)); ba_png = os.path.join(ROOT, "build", "_before_after_small.png"); plt.savefig(ba_png); plt.close()

# ---------- styles ----------
def st(name, size=7.4, lead=9.2, font="DJ", color=colors.black, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=lead, textColor=color, **kw)
H = st("h", 7.8, 9.4, "DJB", NAVY, spaceBefore=2.5, spaceAfter=1.5)
B = st("b", 7.2, 9.0)
BUL = st("bul", 7.1, 8.8, leftIndent=8, bulletIndent=0, spaceAfter=0.6)
SM = st("sm", 6.3, 7.8, color=colors.HexColor("#444444"))
CELL = st("cell", 6.7, 8.0)
CELLB = st("cellb", 6.7, 8.0, "DJB")
TILE_T = st("tt", 6.2, 7.6, color=colors.HexColor("#555555"))
TILE_V = st("tv", 9.0, 10.8, "DJB", NAVY)
TILE_S = st("ts", 6.2, 7.6, color=colors.HexColor("#333333"))
def P(t, s=B): return Paragraph(t, s)
def bl(t): return Paragraph(t, BUL, bulletText="•")

doc = SimpleDocTemplate(PDF, pagesize=A4, leftMargin=14*mm, rightMargin=14*mm, topMargin=8*mm, bottomMargin=7*mm,
                        title="Day 4 – Inventory Management and Optimization – One-Page Summary",
                        author="Krishna Mathur (AS25DXB018)")
W = A4[0] - 28*mm
story = []

# ---------- header ----------
hdr = Table([[P("<font color='white' size='11.5'><b>Day 4 – Inventory Management and Optimization</b></font><br/>"
                "<font color='#CFE3F3' size='7.6'>Session IV Lab Activity + Lab Exercise · One-Page Summary</font>", st("x", 9, 12)),
              P("<font color='white' size='7.2'><b>Krishna Mathur</b> · Enrollment ID: <b>AS25DXB018</b><br/>"
                "MAIB, September 2025 · AI in Operations<br/>Prof. Dr. Sandip Kumar Roy · 13 November 2026</font>", st("y", 7.2, 9.4, align=2))]],
            colWidths=[W*0.55, W*0.45])
hdr.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                         ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                         ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
story += [hdr, Spacer(1, 3)]

# ---------- objective + approach ----------
obj = [P("OBJECTIVE", H),
       P("<b>Part A:</b> automate inventory prioritisation and buffer planning for a retail chain (ABC analysis → decision tree → "
         "regression forecast → safety stock). <b>Part B:</b> quantify how the chosen <b>service level</b> changes safety stock and "
         "holding cost for three products, and recommend a level for each.")]
app = [P("APPROACH", H),
       bl("<b>A:</b> 500 <b>synthetic</b> SKUs (seed 42; not real data). ABC rule 70/20/10 on usage × cost; decision tree "
          "(stratified 70/30 split, depth by 5-fold CV); linear regression Past_Demand → Annual_Usage; "
          "Safety stock = 1.65 · σ · √LT, σ = 10 % of predicted demand."),
       bl("<b>B:</b> products A, B, C with assumed demand, σ, lead time, holding cost; service levels 80–99 % with "
          "Z = norm.ppf; SS = Z·σ·√L, HC = SS × cost/unit; Monte-Carlo check (max error "
          f"{M['mc_max_err_pp']:.2f} pp); lead-time and variability sensitivity.")]
two = Table([[obj, app]], colWidths=[W*0.36, W*0.64])
two.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 8),
                         ("RIGHTPADDING", (1, 0), (1, 0), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
story += [two, Spacer(1, 3)]

# ---------- KPI tiles ----------
save_pct = (1 - M["pol_Recommended_hc"] / M["pol_Uniform_99_hc"]) * 100
def tile(t, v, s): return [P(t, TILE_T), P(v, TILE_V), P(s, TILE_S)]
tiles = [tile("ABC SPLIT (% of items)", f"{M['abc_A_items_pct']:.0f}/{M['abc_B_items_pct']:.0f}/{M['abc_C_items_pct']:.0f} %",
              f"carry {M['abc_A_value_pct']:.0f} / {M['abc_B_value_pct']:.0f} / {M['abc_C_value_pct']:.0f} % of value (A / B / C)"),
         tile("DECISION TREE (test)", f"{M['tree_acc_test']*100:.1f} % acc.", f"macro-F1 {M['tree_macro_f1']:.3f}; {M['tree_train_n']:.0f} train / {M['tree_test_n']:.0f} test"),
         tile("LINEAR REGRESSION (test)", f"R² = {M['lr_r2_test']:.3f}", f"MAE {M['lr_mae_test']:.1f} · RMSE {M['lr_rmse_test']:.1f} units"),
         tile("SAFETY STOCK, units (95 %)", f"{M['ss_total']:,.0f}", f"{M['ss_pct_demand']:.1f} % of demand; A holds {M['ss_A_share']:.0f} %"),
         tile("SERVICE 95 % → 99 %", f"+{M['B_inc_pct']:.1f} %", "safety stock and holding cost (every product)"),
         tile("RECOMMENDED POLICY", f"−{save_pct:.0f} % cost", f"vs uniform 99 % ({M['pol_Recommended_hc']:.0f} vs {M['pol_Uniform_99_hc']:.0f} / period)")]
kp = Table([tiles], colWidths=[W/6]*6)
kp.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.5, NAVY),
                        ("LINEAFTER", (0, 0), (-2, -1), 0.4, colors.white), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
story += [P("KEY NUMBERS", H), kp, Spacer(1, 3)]

# ---------- Part A: chart + findings ----------
pw = W * 0.45
img1 = Image(pareto_png, width=pw, height=pw * 2.55 / 5.4)
A_txt = [P("PART A – FINDINGS", H),
         bl(f"<b>ABC:</b> {M['abc_A_items']:.0f} class-A items ({M['abc_A_items_pct']:.1f} %) give {M['abc_A_value_pct']:.0f} % of value; "
            f"{M['abc_C_items']:.0f} class-C items ({M['abc_C_items_pct']:.0f} %) give only {M['abc_C_value_pct']:.0f} %."),
         bl(f"<b>Tree:</b> errors only between neighbouring classes (no A↔C); B is hardest (F1 {M['tree_f1_B']:.2f}). "
            f"Top features: unit cost ({M['imp_Unit_Cost']:.2f}), usage ({M['imp_Annual_Usage']:.2f}); lead time ≈ {M['imp_Lead_Time']:.2f}. "
            f"Train accuracy {M['tree_acc_train']*100:.1f} % → mild overfit."),
         bl(f"<b>Forecast:</b> slope {M['lr_coef']:.3f}; only {M['mae_reduction_pct']:.1f} % lower MAE than the naive "
            "“same as last year” forecast (synthetic data).")]
rowA = Table([[img1, A_txt]], colWidths=[pw + 2, W - pw - 2])
rowA.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 6),
                          ("RIGHTPADDING", (1, 0), (1, 0), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
story += [rowA, Spacer(1, 2)]

# ---------- Part B: figure ----------
fig_path = os.path.join(OUT, "B5_service_level_tradeoffs.png")
from PIL import Image as PILImage
w0, h0 = PILImage.open(fig_path).size
bw = W
story += [P("PART B – SERVICE-LEVEL TRADE-OFFS (blue = safety stock, green = holding cost; same y-scale)", H),
          Image(fig_path, width=bw * 0.62, height=bw * 0.62 * h0 / w0), Spacer(1, 2)]

# ---------- Part B table ----------
hdrs = ["Item", "μ / σ / L / h", "SS @80", "SS @90", "SS @95", "SS @99", "HC @95", "HC @99", "Rec. SL", "Why"]
rows = [[P(f"<b>{h}</b>", CELLB) for h in hdrs]]
prm = {"A": "400 / 30 / 3 / 2.0", "B": "250 / 50 / 4 / 1.5", "C": "150 / 20 / 2 / 2.5"}
why = {"A": "Stable, high volume: protect it; 97→99 % would add 46 HC.",
       "B": "CV 20 %, lead time 4: costliest per point; fix variability, not buffer.",
       "C": "Small buffer: 98 % is cheap; 99 % adds only 19 HC."}
for p in "ABC":
    rows.append([P(f"<b>{p}</b>", CELLB), P(prm[p], CELL)] +
                [P(f"{M[f'B_{p}_ss_{s}']:.1f}", CELL) for s in (80, 90, 95, 99)] +
                [P(f"{M[f'B_{p}_hc_95']:.1f}", CELL), P(f"{M[f'B_{p}_hc_99']:.1f}", CELL),
                 P(f"<b>{M[f'rec_{p}']*100:.0f} %</b>", CELLB), P(why[p], CELL)])
cw = [0.05, 0.13, 0.062, 0.062, 0.062, 0.062, 0.065, 0.065, 0.07, 0.372]
tb = Table(rows, colWidths=[W*c for c in cw], repeatRows=1)
tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#9AA5B1")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))
story += [tb,
          P("μ = avg demand/period, σ = demand std. dev., L = lead time (periods), h = holding cost per unit per period; SS = safety stock (units), HC = holding cost per period, at the given service level (%). "
            " Recommendation rule: raise the service level while the next +1 pp costs ≤ 15 holding-cost units "
            "(assumption; ranking C ≥ A ≥ B holds for tolerances 10–25).", SM), Spacer(1, 2)]

# ---------- Before vs after AI ----------
story += [P("BEFORE AI vs AFTER AI – same items, same data (traditional method vs the models of this lab)", H),
          Image(ba_png, width=W, height=W * 2.15 / 11.2),
          P(f"Classification {M['ba_cls_acc_before']*100:.0f}% → <b>{M['ba_cls_acc_after']*100:.0f}%</b> (class-A items found {M['ba_cls_a_total']-M['ba_cls_a_missed_before']:.0f} → {M['ba_cls_a_total']-M['ba_cls_a_missed_after']:.0f} of {M['ba_cls_a_total']:.0f}); "
            f"forecast only <b>marginally</b> better (MAE {M['ba_fc_mae_before']:.1f} → {M['ba_fc_mae_after']:.1f}, bias {M['ba_fc_bias_before']:.0f} → {M['ba_fc_bias_after']:.0f}); "
            f"same-budget safety stock leaves {M['ba_ss_below90_before']:.0f} items below 90% service before vs {M['ba_ss_below90_after']:.0f} after; "
            f"differentiated service levels are a <b>trade-off</b> (+{(M['ba_B_after_hc']/M['ba_B_b95_hc']-1)*100:.0f}% cost for −{(1-M['ba_B_after_short']/M['ba_B_b95_short'])*100:.0f}% shortage).", SM),
          Spacer(1, 1)]

# ---------- Part B findings + policy table ----------
fnd = [bl(f"<b>Non-linear growth:</b> 80→90 % adds {M['B_A_d_80_90']:.0f} / {M['B_B_d_80_90']:.0f} / {M['B_C_d_80_90']:.0f} units (A / B / C) but 90→99 % "
          f"(fewer points) adds {M['B_A_d_90_99']:.0f} / {M['B_B_d_90_99']:.0f} / {M['B_C_d_90_99']:.0f} – about 2.4× more."),
       bl(f"<b>95 → 99 %:</b> +{M['B_inc_pct']:.1f} % buffer and cost for every product; extra holding cost per period: "
          f"A +{M['B_A_extra_cost']:.0f}, B +{M['B_B_extra_cost']:.0f}, C +{M['B_C_extra_cost']:.0f}."),
       bl(f"<b>Sensitivity (95 %):</b> lead time ×2 → +{M['el_lt2']:.0f} % safety stock; demand σ ×2 → +100 %. B is most exposed "
          f"(σ√L = {M['B_sig_lt_B']:.0f} vs A {M['B_sig_lt_A']:.0f}, C {M['B_sig_lt_C']:.0f}).")]
pol_rows = [[P("<b>Policy</b>", CELLB), P("<b>Σ SS</b>", CELLB), P("<b>Σ HC / period</b>", CELLB)],
            [P("Uniform 95 %", CELL), P(f"{M['pol_Uniform_95_ss']:.0f}", CELL), P(f"{M['pol_Uniform_95_hc']:.0f}", CELL)],
            [P("<b>Recommended 97/95/98</b>", CELLB), P(f"<b>{M['pol_Recommended_ss']:.0f}</b>", CELLB), P(f"<b>{M['pol_Recommended_hc']:.0f}</b>", CELLB)],
            [P("Uniform 99 %", CELL), P(f"{M['pol_Uniform_99_ss']:.0f}", CELL), P(f"{M['pol_Uniform_99_hc']:.0f}", CELL)]]
pt = Table(pol_rows, colWidths=[W*0.17, W*0.07, W*0.1])
pt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#E3F1EA")),
                        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#9AA5B1")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 1.8), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))
rowB = Table([[fnd, pt]], colWidths=[W*0.64, W*0.36])
rowB.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 8),
                          ("RIGHTPADDING", (1, 0), (1, 0), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
story += [Spacer(1, 3), rowB, Spacer(1, 2)]

# ---------- conclusion ----------
story += [P("CONCLUSION", H),
          P(f"A small share of SKUs drives the value, so control and service effort should focus on class A; the tree and regression automate "
            f"classification and forecasting (accuracy {M['tree_acc_test']*100:.0f} %, R² {M['lr_r2_test']:.2f}) and feed Z·σ·√LT buffers. "
            f"Service level is not free: safety stock grows with Z, so 95 → 99 % costs +{M['B_inc_pct']:.0f} % buffer and holding cost, and the last point costs "
            f"≈ {M['marg_ratio']:.1f}× the first. A differentiated policy (<b>A 97 %, B 95 %, C 98 %</b>) is ≈ {save_pct:.0f} % cheaper than uniform 99 %. "
            "Variability (linear) is a stronger lever than lead time (√L).", B),
          Spacer(1, 2),
          P("<b>Caveats:</b> Part A data are synthetic (seed 42), so figures illustrate the method only. Part B parameters and the cost tolerance "
            "are my assumptions; no stock-out cost was available. Demand is assumed normal and independent. Full details: executed notebook.", SM),
          P(f"<b>Links:</b> Colab notebook <a href='{COLAB_URL}' color='#0e7a55'>{COLAB_URL}</a> · Live dashboard <a href='{VERCEL_URL}' color='#0e7a55'>{VERCEL_URL}</a>", SM)]

doc.build(story)
print("built", PDF)
