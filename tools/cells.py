# -*- coding: utf-8 -*-
"""Cell definitions for the Day-4 notebook. Each entry: (kind, key_or_text)
kind: 'md' (markdown text), 'code' (code), 'interp' (business interpretation, filled from interp.py)
"""

CELLS = []
def md(t): CELLS.append(("md", t.strip("\n")))
def code(t): CELLS.append(("code", t.strip("\n")))
def interp(k): CELLS.append(("interp", k))

# ------------------------------------------------------------------ TITLE + CHECKLIST
md("""
# Day 4 – Inventory Management and Optimization
## Session IV: Lab Activity + Lab Exercise

| | |
|---|---|
| **Name** | Krishna Mathur |
| **Enrollment ID** | AS25DXB018 |
| **Program** | MAIB, September 2025 |
| **Course** | AI in Operations |
| **Professor** | Prof. Dr. Sandip Kumar Roy |
| **Task** | Day 4 – Inventory Management and Optimization, Session IV Lab Activity + Lab Exercise |
| **Date** | 13 November 2026 |
""")

md("""
## ✅ Requirements Checklist

**PART A: LAB ACTIVITY – Inventory Prioritization for a Retail Chain**
- [x] **A1.** ABC classification on annual consumption value (annual usage × unit cost): sort descending, cumulative %, assign A/B/C (reference: A ≈ 70–80 % of value from ≈ 20 % of items; B ≈ 15–25 % from ≈ 30 %; C ≈ 5–10 % from ≈ 50 %).
- [x] **A2.** Decision tree classifier predicting ABC category from annual usage, unit cost, lead time, past demand. Report split, accuracy, confusion matrix, classification report, feature importances, tree plot.
- [x] **A3.** Linear regression forecasting future demand from historical usage. Report coefficients, R², MAE, RMSE, actual-vs-predicted plot.
- [x] **A4.** Safety Stock = Z × σ × √Lead Time, 95 % service level (Z = 1.65), σ = 10 % of predicted demand. Show formula, per-item computation, summary table.
- [x] **A5.** Visualise ABC distribution (Pareto with cumulative % line, category counts, value share) and safety stock levels (by item and by class).
- [x] **A6.** Address learning outcomes: how AI enhances traditional inventory models; classification and regression for operational decisions; visualising and interpreting inventory risk buffers.

**PART B: LAB EXERCISE – Advanced Service-Level Trade-Off Simulation (Multi-Product Inventory Strategy)**
- [x] **B1.** Products A, B, C with unique demand, variability, lead time, holding cost per unit (parameter table).
- [x] **B2.** Service levels simulated from 80 % to 99 %.
- [x] **B3.** Z-scores matched to service levels (`scipy.stats.norm.ppf`).
- [x] **B4.** Safety Stock = Z × σ × √Lead Time; Holding Cost = Safety Stock × Holding Cost per Unit.
- [x] **B5.** ONE figure, 3 side-by-side subplots (Product A | B | C) titled *"Service Level Trade-offs in Inventory Optimization"*; x = Service Level (80–99 %); y = Units / Cost; **blue** = Safety Stock; **green** = Holding Cost; legend in each subplot; same y-scale for comparability.
- [x] **B6.** Results: quantify how service-level decisions affect buffers and cost (table at 80/90/95/99 % and % increase from 95 % to 99 %); compare trade-offs across products; show non-linear safety stock growth, rising holding cost, product variation; recommend a service level per product using the visuals.
- [x] **B7.** Sensitivity of safety stock to lead time and demand variability.

**ADDITIONAL (professor's request)**
- [x] **A7.** Plots *before AI* (traditional) vs *after AI* for classification, demand forecast and safety stock.
- [x] **B8.** Plots *before AI* (uniform service level) vs *after AI* (differentiated, data-driven service levels).
""")

# ------------------------------------------------------------------ FRAMING
md("""
## 1. Objective

- **Part A (Lab Activity):** Help a retail chain *automate inventory prioritisation and buffer planning* by combining (i) classical **ABC analysis**, (ii) a **decision tree** that predicts the ABC class from item attributes, (iii) a **linear regression** that forecasts demand, and (iv) a statistical **safety-stock** rule tied to a 95 % service level.
- **Part B (Lab Exercise):** Analyse how the **service level** chosen for a product changes its **safety stock** and **holding cost**, how this differs across three products with different demand, variability, lead time and holding cost, and recommend a service level for each product.
""")

md("""
## 2. Problem Statement

A retail chain stocks thousands of SKUs. Treating every SKU the same wastes working capital on slow, low-value items and under-protects the few items that drive most of the revenue. The inventory manager needs to:

1. **Prioritise** items by their annual consumption value (ABC analysis) and learn a model that can classify *new* items automatically.
2. **Forecast** next-period demand from historical usage.
3. **Size the safety stock** of every item from the forecast and its lead time, for a target service level.
4. **Decide** (Part B) how much service level is worth paying for, because every extra point of service costs additional buffer units and holding cost.
""")

md("""
## 3. Data Description

> ⚠️ **No real retail dataset was provided with the lab.** The professor's sample notebook (`Untitled7.ipynb`) uses a hand-typed table of 7 items. 7 rows are too few to evaluate a classifier or a regression on a hold-out set, so I follow the same approach (item, usage, cost, lead time, past demand) but **generate a larger, clearly labelled SYNTHETIC dataset of 500 SKUs with `np.random.seed(42)`**. It is *not* real data and the numbers should be read as an illustration of the method, not as real retail findings.

| Column | Meaning | Unit |
|---|---|---|
| `Item` | SKU identifier | – |
| `Annual_Usage` | Units consumed in the current year | units / year |
| `Unit_Cost` | Purchase cost per unit | currency / unit |
| `Lead_Time` | Replenishment lead time | periods (as in the professor's sample) |
| `Past_Demand` | Demand observed in the previous year (historical usage) | units / year |

**Part B** uses three products (A, B, C) with a hand-specified parameter table (Section B1).
""")

md("""
## 4. Assumptions

1. **Synthetic data** (seed 42) mimicking a retail catalogue: lognormal usage (capped at 5,000 units) and unit cost (capped at 40) – a few high-value items and a long tail of low-value ones – integer lead times 1–6, past demand = usage × random noise (mean 0.98, sd 0.08).
2. **ABC rule** exactly as in the professor's code: cumulative value ≤ 70 % → **A**, ≤ 90 % → **B**, otherwise **C**.
3. **Safety stock (Part A):** service level 95 %, **Z = 1.65** (as given on the slides; `norm.ppf(0.95)` = 1.645), σ = **10 % of predicted demand**, lead time used in the same time unit as the professor's sample (the formula is applied exactly as specified).
4. **Part B parameters** (demand, σ, lead time, holding cost) are **my own assumptions**, because the slides do not list numbers. They were calibrated so the curves have the same scale and ordering (B > A > C) as the reference chart on slide 33. Units: demand and σ in *units per period (week)*, lead time in *periods*, holding cost in *currency per unit per period*.
5. Demand during the lead time is **normally distributed** with mean μ·L and standard deviation σ·√L; demand is independent across periods.
6. **Recommendation rule (B6):** a planner tolerance of **15 currency units of extra holding cost per +1 percentage-point of service level** (an assumption – no stock-out cost was supplied). A sensitivity of this assumption is shown.
""")

md("""
## 5. Methodology

| Step | Method | Library |
|---|---|---|
| A1 | Annual value = usage × cost → sort → cumulative % → 70/20/10 rule | `pandas` |
| A2 | Decision tree classifier (stratified 70/30 split, depth chosen by cross-validation on the training set) | `sklearn.tree` |
| A3 | Simple linear regression `Past_Demand → Annual_Usage` (70/30 split; R², MAE, RMSE) | `sklearn.linear_model` |
| A4 | Safety stock = Z · σ · √LT with Z = 1.65 | `numpy` |
| A5 | Pareto, count, value-share and safety-stock charts | `matplotlib` |
| B1–B4 | Parameter table → Z via `norm.ppf` (80–99 %) → safety stock and holding cost, plus a Monte-Carlo check | `scipy.stats`, `numpy` |
| B5–B6 | 3-panel trade-off figure, comparison tables, marginal-cost analysis and recommendation | `matplotlib` |
| B7 | Sensitivity to lead time and demand variability (curves + heat-maps) | `matplotlib`, `seaborn` |
""")

# ------------------------------------------------------------------ SETUP
md("""
### Environment set-up
All packages used here are pre-installed in Google Colab; the first cell only makes sure they are present (it is silent when everything is already installed). No file paths are absolute – all data is generated inside the notebook and results are written to the relative folders `data/` and `outputs/`.
""")
code("""
!pip install -q numpy pandas scipy scikit-learn matplotlib seaborn

import sys, sklearn, scipy, numpy, pandas, matplotlib
print("Python      :", sys.version.split()[0])
print("numpy       :", numpy.__version__)
print("pandas      :", pandas.__version__)
print("scipy       :", scipy.__version__)
print("scikit-learn:", sklearn.__version__)
print("matplotlib  :", matplotlib.__version__)
print("Environment ready.")
""")

md("""
### Imports, global settings and colour palette
Same library set as the professor's sample (`pandas`, `numpy`, `matplotlib`, `sklearn`, `scipy.stats.norm`) plus `seaborn` for heat-maps. A fixed seed (42) makes every number reproducible.
""")
code("""
import os, json, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, confusion_matrix, classification_report,
                             r2_score, mean_absolute_error, mean_squared_error)
from scipy.stats import norm

warnings.filterwarnings("ignore")
SEED = 42
np.random.seed(SEED)

os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# consistent palette: ABC classes (Part A) and fixed semantic colours for Part B
PAL = {"A": "#D1495B", "B": "#EDAE49", "C": "#00798C"}
BLUE, GREEN = "tab:blue", "tab:green"
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "font.size": 10})
pd.set_option("display.float_format", "{:,.2f}".format)
pd.set_option("display.width", 160)

metrics = {}          # collected key numbers (exported at the end)
def put(key, value):
    if isinstance(value, (np.integer,)): value = int(value)
    elif isinstance(value, (np.floating,)): value = float(value)
    metrics[key] = value

Z_95 = 1.65           # given on the slides for a 95 % service level
print("Setup complete. Seed =", SEED, "| Z (95 %) used in Part A =", Z_95)
""")

# ================================================================== PART A
md("""
---
# PART A – LAB ACTIVITY: Inventory Prioritization for a Retail Chain
""")

md("""
## A0. Baseline – the professor's 7-item sample
Before scaling up, I reproduce the professor's pipeline on his own 7-item table (slide 29) with the same logic (ABC → decision tree → linear regression → safety stock, in-sample, Z = 1.65). This confirms I understand the reference implementation; the full analysis in A1–A6 then uses a larger dataset so the models can be evaluated on unseen items.
""")
code("""
sample = pd.DataFrame({
    'Item': ['A1', 'A2', 'A3', 'B1', 'B2', 'C1', 'C2'],
    'Annual_Usage': [1000, 800, 600, 400, 300, 100, 50],
    'Unit_Cost': [10, 12, 8, 5, 6, 2, 1],
    'Lead_Time': [2, 2, 2, 3, 3, 4, 4],
    'Past_Demand': [950, 820, 610, 390, 310, 120, 60]})

sample['Annual_Value'] = sample['Annual_Usage'] * sample['Unit_Cost']
sample = sample.sort_values('Annual_Value', ascending=False)
sample['Cumulative%'] = sample['Annual_Value'].cumsum() / sample['Annual_Value'].sum() * 100
sample['ABC_Category'] = np.where(sample['Cumulative%'] <= 70, 'A',
                          np.where(sample['Cumulative%'] <= 90, 'B', 'C'))

feat = ['Annual_Usage', 'Unit_Cost', 'Lead_Time', 'Past_Demand']
tree_s = DecisionTreeClassifier(random_state=SEED).fit(sample[feat], sample['ABC_Category'])
sample['Predicted_ABC'] = tree_s.predict(sample[feat])

reg_s = LinearRegression().fit(sample[['Past_Demand']], sample['Annual_Usage'])
sample['Predicted_Demand'] = reg_s.predict(sample[['Past_Demand']]).round()
sample['Std_Dev'] = sample['Predicted_Demand'] * 0.10
sample['Safety_Stock'] = (Z_95 * sample['Std_Dev'] * np.sqrt(sample['Lead_Time'])).round()

display(sample[['Item', 'Annual_Value', 'Cumulative%', 'ABC_Category', 'Predicted_ABC',
                'Predicted_Demand', 'Lead_Time', 'Safety_Stock']].reset_index(drop=True))
""")
interp("A0")

md("""
## Dataset generation (synthetic, seed = 42)
I generate 500 SKUs: lognormal usage and unit cost (a handful of expensive/fast items and a long tail of cheap/slow ones, typical of retail), integer lead times, and `Past_Demand` as last year's demand = usage × noise. The generator was tuned (not the results) so that the resulting ABC split is close to the classical reference proportions.

*Optional:* set `USE_OWN_CSV = True` to upload your own file with the same five columns instead.
""")
code("""
USE_OWN_CSV = False      # True -> upload a CSV with columns Item, Annual_Usage, Unit_Cost, Lead_Time, Past_Demand

if USE_OWN_CSV:
    from google.colab import files
    uploaded = files.upload()
    df = pd.read_csv(next(iter(uploaded)))
else:
    n_items = 500
    np.random.seed(SEED)
    base_usage = np.random.lognormal(mean=np.log(500), sigma=1.1, size=n_items)
    annual_usage = np.clip(np.round(base_usage), 20, 5000).astype(int)      # cap at a realistic maximum
    unit_cost = np.clip(np.round(np.random.lognormal(mean=np.log(6), sigma=0.9, size=n_items), 2), 0.5, 40.0)
    lead_time = np.random.choice([1, 2, 3, 4, 5, 6], size=n_items, p=[.10, .25, .25, .20, .12, .08])
    past_demand = np.round(annual_usage * np.random.normal(0.98, 0.08, n_items)).astype(int)
    df = pd.DataFrame({'Item': [f"SKU_{i+1:03d}" for i in range(n_items)],
                       'Annual_Usage': annual_usage, 'Unit_Cost': unit_cost,
                       'Lead_Time': lead_time, 'Past_Demand': past_demand})

df.to_csv("data/inventory_synthetic_data.csv", index=False)
put("n_items", len(df))
print("SYNTHETIC dataset (not real data) | rows, columns:", df.shape)
print("Missing values:", int(df.isna().sum().sum()))
display(df.head(8))
display(df.describe().T)
""")
interp("DATA")

md("""
## A1. ABC Classification on Annual Consumption Value
**Steps:** (1) annual value = `Annual_Usage × Unit_Cost`; (2) sort descending; (3) cumulative % of total value; (4) assign **A** (cumulative ≤ 70 %), **B** (≤ 90 %), **C** (rest) – the rule from the professor's code. The summary table compares the result with the textbook reference proportions.
""")
code("""
df['Annual_Value'] = df['Annual_Usage'] * df['Unit_Cost']
df = df.sort_values(by='Annual_Value', ascending=False).reset_index(drop=True)
df['Value_Share%'] = df['Annual_Value'] / df['Annual_Value'].sum() * 100
df['Cumulative%'] = df['Annual_Value'].cumsum() / df['Annual_Value'].sum() * 100
df['Item_Rank%'] = (df.index + 1) / len(df) * 100        # cumulative % of items

def classify(row):
    if row['Cumulative%'] <= 70:
        return 'A'
    elif row['Cumulative%'] <= 90:
        return 'B'
    else:
        return 'C'
df['ABC_Category'] = df.apply(classify, axis=1)

abc = (df.groupby('ABC_Category')
         .agg(Items=('Item', 'count'), Annual_Value=('Annual_Value', 'sum'))
         .assign(**{'Items_%': lambda t: t['Items'] / t['Items'].sum() * 100,
                    'Value_%': lambda t: t['Annual_Value'] / t['Annual_Value'].sum() * 100}))
abc['Reference (items / value)'] = ['~20% / 70-80%', '~30% / 15-25%', '~50% / 5-10%']
for c in 'ABC':
    put(f'abc_{c}_items', abc.loc[c, 'Items']); put(f'abc_{c}_items_pct', abc.loc[c, 'Items_%'])
    put(f'abc_{c}_value', abc.loc[c, 'Annual_Value']); put(f'abc_{c}_value_pct', abc.loc[c, 'Value_%'])
put('total_value', df['Annual_Value'].sum())

print("Top 10 items by annual consumption value:")
display(df[['Item', 'Annual_Usage', 'Unit_Cost', 'Annual_Value', 'Cumulative%', 'ABC_Category']].head(10))
print("ABC summary vs reference proportions:")
display(abc)
""")
interp("A1")

md("""
## A2. Decision Tree – Predicting the ABC Category
**Goal:** learn to predict the ABC class from `Annual_Usage`, `Unit_Cost`, `Lead_Time`, `Past_Demand` so that *new* items can be classified instantly, without recomputing the whole cumulative table.

**Design:** stratified **70 / 30 train–test split** (`random_state = 42`); tree depth chosen by 5-fold cross-validation **on the training set only** (the test set is never used to tune). Reported: accuracy, confusion matrix, classification report, feature importances and the tree plot.
""")
code("""
features = ['Annual_Usage', 'Unit_Cost', 'Lead_Time', 'Past_Demand']
X = df[features]
y = df['ABC_Category']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=SEED, stratify=y)
print(f"Split -> train: {len(X_train)} items (70%) | test: {len(X_test)} items (30%), stratified by ABC class")

# choose tree depth by 5-fold CV on the TRAINING set only
rows = []
for d in range(2, 9):
    cv = cross_val_score(DecisionTreeClassifier(max_depth=d, random_state=SEED), X_train, y_train, cv=5).mean()
    rows.append({'max_depth': d, 'CV_accuracy': cv})
depth_tbl = pd.DataFrame(rows)
best_depth = int(depth_tbl.loc[depth_tbl['CV_accuracy'].round(4).idxmax(), 'max_depth'])
display(depth_tbl)
print("Selected max_depth =", best_depth)

tree = DecisionTreeClassifier(max_depth=best_depth, random_state=SEED)
tree.fit(X_train, y_train)
pred_test = tree.predict(X_test)
acc_test = accuracy_score(y_test, pred_test)
acc_train = accuracy_score(y_train, tree.predict(X_train))
put('tree_depth', best_depth); put('tree_train_n', len(X_train)); put('tree_test_n', len(X_test))
put('tree_acc_test', acc_test); put('tree_acc_train', acc_train)
print(f"\\nTrain accuracy: {acc_train:.3f} | TEST accuracy: {acc_test:.3f}")

labels = ['A', 'B', 'C']
cm = confusion_matrix(y_test, pred_test, labels=labels)
print("\\nConfusion matrix (rows = actual, columns = predicted):")
display(pd.DataFrame(cm, index=[f'Actual {l}' for l in labels], columns=[f'Pred {l}' for l in labels]))
print("Classification report (test set):")
print(classification_report(y_test, pred_test, labels=labels, digits=3))
rep = classification_report(y_test, pred_test, labels=labels, output_dict=True)
for l in labels:
    put(f'tree_f1_{l}', rep[l]['f1-score']); put(f'tree_recall_{l}', rep[l]['recall']); put(f'tree_prec_{l}', rep[l]['precision'])
put('tree_macro_f1', rep['macro avg']['f1-score'])

imp = pd.Series(tree.feature_importances_, index=features).sort_values(ascending=False)
print("Feature importances:")
display(imp.rename('Importance').to_frame())
for f_, v_ in imp.items(): put(f'imp_{f_}', v_)

# in-sample prediction for every item (as in the professor's code)
df['Predicted_ABC'] = tree.predict(df[features])
put('tree_all_agree_pct', (df['Predicted_ABC'] == df['ABC_Category']).mean() * 100)
""")
interp("A2a")

md("""
#### A2 (continued) – Confusion-matrix heat-map and feature importances
""")
code("""
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels,
            cbar=False, ax=axes[0], annot_kws={'size': 14})
axes[0].set_title(f'Confusion Matrix – Test Set (accuracy {acc_test:.1%})')
axes[0].set_xlabel('Predicted ABC category'); axes[0].set_ylabel('Actual ABC category'); axes[0].grid(False)

axes[1].barh(imp.index[::-1], imp.values[::-1], color='#00798C')
for i, v in enumerate(imp.values[::-1]):
    axes[1].text(v + 0.01, i, f'{v:.2f}', va='center')
axes[1].set_title('Decision Tree – Feature Importances')
axes[1].set_xlabel('Importance (share of total impurity reduction)'); axes[1].set_xlim(0, imp.max() * 1.15)
plt.tight_layout()
plt.savefig('outputs/A2_confusion_matrix_feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()
""")
interp("A2b")

md("""
#### A2 (continued) – Tree plot
The fitted tree (top three levels shown for readability), with the split rule, class counts and majority class in every node (colours = predicted class).
""")
code("""
plt.figure(figsize=(28, 11))
plot_tree(tree, feature_names=features, class_names=labels, filled=True, rounded=True,
          fontsize=9, impurity=False, proportion=False, max_depth=3)   # top 3 levels shown for readability
plt.title(f'Decision Tree for ABC Classification (max_depth = {best_depth}, trained on {len(X_train)} items; top 3 levels shown)', fontsize=14)
plt.savefig('outputs/A2_decision_tree.png', dpi=130, bbox_inches='tight')
plt.show()
print("Number of leaves in the full tree:", tree.get_n_leaves(), "| tree depth:", tree.get_depth())
put('tree_leaves', tree.get_n_leaves())
""")
interp("A2c")

md("""
## A3. Linear Regression – Demand Forecast from Historical Usage
**Goal:** forecast demand from historical usage. As in the professor's code the model is `Annual_Usage = β₀ + β₁ · Past_Demand` (last year's demand as the predictor of this year's demand).

**Design:** the model is trained on a **70 / 30 split** and evaluated on unseen items (R², MAE, RMSE, with the training scores for comparison). The final model is then refitted on all items to produce `Predicted_Demand` for every SKU, which feeds the safety-stock step.
""")
code("""
Xr = df[['Past_Demand']]
yr = df['Annual_Usage']
Xr_train, Xr_test, yr_train, yr_test = train_test_split(Xr, yr, test_size=0.30, random_state=SEED)

reg = LinearRegression().fit(Xr_train, yr_train)
yr_pred = reg.predict(Xr_test)

r2_te = r2_score(yr_test, yr_pred); mae_te = mean_absolute_error(yr_test, yr_pred)
rmse_te = np.sqrt(mean_squared_error(yr_test, yr_pred))
r2_tr = r2_score(yr_train, reg.predict(Xr_train))
mae_tr = mean_absolute_error(yr_train, reg.predict(Xr_train))
rmse_tr = np.sqrt(mean_squared_error(yr_train, reg.predict(Xr_train)))

res = pd.DataFrame({'R2': [r2_tr, r2_te], 'MAE (units)': [mae_tr, mae_te], 'RMSE (units)': [rmse_tr, rmse_te]},
                   index=['Train (70%)', 'Test (30%)'])
print(f"Equation: Annual_Usage = {reg.intercept_:.3f} + {reg.coef_[0]:.4f} x Past_Demand")
print(f"Coefficient (slope)   : {reg.coef_[0]:.4f}")
print(f"Intercept             : {reg.intercept_:.3f}")
print(f"R2   train = {r2_tr:.4f} | test = {r2_te:.4f}")
print(f"MAE  train = {mae_tr:.2f} | test = {mae_te:.2f} units")
print(f"RMSE train = {rmse_tr:.2f} | test = {rmse_te:.2f} units")
display(res)
for k, v in {'lr_coef': reg.coef_[0], 'lr_intercept': reg.intercept_, 'lr_r2_test': r2_te, 'lr_mae_test': mae_te,
             'lr_rmse_test': rmse_te, 'lr_r2_train': r2_tr, 'lr_mae_train': mae_tr, 'lr_rmse_train': rmse_tr,
             'lr_test_n': len(yr_test), 'mean_usage': yr.mean()}.items():
    put(k, v)

# final model on all items -> Predicted_Demand for every SKU (as in the professor's code)
reg_all = LinearRegression().fit(Xr, yr)
df['Predicted_Demand'] = reg_all.predict(Xr).round()
put('lr_all_coef', reg_all.coef_[0]); put('lr_all_intercept', reg_all.intercept_)
put('pred_demand_total', df['Predicted_Demand'].sum())

fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
lim = [0, max(yr_test.max(), yr_pred.max()) * 1.05]
axes[0].scatter(yr_test, yr_pred, s=28, alpha=0.75, color='#00798C', label='Test items')
axes[0].plot(lim, lim, 'r--', lw=1.3, label='Perfect forecast (y = x)')
axes[0].set_title('Actual vs Predicted Demand (Test Set)')
axes[0].set_xlabel('Actual annual demand (units)'); axes[0].set_ylabel('Predicted annual demand (units)'); axes[0].legend()

axes[1].scatter(yr_test, yr_test - yr_pred, s=28, alpha=0.75, color='#EDAE49')
axes[1].axhline(0, color='r', ls='--', lw=1.3)
axes[1].set_title('Forecast Residuals (Actual - Predicted)')
axes[1].set_xlabel('Actual annual demand (units)'); axes[1].set_ylabel('Residual (units)')
plt.tight_layout()
plt.savefig('outputs/A3_actual_vs_predicted.png', dpi=150, bbox_inches='tight')
plt.show()
""")
interp("A3")

md("""
## A4. Safety Stock Calculation
**Formula (95 % service level):**

$$\\text{Safety Stock} = Z \\times \\sigma \\times \\sqrt{\\text{Lead Time}},\\qquad Z = 1.65,\\qquad \\sigma = 10\\,\\% \\times \\text{Predicted Demand}$$

- `Z = 1.65` is the standard-normal value for a 95 % cycle service level (given on the slide).
- σ is the standard deviation of demand, assumed to be **10 % of the predicted demand** from A3.
- Lead time enters through its square root because variances add across periods.

The cell first shows one worked example, then computes the buffer for every item and summarises it by ABC class.
""")
code("""
df['Std_Dev'] = df['Predicted_Demand'] * 0.10
df['Safety_Stock'] = (Z_95 * df['Std_Dev'] * np.sqrt(df['Lead_Time'])).round()

# worked example for the top item
r0 = df.iloc[0]
print("Worked example –", r0['Item'], f"(class {r0['ABC_Category']})")
print(f"  Predicted demand = {r0['Predicted_Demand']:,.0f}   ->  sigma = 10% x {r0['Predicted_Demand']:,.0f} = {r0['Std_Dev']:,.1f}")
print(f"  Lead time        = {r0['Lead_Time']}            ->  sqrt(LT) = {np.sqrt(r0['Lead_Time']):.3f}")
print(f"  Safety Stock     = {Z_95} x {r0['Std_Dev']:,.1f} x {np.sqrt(r0['Lead_Time']):.3f} = {r0['Safety_Stock']:,.0f} units\\n")

print("Per-item computation (top 12 items by annual value; all 500 items are saved in outputs/):")
display(df[['Item', 'ABC_Category', 'Predicted_ABC', 'Predicted_Demand', 'Std_Dev', 'Lead_Time', 'Safety_Stock']].head(12))

ss_sum = (df.groupby('ABC_Category')
            .agg(Items=('Item', 'count'), Predicted_Demand=('Predicted_Demand', 'sum'),
                 Total_Safety_Stock=('Safety_Stock', 'sum'), Avg_Safety_Stock=('Safety_Stock', 'mean'),
                 Avg_Lead_Time=('Lead_Time', 'mean')))
ss_sum['SS_as_%_of_Demand'] = ss_sum['Total_Safety_Stock'] / ss_sum['Predicted_Demand'] * 100
ss_sum['Share_of_Total_SS_%'] = ss_sum['Total_Safety_Stock'] / ss_sum['Total_Safety_Stock'].sum() * 100
print("Summary of safety stock by ABC class:")
display(ss_sum)
total_ss = df['Safety_Stock'].sum()
print(f"TOTAL safety stock for all {len(df)} items: {total_ss:,.0f} units "
      f"({total_ss / df['Predicted_Demand'].sum():.1%} of total predicted demand)")

# value of the buffer (units x unit cost)
df['SS_Value'] = df['Safety_Stock'] * df['Unit_Cost']
ssv = df.groupby('ABC_Category')['SS_Value'].sum()
print("Safety-stock value (units x unit cost) by class:", {k: round(v) for k, v in ssv.items()}, "| total:", round(ssv.sum()))
put('ss_total', total_ss); put('ss_total_value', ssv.sum()); put('ss_pct_demand', total_ss / df['Predicted_Demand'].sum() * 100)
for c in 'ABC':
    put(f'ss_{c}_total', ss_sum.loc[c, 'Total_Safety_Stock']); put(f'ss_{c}_avg', ss_sum.loc[c, 'Avg_Safety_Stock'])
    put(f'ss_{c}_share', ss_sum.loc[c, 'Share_of_Total_SS_%']); put(f'ss_{c}_value', ssv[c])
    put(f'ss_{c}_pct_demand', ss_sum.loc[c, 'SS_as_%_of_Demand'])
""")
interp("A4")

md("""
## A5. Visualising the ABC Distribution and Safety Stock Levels
Three figures: **(1)** Pareto chart (value bars + cumulative % line with the 70 % / 90 % cut-offs), **(2)** category counts and value share, **(3)** safety stock by item and by class.
""")
code("""
# ---- Figure 1: Pareto chart --------------------------------------------------
fig, ax1 = plt.subplots(figsize=(13, 5))
colors = df['ABC_Category'].map(PAL)
ax1.bar(range(1, len(df) + 1), df['Annual_Value'], color=colors, width=0.9)
ax1.set_xlabel('Items ranked by annual consumption value (1 = highest)')
ax1.set_ylabel('Annual consumption value (currency units)')
ax1.set_title('Pareto Chart – ABC Classification of 500 SKUs (synthetic data)')
ax2 = ax1.twinx()
ax2.plot(range(1, len(df) + 1), df['Cumulative%'], color='black', lw=2, label='Cumulative % of value')
ax2.axhline(70, color='gray', ls='--', lw=1); ax2.axhline(90, color='gray', ls='--', lw=1)
ax2.text(len(df) * 0.62, 71.5, 'A / B boundary (70 %)', fontsize=9, color='dimgray')
ax2.text(len(df) * 0.62, 91.5, 'B / C boundary (90 %)', fontsize=9, color='dimgray')
ax2.set_ylim(0, 105); ax2.set_ylabel('Cumulative % of total value'); ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
ax2.grid(False)
from matplotlib.patches import Patch
handles = [Patch(color=PAL[c], label=f'Class {c}') for c in 'ABC'] + [plt.Line2D([0], [0], color='black', lw=2, label='Cumulative % of value')]
ax1.legend(handles=handles, loc='center right')
plt.tight_layout(); plt.savefig('outputs/A5_pareto_chart.png', dpi=150, bbox_inches='tight'); plt.show()

# ---- Figure 2: counts + value share -----------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.3))
cnt = df['ABC_Category'].value_counts().reindex(list('ABC'))
bars = axes[0].bar(cnt.index, cnt.values, color=[PAL[c] for c in cnt.index])
axes[0].bar_label(bars, padding=2); axes[0].set_title('ABC Category Distribution (item count)')
axes[0].set_xlabel('Category'); axes[0].set_ylabel('Number of items')

x = np.arange(3); w = 0.38
axes[1].bar(x - w/2, abc['Items_%'], w, label='% of items', color='#9AA5B1')
axes[1].bar(x + w/2, abc['Value_%'], w, label='% of annual value', color='#1F3A5F')
for i, c in enumerate('ABC'):
    axes[1].text(i - w/2, abc.loc[c, 'Items_%'] + 1, f"{abc.loc[c, 'Items_%']:.0f}%", ha='center', fontsize=9)
    axes[1].text(i + w/2, abc.loc[c, 'Value_%'] + 1, f"{abc.loc[c, 'Value_%']:.0f}%", ha='center', fontsize=9)
axes[1].set_xticks(x); axes[1].set_xticklabels(list('ABC')); axes[1].legend()
axes[1].set_title('Share of Items vs Share of Value'); axes[1].set_xlabel('Category'); axes[1].set_ylabel('Percent')
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())

axes[2].pie(abc['Value_%'], labels=[f'{c}  ({v:.1f}%)' for c, v in zip('ABC', abc['Value_%'])],
            colors=[PAL[c] for c in 'ABC'], startangle=90, wedgeprops={'width': 0.45, 'edgecolor': 'white'})
axes[2].set_title('Value Share by Category'); axes[2].grid(False)
plt.tight_layout(); plt.savefig('outputs/A5_category_distribution.png', dpi=150, bbox_inches='tight'); plt.show()

# ---- Figure 3: safety stock by item and by class ----------------------------
fig, axes = plt.subplots(1, 2, figsize=(15, 4.8), gridspec_kw={'width_ratios': [2.2, 1]})
top = df.nlargest(25, 'Safety_Stock')
axes[0].bar(top['Item'].str.replace('SKU_', ''), top['Safety_Stock'], color=top['ABC_Category'].map(PAL))
axes[0].set_title('Safety Stock by Item – 25 Largest Buffers (95 % service level, Z = 1.65)')
axes[0].set_xlabel('SKU number'); axes[0].set_ylabel('Safety stock (units)')
axes[0].tick_params(axis='x', rotation=90)
axes[0].legend(handles=[Patch(color=PAL[c], label=f'Class {c}') for c in 'ABC'])

tot = ss_sum['Total_Safety_Stock']; avg = ss_sum['Avg_Safety_Stock']
b = axes[1].bar(list('ABC'), tot.values, color=[PAL[c] for c in 'ABC'])
axes[1].bar_label(b, labels=[f'{v:,.0f}\\n(avg {a:,.0f}/item)' for v, a in zip(tot, avg)], padding=2, fontsize=9)
axes[1].set_title('Total Safety Stock by ABC Class'); axes[1].set_xlabel('Category'); axes[1].set_ylabel('Safety stock (units)')
axes[1].set_ylim(0, tot.max() * 1.18)
plt.tight_layout(); plt.savefig('outputs/A5_safety_stock_levels.png', dpi=150, bbox_inches='tight'); plt.show()
""")
interp("A5")

md("""
## A6. Learning Outcomes – AI vs Traditional, and What the Models Add
To make the three learning outcomes concrete, the next cell quantifies two things: **(i)** how much better the regression forecast is than the *traditional* static rule "next year = last year" (a naive forecast), and what that does to the buffer; **(ii)** how the trained decision tree classifies three **brand-new items** instantly, and how the forecast → safety-stock chain then treats them.
""")
code("""
# (i) traditional naive forecast (last year's demand) vs regression forecast on the SAME test items
test_idx = yr_test.index
naive_mae = mean_absolute_error(yr_test, df.loc[test_idx, 'Past_Demand'])
naive_rmse = np.sqrt(mean_squared_error(yr_test, df.loc[test_idx, 'Past_Demand']))
cmp = pd.DataFrame({'MAE (units)': [naive_mae, mae_te], 'RMSE (units)': [naive_rmse, rmse_te]},
                   index=['Traditional: forecast = last year', 'AI/ML: linear regression'])
cmp['Error reduction vs traditional'] = [0.0, (1 - cmp.iloc[1, 0] / cmp.iloc[0, 0]) * 100]
display(cmp)
put('naive_mae', naive_mae); put('naive_rmse', naive_rmse)
put('mae_reduction_pct', (1 - mae_te / naive_mae) * 100)

# safety stock if the buffer used the naive forecast instead of the regression forecast
ss_naive = (Z_95 * (df['Past_Demand'] * 0.10) * np.sqrt(df['Lead_Time'])).round().sum()
print(f"Total safety stock with naive forecast : {ss_naive:,.0f} units")
print(f"Total safety stock with regression     : {df['Safety_Stock'].sum():,.0f} units")
put('ss_total_naive', ss_naive)

# (ii) classifying and buffering NEW items without the full cumulative-value table
new_items = pd.DataFrame({'Item': ['NEW_1', 'NEW_2', 'NEW_3'],
                          'Annual_Usage': [4200, 700, 90], 'Unit_Cost': [14.0, 5.0, 3.0],
                          'Lead_Time': [2, 4, 6], 'Past_Demand': [4000, 720, 85]})
new_items['Predicted_ABC'] = tree.predict(new_items[features])
new_items['Predicted_Demand'] = reg_all.predict(new_items[['Past_Demand']]).round()
new_items['Safety_Stock'] = (Z_95 * 0.10 * new_items['Predicted_Demand'] * np.sqrt(new_items['Lead_Time'])).round()
new_items['True_Annual_Value'] = new_items['Annual_Usage'] * new_items['Unit_Cost']
minA = df.loc[df['ABC_Category'] == 'A', 'Annual_Value'].min(); minB = df.loc[df['ABC_Category'] == 'B', 'Annual_Value'].min()
new_items['Class_by_value_rule'] = np.where(new_items['True_Annual_Value'] >= minA, 'A', np.where(new_items['True_Annual_Value'] >= minB, 'B', 'C'))
put('new_items_correct', int((new_items['Predicted_ABC'] == new_items['Class_by_value_rule']).sum()))
print("\\nDecision-tree + regression applied to new items:")
display(new_items)
""")
interp("A6")

# ---------------------------------------------------------------- A7 BEFORE vs AFTER AI
md("""
---
## A7. Before AI vs After AI – Comparison of Plots *(requested by the professor)*
The professor asked for the plots **before AI** (the traditional way of working) next to the plots **after AI** (the models built in A2–A4). Three comparisons follow, each on the **same items** so that the comparison is fair:

| Decision | **Before AI (traditional)** | **After AI** |
|---|---|---|
| **Classification** | Single-criterion rule of thumb: rank items by *annual usage only* and call the top 20 % "A", next 30 % "B", rest "C" (it ignores unit cost) | Decision tree using usage, **cost**, lead time and past demand (A2) |
| **Demand forecast** | Naive rule: next year's demand = last year's demand | Linear regression (A3) |
| **Safety stock** | One flat rule: buffer = a fixed % of last year's demand, the same % for every item, lead time ignored (the % is set so that the **total number of buffer units is identical** to the AI buffer – same budget) | Z · σ · √LT on the predicted demand (A4) |

*Reference for what to expect:* the literature describes ML for ABC mainly as a way to **replicate and extend** multi-criteria classification so new items can be classified without re-running the full analysis (e.g. Lolli et al., decision trees for supervised multi-criteria inventory classification), and vendor/consulting sources claim large forecast-error reductions from AI forecasting (often quoted as 20–50 %). I do **not** assume those figures: everything below is measured on my synthetic data and the gains are reported as they come out.
""")

md("""
#### A7.1 Classification – traditional rule of thumb vs decision tree
Both are scored against the true value-based ABC class on the **same 150 test items**.
""")
code("""
# ---- BEFORE: single-criterion rule of thumb (rank by annual usage only) ----------------
usage_share = df['Annual_Usage'].rank(ascending=False, method='first') / len(df)
df['Traditional_ABC'] = np.where(usage_share <= 0.20, 'A', np.where(usage_share <= 0.50, 'B', 'C'))
trad_test = df.loc[X_test.index, 'Traditional_ABC']

cm_trad = confusion_matrix(y_test, trad_test, labels=labels)
acc_trad = accuracy_score(y_test, trad_test)
rep_trad = classification_report(y_test, trad_test, labels=labels, output_dict=True)
recallA_trad = cm_trad[0, 0] / cm_trad[0].sum(); recallA_ai = cm[0, 0] / cm[0].sum()

cls_cmp = pd.DataFrame({'Before AI (usage-only rule)': [acc_trad, rep_trad['macro avg']['f1-score'], recallA_trad],
                        'After AI (decision tree)':   [acc_test, rep['macro avg']['f1-score'], recallA_ai]},
                       index=['Accuracy', 'Macro-F1', 'Recall of class A'])
cls_cmp['Change (pp)'] = (cls_cmp.iloc[:, 1] - cls_cmp.iloc[:, 0]) * 100
display(cls_cmp.round(3))
for k, v in {'ba_cls_acc_before': acc_trad, 'ba_cls_acc_after': acc_test, 'ba_cls_f1_before': rep_trad['macro avg']['f1-score'],
             'ba_cls_f1_after': rep['macro avg']['f1-score'], 'ba_cls_recallA_before': recallA_trad,
             'ba_cls_recallA_after': recallA_ai}.items():
    put(k, v)
put('ba_cls_a_missed_before', int(cm_trad[0].sum() - cm_trad[0, 0])); put('ba_cls_a_missed_after', int(cm[0].sum() - cm[0, 0]))
put('ba_cls_a_total', int(cm[0].sum()))

GREY, GRN = '#7A8A99', '#12805C'
fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
sns.heatmap(cm_trad, annot=True, fmt='d', cmap='Greys', xticklabels=labels, yticklabels=labels, cbar=False, ax=axes[0], annot_kws={'size': 14})
axes[0].set_title(f'BEFORE AI – usage-only rule\\naccuracy {acc_trad:.1%}'); axes[0].set_xlabel('Predicted class'); axes[0].set_ylabel('Actual class (value-based ABC)'); axes[0].grid(False)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=labels, yticklabels=labels, cbar=False, ax=axes[1], annot_kws={'size': 14})
axes[1].set_title(f'AFTER AI – decision tree\\naccuracy {acc_test:.1%}'); axes[1].set_xlabel('Predicted class'); axes[1].set_ylabel('Actual class (value-based ABC)'); axes[1].grid(False)
x = np.arange(3); w = 0.38
b1 = axes[2].bar(x - w/2, cls_cmp.iloc[:, 0], w, color=GREY, label='Before AI (usage-only rule)')
b2 = axes[2].bar(x + w/2, cls_cmp.iloc[:, 1], w, color=GRN, label='After AI (decision tree)')
axes[2].bar_label(b1, fmt='%.2f', padding=2, fontsize=9); axes[2].bar_label(b2, fmt='%.2f', padding=2, fontsize=9)
axes[2].set_xticks(x); axes[2].set_xticklabels(cls_cmp.index); axes[2].set_ylim(0, 1.12); axes[2].legend(loc='lower right')
axes[2].set_title('Classification quality (150 test items)'); axes[2].set_ylabel('Score')
plt.tight_layout(); plt.savefig('outputs/A7_before_after_classification.png', dpi=150, bbox_inches='tight'); plt.show()
""")
interp("A7a")

md("""
#### A7.2 Demand forecast – naive "same as last year" vs linear regression
""")
code("""
actual_t = yr_test
naive_t = df.loc[yr_test.index, 'Past_Demand']
ai_t = pd.Series(yr_pred, index=yr_test.index)

def fc_metrics(a, p):
    e = a - p
    return {'MAE (units)': mean_absolute_error(a, p), 'RMSE (units)': np.sqrt(mean_squared_error(a, p)),
            'Bias (mean actual - forecast)': e.mean(), 'MAPE (%)': (e.abs() / a).mean() * 100, 'R2': r2_score(a, p)}
fc_cmp = pd.DataFrame({'Before AI (naive: last year)': fc_metrics(actual_t, naive_t),
                       'After AI (linear regression)': fc_metrics(actual_t, ai_t)})
fc_cmp['Change'] = fc_cmp.iloc[:, 1] - fc_cmp.iloc[:, 0]
display(fc_cmp.round(3))
for i, nm in enumerate(['mae', 'rmse', 'bias', 'mape', 'r2']):
    put(f'ba_fc_{nm}_before', fc_cmp.iloc[i, 0]); put(f'ba_fc_{nm}_after', fc_cmp.iloc[i, 1])

fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
lim = [0, max(actual_t.max(), naive_t.max(), ai_t.max()) * 1.05]
for ax, pred, ttl, col in [(axes[0], naive_t, 'BEFORE AI – naive forecast (last year)', GREY), (axes[1], ai_t, 'AFTER AI – linear regression', GRN)]:
    ax.scatter(actual_t, pred, s=24, alpha=0.75, color=col); ax.plot(lim, lim, 'k--', lw=1.1)
    ax.set_title(ttl); ax.set_xlabel('Actual annual demand (units)'); ax.set_ylabel('Forecast (units)')
    ax.text(0.04, 0.92, f"MAE {mean_absolute_error(actual_t, pred):.1f} | RMSE {np.sqrt(mean_squared_error(actual_t, pred)):.1f}", transform=ax.transAxes, fontsize=9)
x = np.arange(3); w = 0.38
vals_b = [fc_cmp.iloc[0, 0], fc_cmp.iloc[1, 0], abs(fc_cmp.iloc[2, 0])]; vals_a = [fc_cmp.iloc[0, 1], fc_cmp.iloc[1, 1], abs(fc_cmp.iloc[2, 1])]
b1 = axes[2].bar(x - w/2, vals_b, w, color=GREY, label='Before AI (naive)'); b2 = axes[2].bar(x + w/2, vals_a, w, color=GRN, label='After AI (regression)')
axes[2].bar_label(b1, fmt='%.1f', padding=2, fontsize=9); axes[2].bar_label(b2, fmt='%.1f', padding=2, fontsize=9)
axes[2].set_xticks(x); axes[2].set_xticklabels(['MAE', 'RMSE', '|Bias|']); axes[2].set_ylabel('Units'); axes[2].legend()
axes[2].set_title('Forecast error (lower is better)')
plt.tight_layout(); plt.savefig('outputs/A7_before_after_forecast.png', dpi=150, bbox_inches='tight'); plt.show()
""")
interp("A7b")

md("""
#### A7.3 Safety stock – one flat rule vs Z · σ · √LT on the predicted demand
Same budget: the flat rule's % is set so that it holds exactly as many buffer units in total as the AI approach. To judge the *protection* each buffer gives, I use the same risk model as in A4 (σ = 10 % of predicted demand, lead time √LT) and compute the **achieved service level** of every item as Φ(buffer ÷ (σ·√LT)). *(This evaluates both rules with my assumed σ model, so it measures consistency of protection, not real-world stock-outs.)*
""")
code("""
flat_pct = df['Safety_Stock'].sum() / df['Past_Demand'].sum()            # same total units as the AI buffer
df['SS_Before'] = flat_pct * df['Past_Demand']
df['SS_After'] = df['Safety_Stock']
sigma_lt = df['Std_Dev'] * np.sqrt(df['Lead_Time'])                       # risk model of A4
df['CSL_Before'] = norm.cdf(df['SS_Before'] / sigma_lt)
df['CSL_After'] = norm.cdf(df['SS_After'] / sigma_lt)

sc = pd.DataFrame({
    'Total buffer (units)': [df['SS_Before'].sum(), df['SS_After'].sum()],
    'Buffer value (units x cost)': [(df['SS_Before'] * df['Unit_Cost']).sum(), (df['SS_After'] * df['Unit_Cost']).sum()],
    'Mean achieved service level': [df['CSL_Before'].mean(), df['CSL_After'].mean()],
    'Lowest item service level': [df['CSL_Before'].min(), df['CSL_After'].min()],
    'Items below 90 % service': [(df['CSL_Before'] < 0.90).sum(), (df['CSL_After'] < 0.90).sum()],
    'Items below 80 % service': [(df['CSL_Before'] < 0.80).sum(), (df['CSL_After'] < 0.80).sum()],
    'Std. dev. of item service level (pp)': [df['CSL_Before'].std() * 100, df['CSL_After'].std() * 100],
}, index=['Before AI (flat % of last year)', 'After AI (Z x sigma x sqrt(LT))']).T
print(f"Flat rule: buffer = {flat_pct:.1%} of last year's demand for every item (lead time ignored)")
display(sc)
for i, nm in enumerate(['units', 'value', 'csl_mean', 'csl_min', 'below90', 'below80', 'csl_sd']):
    put(f'ba_ss_{nm}_before', sc.iloc[i, 0]); put(f'ba_ss_{nm}_after', sc.iloc[i, 1])
put('ba_ss_flat_pct', flat_pct * 100)

fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
axes[0].scatter(df['Lead_Time'] + np.random.default_rng(1).uniform(-0.18, 0.18, len(df)), df['SS_Before'], s=14, alpha=0.5, color=GREY)
axes[0].set_title('BEFORE AI – flat % of last year'); axes[0].set_xlabel('Lead time (periods, jittered)'); axes[0].set_ylabel('Safety stock (units)')
axes[1].scatter(df['Lead_Time'] + np.random.default_rng(1).uniform(-0.18, 0.18, len(df)), df['SS_After'], s=14, alpha=0.5, color=GRN)
axes[1].set_title('AFTER AI – Z x sigma x sqrt(LT)'); axes[1].set_xlabel('Lead time (periods, jittered)'); axes[1].set_ylabel('Safety stock (units)')
ymax_ss = max(df['SS_Before'].max(), df['SS_After'].max()) * 1.05
axes[0].set_ylim(0, ymax_ss); axes[1].set_ylim(0, ymax_ss)
bins = np.linspace(0.80, 1.0, 41)
axes[2].hist(df['CSL_Before'], bins=bins, color=GREY, alpha=0.8, label='Before AI (flat rule)')
axes[2].hist(df['CSL_After'], bins=bins, color=GRN, alpha=0.85, label='After AI')
axes[2].axvline(0.95, color='k', ls='--', lw=1); axes[2].xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
axes[2].set_title('Service level achieved per item (same total buffer)'); axes[2].set_xlabel('Achieved service level'); axes[2].set_ylabel('Number of items'); axes[2].legend(loc='upper left')
plt.tight_layout(); plt.savefig('outputs/A7_before_after_safety_stock.png', dpi=150, bbox_inches='tight'); plt.show()
""")
interp("A7c")

md("""
#### A7.4 Part A scorecard – before vs after AI
""")
code("""
score = pd.DataFrame({
    'Metric': ['Classification accuracy (test)', 'Class-A items correctly flagged', 'Forecast MAE (units)', 'Forecast RMSE (units)',
               'Forecast bias (units)', 'Items below 90 % service', 'Lowest item service level'],
    'Before AI': [f"{acc_trad:.1%}", f"{cm_trad[0,0]} of {cm_trad[0].sum()}", f"{fc_cmp.iloc[0,0]:.1f}", f"{fc_cmp.iloc[1,0]:.1f}",
                  f"{fc_cmp.iloc[2,0]:+.1f}", f"{int(sc.iloc[4,0])}", f"{sc.iloc[3,0]:.1%}"],
    'After AI':  [f"{acc_test:.1%}", f"{cm[0,0]} of {cm[0].sum()}", f"{fc_cmp.iloc[0,1]:.1f}", f"{fc_cmp.iloc[1,1]:.1f}",
                  f"{fc_cmp.iloc[2,1]:+.1f}", f"{int(sc.iloc[4,1])}", f"{sc.iloc[3,1]:.1%}"]}).set_index('Metric')
display(score)
""")
interp("A7")


# ================================================================== PART B
md("""
---
# PART B – LAB EXERCISE: Advanced Service-Level Trade-Off Simulation (Multi-Product Inventory Strategy)

**Scenario (slide 32):** a supply-chain manager oversees three products with different demand patterns and cost structures and must choose a service level for each by balancing **customer satisfaction** (service level), **inventory risk** (safety stock) and **financial impact** (holding cost).
""")

md("""
## B1. Product Parameters
Products A, B and C each get their own demand, variability, lead time and holding cost per unit. These values are **my assumptions** (see Section 4) calibrated to reproduce the scale of the reference chart. Product **A** is a high-volume, stable item; **B** is a medium-volume item with *highly variable* demand and a long lead time; **C** is a low-volume item with a short lead time but the *highest* holding cost per unit.
""")
code("""
products = pd.DataFrame({
    'Product':      ['A', 'B', 'C'],
    'Avg_Demand':   [400, 250, 150],     # units per period (week)
    'Demand_Std':   [30, 50, 20],        # sigma, units per period
    'Lead_Time':    [3, 4, 2],           # periods
    'Holding_Cost': [2.00, 1.50, 2.50],  # currency per unit per period
}).set_index('Product')
products['CV_%'] = products['Demand_Std'] / products['Avg_Demand'] * 100          # demand variability
products['Sigma_x_sqrtLT'] = products['Demand_Std'] * np.sqrt(products['Lead_Time'])   # std of lead-time demand

print("B1 – Parameter table (assumed values; units per period = week):")
display(products)
for p in products.index:
    put(f'B_cv_{p}', products.loc[p, 'CV_%']); put(f'B_sig_lt_{p}', products.loc[p, 'Sigma_x_sqrtLT'])
""")
interp("B1")

md("""
## B2 & B3. Service Levels (80 % → 99 %) and Matching Z-Scores
Service levels are simulated on a grid from 80 % to 99 % in 1-percentage-point steps (20 points). Each service level is converted into a Z-score with the inverse standard-normal CDF, `scipy.stats.norm.ppf` – no hard-coded values in Part B.
""")
code("""
service_levels = np.round(np.linspace(0.80, 0.99, 20), 2)       # 80%, 81%, ... 99%
z_scores = norm.ppf(service_levels)                                # B3: Z matched to each service level
z_tbl = pd.DataFrame({'Service Level': [f'{s:.0%}' for s in service_levels], 'Z-score': z_scores})
print(f"{len(service_levels)} service levels from {service_levels[0]:.0%} to {service_levels[-1]:.0%}")
display(z_tbl.T)
for s in (0.80, 0.90, 0.95, 0.99):
    put(f'Z_{int(s*100)}', norm.ppf(s))
""")
interp("B3")

md("""
## B4. Safety Stock and Holding Cost
For every product *p* and service level *s*:

$$\\text{Safety Stock}_{p,s} = Z_s \\times \\sigma_p \\times \\sqrt{\\text{Lead Time}_p}\\qquad\\qquad \\text{Holding Cost}_{p,s} = \\text{Safety Stock}_{p,s} \\times h_p$$
""")
code("""
records = []
for p, r in products.iterrows():
    ss = z_scores * r['Demand_Std'] * np.sqrt(r['Lead_Time'])      # safety stock (units)
    hc = ss * r['Holding_Cost']                                      # holding cost per period
    for s, z, a, b in zip(service_levels, z_scores, ss, hc):
        records.append({'Product': p, 'Service_Level': s, 'Z': z, 'Safety_Stock': a, 'Holding_Cost': b})
sim = pd.DataFrame(records)

print("Safety stock (units) – every service level:")
display(sim.pivot(index='Service_Level', columns='Product', values='Safety_Stock').round(1).T)
print("Holding cost (currency per period) – every service level:")
display(sim.pivot(index='Service_Level', columns='Product', values='Holding_Cost').round(1).T)
""")

md("""
#### B4 (continued) – Monte-Carlo check of the simulated service levels
The formulas assume normally distributed lead-time demand. To verify that the safety stock really delivers the intended service level, I simulate **200,000 lead-time demands** per product, N(μ·L, σ·√L), set the reorder point to *mean + safety stock*, and measure the share of cycles without a stock-out (achieved cycle service level).
""")
code("""
rng = np.random.default_rng(SEED)
n_sim = 200_000
mc_rows = []
for p, r in products.iterrows():
    mu_lt = r['Avg_Demand'] * r['Lead_Time']
    sd_lt = r['Demand_Std'] * np.sqrt(r['Lead_Time'])
    ltd = rng.normal(mu_lt, sd_lt, n_sim)                           # simulated lead-time demand
    for s in service_levels:
        ss = norm.ppf(s) * sd_lt
        mc_rows.append({'Product': p, 'Target': s, 'Achieved': (ltd <= mu_lt + ss).mean()})
mc = pd.DataFrame(mc_rows)
mc['Abs_Error_pp'] = (mc['Achieved'] - mc['Target']).abs() * 100
print("Achieved vs target service level (selected levels):")
display(mc[mc['Target'].isin([0.80, 0.90, 0.95, 0.99])].assign(
    Target=lambda t: (t['Target'] * 100).round(0).astype(int).astype(str) + '%',
    Achieved=lambda t: t['Achieved'].map('{:.2%}'.format)).pivot(index='Product', columns='Target', values='Achieved'))
print(f"Maximum absolute deviation over all products and levels: {mc['Abs_Error_pp'].max():.2f} percentage points")
put('mc_max_err_pp', mc['Abs_Error_pp'].max())
""")
interp("B4")

md("""
## B5. Service-Level Trade-off Figure (one figure, three side-by-side subplots)
Products A | B | C, x-axis = service level 80–99 %, y-axis = Units / Cost, **blue = Safety Stock (units)**, **green = Holding Cost (currency per period)**, a legend in every subplot and a **shared y-axis** so the products can be compared directly – as in the reference chart on slide 33.
""")
code("""
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
for ax, p in zip(axes, products.index):
    d = sim[sim['Product'] == p]
    ax.plot(d['Service_Level'], d['Safety_Stock'], color=BLUE, lw=2, label='Safety Stock')
    ax.plot(d['Service_Level'], d['Holding_Cost'], color=GREEN, lw=2, label='Holding Cost')
    ax.set_title(f'Product {p}')
    ax.set_xlabel('Service Level')
    ax.set_xlim(0.795, 0.995)
    ax.set_xticks([0.80, 0.85, 0.90, 0.95, 0.99])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
    ax.grid(True, alpha=0.4)
    ax.legend(loc='upper left')
axes[0].set_ylabel('Units / Cost')
ymax = sim[['Safety_Stock', 'Holding_Cost']].to_numpy().max()
axes[0].set_ylim(0, ymax * 1.08)                      # sharey=True -> identical y-scale in all subplots
fig.suptitle('Service Level Trade-offs in Inventory Optimization', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout(w_pad=2.5)
plt.savefig('outputs/B5_service_level_tradeoffs.png', dpi=150, bbox_inches='tight')
plt.show()
""")
interp("B5")

md("""
## B6. Results – Quantifying the Trade-offs and Recommending a Service Level
**(a)** Table at 80 / 90 / 95 / 99 % service level and the % increase from 95 % to 99 %.
""")
code("""
pick = [0.80, 0.90, 0.95, 0.99]
tbl = (sim[sim['Service_Level'].isin(pick)]
         .assign(SL=lambda t: (t['Service_Level'] * 100).round(0).astype(int).astype(str) + '%')
         .pivot(index='Product', columns='SL', values=['Safety_Stock', 'Holding_Cost']).round(1))
print("Safety stock (units) and holding cost (currency / period) at selected service levels:")
display(tbl)

at = sim.set_index(['Product', 'Service_Level'])
inc = pd.DataFrame({
    'SS @95%': [at.loc[(p, 0.95), 'Safety_Stock'] for p in 'ABC'],
    'SS @99%': [at.loc[(p, 0.99), 'Safety_Stock'] for p in 'ABC'],
    'HC @95%': [at.loc[(p, 0.95), 'Holding_Cost'] for p in 'ABC'],
    'HC @99%': [at.loc[(p, 0.99), 'Holding_Cost'] for p in 'ABC']}, index=list('ABC'))
inc['Extra units'] = inc['SS @99%'] - inc['SS @95%']
inc['Extra cost / period'] = inc['HC @99%'] - inc['HC @95%']
inc['SS increase %'] = (inc['SS @99%'] / inc['SS @95%'] - 1) * 100
inc['HC increase %'] = (inc['HC @99%'] / inc['HC @95%'] - 1) * 100
print("Increase when moving from 95% to 99% service level:")
display(inc.round(1))
for p in 'ABC':
    for s in pick:
        put(f'B_{p}_ss_{int(s*100)}', at.loc[(p, s), 'Safety_Stock']); put(f'B_{p}_hc_{int(s*100)}', at.loc[(p, s), 'Holding_Cost'])
    put(f'B_{p}_extra_units', inc.loc[p, 'Extra units']); put(f'B_{p}_extra_cost', inc.loc[p, 'Extra cost / period'])
put('B_inc_pct', inc['SS increase %'].iloc[0])
""")
interp("B6a")

md("""
**(b) Non-linearity and marginal cost.** If safety stock grew linearly, every extra percentage point would cost the same. The next cell measures the **marginal** safety stock and holding cost of each extra +1 pp, and compares the 80 → 90 % step with the 90 → 99 % step.
""")
code("""
marg = sim.copy()
marg['Marg_SS'] = marg.groupby('Product')['Safety_Stock'].diff()
marg['Marg_HC'] = marg.groupby('Product')['Holding_Cost'].diff()

step = pd.DataFrame({
    p: {'Delta SS 80->90 (10 pp)': at.loc[(p, 0.90), 'Safety_Stock'] - at.loc[(p, 0.80), 'Safety_Stock'],
        'Delta SS 90->99 (9 pp)':  at.loc[(p, 0.99), 'Safety_Stock'] - at.loc[(p, 0.90), 'Safety_Stock'],
        'Marginal SS per +1pp @80-81%': marg[(marg.Product == p) & (np.isclose(marg.Service_Level, 0.81))]['Marg_SS'].iloc[0],
        'Marginal SS per +1pp @98-99%': marg[(marg.Product == p) & (np.isclose(marg.Service_Level, 0.99))]['Marg_SS'].iloc[0],
        'Marginal HC per +1pp @98-99%': marg[(marg.Product == p) & (np.isclose(marg.Service_Level, 0.99))]['Marg_HC'].iloc[0]}
    for p in 'ABC'}).round(1)
display(step)
ratio = (marg[np.isclose(marg.Service_Level, 0.99)]['Marg_SS'].values / marg[np.isclose(marg.Service_Level, 0.81)]['Marg_SS'].values)
put('marg_ratio', ratio[0])
for p in 'ABC':
    put(f'B_{p}_marg_hc_99', step.loc['Marginal HC per +1pp @98-99%', p]); put(f'B_{p}_d_80_90', step.loc['Delta SS 80->90 (10 pp)', p])
    put(f'B_{p}_d_90_99', step.loc['Delta SS 90->99 (9 pp)', p])

fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))
for p, c in zip('ABC', [PAL['A'], PAL['B'], PAL['C']]):
    d = marg[marg.Product == p].dropna()
    axes[0].plot(d['Service_Level'], d['Marg_SS'], marker='o', ms=3, lw=1.8, color=c, label=f'Product {p}')
    axes[1].plot(d['Service_Level'], d['Marg_HC'], marker='o', ms=3, lw=1.8, color=c, label=f'Product {p}')
axes[0].set_title('Marginal Safety Stock per +1 pp of Service Level'); axes[0].set_ylabel('Extra units per +1 pp')
axes[1].set_title('Marginal Holding Cost per +1 pp of Service Level'); axes[1].set_ylabel('Extra cost per period per +1 pp')
for a in axes:
    a.set_xlabel('Service level reached'); a.set_xticks([0.81, 0.85, 0.90, 0.95, 0.99])
    a.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0)); a.legend()
plt.tight_layout(); plt.savefig('outputs/B6_marginal_cost.png', dpi=150, bbox_inches='tight'); plt.show()
""")
interp("B6b")

md("""
**(c) Recommended service level per product.** Because no stock-out (shortage) cost was provided, I use a transparent planner rule: *raise the service level step by step while the extra holding cost of the next +1 pp stays at or below a tolerance of **15 currency units per period**.* The tolerance is an assumption, so its effect is tested at 10 / 15 / 25. The recommended points are then marked on the same trade-off curves (visual check) and compared with uniform 95 % and uniform 99 % policies for the whole portfolio.
""")
code("""
def recommend(tol):
    out = {}
    for p in 'ABC':
        d = marg[marg.Product == p].dropna()
        ok = d[d['Marg_HC'] <= tol]
        out[p] = float(ok['Service_Level'].max()) if len(ok) else 0.80      # highest level whose last step is affordable
    return out

TOL = 15
rec = recommend(TOL)
rec_tbl = pd.DataFrame({
    'Recommended SL': [f'{rec[p]:.0%}' for p in 'ABC'],
    'Safety stock (units)': [at.loc[(p, rec[p]), 'Safety_Stock'] for p in 'ABC'],
    'Holding cost / period': [at.loc[(p, rec[p]), 'Holding_Cost'] for p in 'ABC'],
    'Extra cost to reach 99%': [at.loc[(p, 0.99), 'Holding_Cost'] - at.loc[(p, rec[p]), 'Holding_Cost'] for p in 'ABC'],
    'Marginal HC of last step': [marg[(marg.Product == p) & np.isclose(marg.Service_Level, rec[p])]['Marg_HC'].iloc[0] for p in 'ABC'],
}, index=list('ABC')).round(1)
print(f"Recommendation with tolerance = {TOL} currency units per +1 pp:")
display(rec_tbl)
sens = pd.DataFrame({f'tol={t}': {p: f'{recommend(t)[p]:.0%}' for p in 'ABC'} for t in (10, 15, 25)})
print("Sensitivity of the recommendation to the tolerance:")
display(sens)

# portfolio comparison
def port(levels):
    return (sum(at.loc[(p, levels[p]), 'Safety_Stock'] for p in 'ABC'), sum(at.loc[(p, levels[p]), 'Holding_Cost'] for p in 'ABC'))
policies = {'Uniform 95%': {p: 0.95 for p in 'ABC'}, 'Recommended': rec, 'Uniform 99%': {p: 0.99 for p in 'ABC'}}
pol = pd.DataFrame({k: port(v) for k, v in policies.items()}, index=['Total safety stock (units)', 'Total holding cost / period']).T
display(pol.round(1))
for p in 'ABC':
    put(f'rec_{p}', rec[p]); put(f'rec_{p}_ss', at.loc[(p, rec[p]), 'Safety_Stock']); put(f'rec_{p}_hc', at.loc[(p, rec[p]), 'Holding_Cost'])
for k, v in policies.items():
    kk = k.replace(' ', '_').replace('%', '')
    put(f'pol_{kk}_ss', port(v)[0]); put(f'pol_{kk}_hc', port(v)[1])

# visual check: recommended points on the trade-off curves
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
for ax, p in zip(axes, 'ABC'):
    d = sim[sim.Product == p]
    ax.plot(d['Service_Level'], d['Safety_Stock'], color=BLUE, lw=2, label='Safety Stock')
    ax.plot(d['Service_Level'], d['Holding_Cost'], color=GREEN, lw=2, label='Holding Cost')
    ax.axvline(rec[p], color='crimson', ls='--', lw=1.4, label=f'Recommended {rec[p]:.0%}')
    ax.scatter([rec[p]] * 2, [at.loc[(p, rec[p]), 'Safety_Stock'], at.loc[(p, rec[p]), 'Holding_Cost']], color='crimson', zorder=5)
    ax.set_title(f'Product {p}'); ax.set_xlabel('Service Level'); ax.set_xlim(0.795, 0.995)
    ax.set_xticks([0.80, 0.85, 0.90, 0.95, 0.99])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0)); ax.legend(loc='upper left')
axes[0].set_ylabel('Units / Cost'); axes[0].set_ylim(0, ymax * 1.08)
fig.suptitle('Recommended Service Level per Product (marked on the trade-off curves)', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout(); plt.savefig('outputs/B6_recommended_service_levels.png', dpi=150, bbox_inches='tight'); plt.show()
""")
interp("B6c")

md("""
## B7. Sensitivity of Safety Stock to Lead Time and Demand Variability
At a fixed **95 % service level** (Z from `norm.ppf(0.95)`), I vary one driver at a time and then both together:
1. **Lead time** from 1 to 12 periods (σ held at its base value).
2. **Demand variability** – σ scaled from 0.5× to 2× its base value (lead time held at base).
3. **Heat-maps** of safety stock over a lead-time × coefficient-of-variation grid for each product.
""")
code("""
z95 = norm.ppf(0.95)
lt_grid = np.arange(1, 13)
mult_grid = np.round(np.linspace(0.5, 2.0, 16), 2)

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
for p, c in zip('ABC', [PAL['A'], PAL['B'], PAL['C']]):
    r = products.loc[p]
    axes[0].plot(lt_grid, z95 * r['Demand_Std'] * np.sqrt(lt_grid), marker='o', ms=4, lw=2, color=c, label=f'Product {p} (σ = {r["Demand_Std"]:.0f})')
    axes[0].scatter([r['Lead_Time']], [z95 * r['Demand_Std'] * np.sqrt(r['Lead_Time'])], s=110, facecolors='none', edgecolors='black', zorder=5)
    axes[1].plot(mult_grid, z95 * r['Demand_Std'] * mult_grid * np.sqrt(r['Lead_Time']), marker='o', ms=4, lw=2, color=c,
                 label=f'Product {p} (L = {r["Lead_Time"]:.0f})')
    axes[1].scatter([1.0], [z95 * r['Demand_Std'] * np.sqrt(r['Lead_Time'])], s=110, facecolors='none', edgecolors='black', zorder=5)
axes[0].set_title('Safety Stock vs Lead Time (95 % service level)'); axes[0].set_xlabel('Lead time (periods)'); axes[0].set_ylabel('Safety stock (units)')
axes[1].set_title('Safety Stock vs Demand Variability (95 % service level)'); axes[1].set_xlabel('σ multiplier (1.0 = base demand variability)'); axes[1].set_ylabel('Safety stock (units)')
for a in axes: a.legend()
fig.text(0.5, -0.02, 'Circled points = base case of each product', ha='center', fontsize=9)
plt.tight_layout(); plt.savefig('outputs/B7_sensitivity_curves.png', dpi=150, bbox_inches='tight'); plt.show()

# elasticity table (relative change in safety stock)
el = pd.DataFrame({
    'Change in driver': ['Lead time +25%', 'Lead time x2', 'Lead time x4', 'Std dev +25%', 'Std dev x2'],
    'Safety stock change %': [(np.sqrt(1.25) - 1) * 100, (np.sqrt(2) - 1) * 100, (np.sqrt(4) - 1) * 100, 25.0, 100.0]})
print("Relative effect on safety stock (identical for every product because SS = Z x sigma x sqrt(L)):")
display(el.round(1))
put('el_lt25', el.iloc[0, 1]); put('el_lt2', el.iloc[1, 1]); put('el_lt4', el.iloc[2, 1])

# absolute table
tab = pd.DataFrame({p: {f'L={l}': z95 * products.loc[p, 'Demand_Std'] * np.sqrt(l) for l in (1, 2, 4, 6, 9, 12)} for p in 'ABC'}).round(1)
print("Safety stock (units) at 95 % for different lead times:")
display(tab)
for p in 'ABC':
    put(f'B7_{p}_L1', tab.loc['L=1', p]); put(f'B7_{p}_L12', tab.loc['L=12', p])

# heat-maps: lead time x coefficient of variation
cv_grid = np.array([5, 10, 15, 20, 25, 30])
lt_h = np.array([1, 2, 3, 4, 6, 8, 10])
fig, axes = plt.subplots(1, 3, figsize=(16, 4.4), sharey=True)
vmax = z95 * (cv_grid.max() / 100) * products['Avg_Demand'].max() * np.sqrt(lt_h.max())
vmax = z95 * (cv_grid.max() / 100) * 400 * np.sqrt(lt_h.max())
for ax, p in zip(axes, 'ABC'):
    mu = products.loc[p, 'Avg_Demand']
    grid = np.array([[z95 * (cv / 100) * mu * np.sqrt(l) for cv in cv_grid] for l in lt_h])
    sns.heatmap(pd.DataFrame(grid, index=lt_h, columns=cv_grid), annot=True, fmt='.0f', cmap='YlOrRd', vmin=0, vmax=vmax,
                cbar=(p == 'C'), cbar_kws={'label': 'Safety stock (units)'}, ax=ax, annot_kws={'size': 8})
    ax.set_title(f'Product {p} (avg demand {mu:.0f}/period)'); ax.set_xlabel('Coefficient of variation of demand (%)'); ax.grid(False)
axes[0].set_ylabel('Lead time (periods)')
plt.tight_layout(); plt.savefig('outputs/B7_sensitivity_heatmaps.png', dpi=150, bbox_inches='tight'); plt.show()
""")
interp("B7")

# ---------------------------------------------------------------- B8 BEFORE vs AFTER
md("""
---
## B8. Before AI vs After AI – Comparison of Plots *(requested by the professor)*
**Before (traditional):** one rule of thumb for the whole range – *"serve every product at 95 %"*.
**After (data-driven):** a **differentiated** service level per product, found from the simulation of safety stock and holding cost and its marginal-cost analysis (B6c: A 97 %, B 95 %, C 98 %). *The uniform 99 % policy is shown as a reference for "maximum service".*

Besides safety stock and holding cost, I add the **expected shortage per replenishment cycle** so the benefit of a higher service level is visible too. With lead-time demand N(μL, σ√L) and safety stock z·σ√L, the expected units short per cycle are σ√L · [φ(z) − z·(1 − Φ(z))] (the standard normal loss function).
""")
code("""
def loss_fn(z):                                            # standard normal loss function  E[(Z - z)+]
    return norm.pdf(z) - z * (1 - norm.cdf(z))

policies_b8 = {'Before AI: uniform 95 %': {p: 0.95 for p in 'ABC'},
               'After AI: differentiated': dict(rec),
               'Reference: uniform 99 %': {p: 0.99 for p in 'ABC'}}
rows = []
for name, lv in policies_b8.items():
    for p in 'ABC':
        r = products.loc[p]; s = lv[p]; z = norm.ppf(s)
        sd_lt = r['Demand_Std'] * np.sqrt(r['Lead_Time']); ss = z * sd_lt
        short = sd_lt * loss_fn(z)
        rows.append({'Policy': name, 'Product': p, 'Service_Level': s, 'Z': z, 'Safety_Stock': ss, 'Holding_Cost': ss * r['Holding_Cost'],
                     'Stockout_Prob_per_Cycle': 1 - s, 'Units_Short_per_Cycle': short,
                     'Short_%_of_LT_Demand': short / (r['Avg_Demand'] * r['Lead_Time']) * 100})
b8 = pd.DataFrame(rows)
print("Per product:")
display(b8[['Policy', 'Product', 'Service_Level', 'Safety_Stock', 'Holding_Cost', 'Stockout_Prob_per_Cycle', 'Units_Short_per_Cycle']].round(3))
tot = b8.groupby('Policy', sort=False).agg(Total_Safety_Stock=('Safety_Stock', 'sum'), Total_Holding_Cost=('Holding_Cost', 'sum'),
                                          Total_Units_Short_per_Cycle=('Units_Short_per_Cycle', 'sum'))
print("Portfolio totals:")
display(tot.round(2))
keys = ['b95', 'after', 'b99']
for k, (nm, rowt) in zip(keys, tot.iterrows()):
    put(f'ba_B_{k}_ss', rowt['Total_Safety_Stock']); put(f'ba_B_{k}_hc', rowt['Total_Holding_Cost']); put(f'ba_B_{k}_short', rowt['Total_Units_Short_per_Cycle'])
for k, nm in zip(keys, policies_b8):
    for p in 'ABC':
        r_ = b8[(b8.Policy == nm) & (b8.Product == p)].iloc[0]
        put(f'ba_B_{k}_{p}_short', r_['Units_Short_per_Cycle']); put(f'ba_B_{k}_{p}_sl', r_['Service_Level'])

# ---- Figure 1: the three product curves with the BEFORE and AFTER operating points -------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
for ax, p in zip(axes, 'ABC'):
    d = sim[sim.Product == p]
    ax.plot(d['Service_Level'], d['Safety_Stock'], color=BLUE, lw=2, label='Safety Stock')
    ax.plot(d['Service_Level'], d['Holding_Cost'], color=GREEN, lw=2, label='Holding Cost')
    ax.scatter([0.95], [at.loc[(p, 0.95), 'Holding_Cost']], marker='s', s=90, color='#7A8A99', zorder=6, label='Before AI: 95 % (uniform)')
    ax.scatter([rec[p]], [at.loc[(p, rec[p]), 'Holding_Cost']], marker='o', s=110, color='#0B6B4B', edgecolor='white', zorder=7, label=f'After AI: {rec[p]:.0%} (recommended)')
    ax.set_title(f'Product {p}'); ax.set_xlabel('Service Level'); ax.set_xlim(0.795, 0.995); ax.set_xticks([0.80, 0.85, 0.90, 0.95, 0.99])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0)); ax.legend(loc='upper left', fontsize=8)
axes[0].set_ylabel('Units / Cost'); axes[0].set_ylim(0, ymax * 1.08)
fig.suptitle('Before vs After AI – operating point on each product\\'s trade-off curve', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout(w_pad=2.5); plt.savefig('outputs/B8_before_after_curves.png', dpi=150, bbox_inches='tight'); plt.show()

# ---- Figure 2: portfolio comparison ---------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.3))
cols_p = ['#7A8A99', '#12805C', '#B7C4CF']
for ax, col, ttl, unit in [(axes[0], 'Total_Safety_Stock', 'Total safety stock', 'Units'), (axes[1], 'Total_Holding_Cost', 'Total holding cost per period', 'Currency'),
                           (axes[2], 'Total_Units_Short_per_Cycle', 'Expected units short per cycle (all products)', 'Units')]:
    bars = ax.bar(['Before AI\\nuniform 95 %', 'After AI\\ndifferentiated', 'Reference\\nuniform 99 %'], tot[col].values, color=cols_p)
    ax.bar_label(bars, fmt='%.1f', padding=2); ax.set_title(ttl); ax.set_ylabel(unit); ax.set_ylim(0, tot[col].max() * 1.15)
plt.tight_layout(); plt.savefig('outputs/B8_before_after_portfolio.png', dpi=150, bbox_inches='tight'); plt.show()
""")
interp("B8")


# ------------------------------------------------------------------ EXPORT
md("""
## Saving the Results
All result tables and the key metrics are written to the relative folder `outputs/` so they can be reused (for example in the one-page summary).
""")
code("""
df_out = df[['Item', 'Annual_Usage', 'Unit_Cost', 'Lead_Time', 'Past_Demand', 'Annual_Value', 'Cumulative%',
             'ABC_Category', 'Predicted_ABC', 'Predicted_Demand', 'Std_Dev', 'Safety_Stock']]
df_out.to_csv('outputs/partA_abc_forecast_safety_stock.csv', index=False)
sim.to_csv('outputs/partB_service_level_tradeoff.csv', index=False)
with open('outputs/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print("Saved files:")
for fn in sorted(os.listdir('outputs')):
    print(f"  outputs/{fn}  ({os.path.getsize(os.path.join('outputs', fn)) / 1024:,.1f} KB)")
print(f"\\n{len(metrics)} key metrics stored in outputs/metrics.json")
""")

md("""
## Export for the dashboards
One file, `dashboard_data.json`, holds every number the two dashboards (Next.js and Streamlit) display, so they always show exactly what this notebook computed. The tables are also saved as CSV files in `outputs/`.
""")
code("""
import datetime
def recs(frame, nd=4):
    return json.loads(frame.round(nd).to_json(orient='records'))

items = df.copy()
items['Rank'] = np.arange(1, len(items) + 1)
items['Tree_Split'] = np.where(items.index.isin(X_test.index), 'test', 'train')
items['LR_Split'] = np.where(items.index.isin(yr_test.index), 'test', 'train')
item_cols = ['Rank', 'Item', 'Annual_Usage', 'Unit_Cost', 'Lead_Time', 'Past_Demand', 'Annual_Value', 'Value_Share%', 'Cumulative%',
             'ABC_Category', 'Predicted_ABC', 'Traditional_ABC', 'Predicted_Demand', 'Std_Dev', 'Safety_Stock', 'SS_Value',
             'SS_Before', 'CSL_Before', 'CSL_After', 'Tree_Split', 'LR_Split']
items_out = items[item_cols]
items_out.round(4).to_csv('outputs/abc_table.csv', index=False)
items[['Item', 'Past_Demand', 'Annual_Usage', 'Predicted_Demand', 'LR_Split']].to_csv('outputs/forecast_table.csv', index=False)
items[['Item', 'ABC_Category', 'Predicted_Demand', 'Std_Dev', 'Lead_Time', 'Safety_Stock', 'SS_Value']].to_csv('outputs/safety_stock_table.csv', index=False)
products.reset_index().to_csv('outputs/partB_parameters.csv', index=False)
b8.round(4).to_csv('outputs/partB_before_after.csv', index=False)
sc.reset_index().rename(columns={'index': 'Metric'}).round(4).to_csv('outputs/partA_before_after_safety_stock.csv', index=False)
fc_cmp.reset_index().rename(columns={'index': 'Metric'}).round(4).to_csv('outputs/partA_before_after_forecast.csv', index=False)
cls_cmp.reset_index().rename(columns={'index': 'Metric'}).round(4).to_csv('outputs/partA_before_after_classification.csv', index=False)

tree_metrics = {'depth': int(best_depth), 'leaves': int(tree.get_n_leaves()), 'train_n': int(len(X_train)), 'test_n': int(len(X_test)),
                'acc_train': float(acc_train), 'acc_test': float(acc_test), 'labels': labels, 'confusion': cm.tolist(),
                'report': {k: {m_: float(v_) for m_, v_ in d.items()} if isinstance(d, dict) else float(d) for k, d in rep.items()},
                'importances': [{'feature': f_, 'importance': float(v_)} for f_, v_ in imp.items()],
                'depth_cv': recs(depth_tbl, 4), 'cv_folds': 5}
json.dump(tree_metrics, open('outputs/tree_metrics.json', 'w'), indent=2)

dash = {
  'meta': {'name': 'Krishna Mathur', 'enrollment_id': 'AS25DXB018', 'program': 'MAIB, September 2025', 'course': 'AI in Operations',
           'professor': 'Prof. Dr. Sandip Kumar Roy', 'task': 'Day 4 - Inventory Management and Optimization, Lab Activity + Lab Exercise',
           'date': '13 November 2026', 'seed': SEED, 'synthetic': True,
           'note': 'Part A data are SYNTHETIC (seed 42). Part B parameters are assumptions calibrated to the reference chart.'},
  'metrics': {k: v for k, v in metrics.items()},
  'abc_summary': recs(abc.reset_index().rename(columns={'ABC_Category': 'Category'}).drop(columns=['Reference (items / value)'])),
  'items': recs(items_out),
  'tree': tree_metrics,
  'forecast': {'coef': float(reg.coef_[0]), 'intercept': float(reg.intercept_), 'r2_test': float(r2_te), 'mae_test': float(mae_te),
               'rmse_test': float(rmse_te), 'r2_train': float(r2_tr), 'mae_train': float(mae_tr), 'rmse_train': float(rmse_tr),
               'coef_all': float(reg_all.coef_[0]), 'intercept_all': float(reg_all.intercept_)},
  'safety_stock': {'z_95': Z_95, 'sigma_pct': 10, 'by_class': recs(ss_sum.reset_index().rename(columns={'ABC_Category': 'Category'})),
                   'total': float(total_ss), 'total_value': float(ssv.sum())},
  'partB': {'parameters': recs(products.reset_index()), 'service_levels': [float(s) for s in service_levels],
            'curves': recs(sim, 4),
            'recommendation': {'tolerance': TOL, 'levels': {p: float(rec[p]) for p in 'ABC'}, 'sensitivity': sens.to_dict()},
            'policies': recs(pol.reset_index().rename(columns={'index': 'Policy'}), 3),
            'before_after': recs(b8, 4), 'before_after_totals': recs(tot.reset_index(), 4)},
  'before_after': {
      'classification': {'before': {'accuracy': float(acc_trad), 'macro_f1': float(rep_trad['macro avg']['f1-score']), 'recall_A': float(recallA_trad), 'confusion': cm_trad.tolist()},
                         'after': {'accuracy': float(acc_test), 'macro_f1': float(rep['macro avg']['f1-score']), 'recall_A': float(recallA_ai), 'confusion': cm.tolist()}},
      'forecast': {'before': {k.split(' (')[0]: float(v) for k, v in fc_cmp.iloc[:, 0].items()}, 'after': {k.split(' (')[0]: float(v) for k, v in fc_cmp.iloc[:, 1].items()},
                   'points': [{'item': it, 'actual': float(actual_t[it]), 'before': float(naive_t[it]), 'after': float(ai_t[it])} for it in yr_test.index]},
      'safety_stock': {'flat_pct': float(flat_pct * 100), 'summary': {r_: {'before': float(sc.loc[r_].iloc[0]), 'after': float(sc.loc[r_].iloc[1])} for r_ in sc.index}}},
  'generated_by': 'AS25DXB018_Krishna_Mathur_Day4_Inventory_Management.ipynb (executed, seed 42)'}
for path in ('outputs/dashboard_data.json', 'data/dashboard_data.json'):
    with open(path, 'w') as f:
        json.dump(dash, f, separators=(',', ':'))
print(f"dashboard_data.json written: {os.path.getsize('outputs/dashboard_data.json') / 1024:,.0f} KB | items: {len(items_out)} | curves: {len(sim)} rows")
print("Also saved: abc_table.csv, forecast_table.csv, safety_stock_table.csv, partB_parameters.csv, partB_before_after.csv, tree_metrics.json, partA_before_after_*.csv")
""")


# ------------------------------------------------------------------ END MATTER
interp("CONCLUSION")
interp("TAKEAWAYS")
interp("LIMITATIONS")
md("""
## References

1. Roy, S. K. (2026). *Inventory Management and Optimization* – Day 4 lecture slides and sample Colab notebook, AI in Operations, MAIB (September 2025), 13 November 2026.
2. Silver, E. A., Pyke, D. F., & Thomas, D. J. (2017). *Inventory and Production Management in Supply Chains* (4th ed.). CRC Press. (ABC analysis, safety stock, cycle service level.)
3. Chopra, S., & Meindl, P. (2016). *Supply Chain Management: Strategy, Planning, and Operation* (6th ed.). Pearson. (Safety stock and service-level trade-off.)
4. Nahmias, S., & Olsen, T. L. (2015). *Production and Operations Analysis* (7th ed.). Waveland Press.
5. Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.
6. Virtanen, P. et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods, 17*, 261–272.
7. Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering, 9*(3), 90–95.
8. The Investors Book – Inventory Management (https://theinvestorsbook.com/inventory-management.html), as cited on slide 7 of the lecture.
""")
