# -*- coding: utf-8 -*-
"""Business interpretations placed AFTER the outputs. Numbers come from the executed metrics (metrics.json)."""

def get(key, m):
    f = lambda k, d=1: f"{m(k):,.{d}f}"
    T = {}

    T["A0"] = """
**Business interpretation – baseline.**
- A1 and A2 (the two high-value items) are class **A**, A3 falls into **B** because it crosses the 70 % mark, and the four low-value items are **C** – the professor's rule is reproduced exactly (70 % → A, next 20 % → B, rest → C).
- The decision tree reproduces every label (in-sample), and the buffers are largest for the fast-moving items (A1: 226 units, A2: 194 units) and smallest for C2 (14 units).
- With only 7 rows a tree can always memorise the labels, so this accuracy says nothing about generalisation. That is why the rest of the lab uses a larger dataset and a **hold-out test set**.
"""

    T["DATA"] = f"""
**Reading the data.** The dataset has {m('n_items'):.0f} SKUs and no missing values. Usage and unit cost are right-skewed (mean annual usage ≈ 855 units vs median ≈ 507; a few items are priced at 20–40 per unit while the median is ≈ 6), which is the pattern that makes ABC analysis worthwhile: a minority of SKUs will dominate the annual spend. Remember that this is **synthetic data**, generated with seed 42 and saved to `data/inventory_synthetic_data.csv`.
"""

    T["A1"] = f"""
**Business interpretation – ABC classification.**
- **Class A:** {m('abc_A_items'):.0f} items ({f('abc_A_items_pct')} % of the catalogue) generate **{f('abc_A_value_pct')} %** of annual consumption value → tight control, frequent review, accurate forecasts and a high service level.
- **Class B:** {m('abc_B_items'):.0f} items ({f('abc_B_items_pct')} %) generate {f('abc_B_value_pct')} % of value → moderate control, periodic review.
- **Class C:** {m('abc_C_items'):.0f} items ({f('abc_C_items_pct')} %) generate only **{f('abc_C_value_pct')} %** of value → simple rules (e.g. bulk ordering, low review frequency).
- The split (≈ 21 % / 28 % / 51 % of items carrying 70 % / 20 % / 10 % of value) is close to the textbook Pareto reference of ~20 / ~30 / ~50 % of items. Half of the catalogue accounts for one-tenth of the spend, so management attention should not be spread evenly. The generator was tuned for this shape, so this closeness is by design and not a discovery about real retail data.
- By the professor's rule the item that crosses 70 % is placed in B, so class A carries just under 70 % ({f('abc_A_value_pct', 2)} %).
"""

    T["A2a"] = f"""
**Business interpretation – decision tree.**
- **Split:** {m('tree_train_n'):.0f} training items (70 %) and {m('tree_test_n'):.0f} unseen test items (30 %), stratified so that A, B and C keep the same proportions in both parts.
- **Accuracy:** **{f('tree_acc_test', 3)}** on the test set ({m('tree_acc_test')*100:.1f} %) vs {f('tree_acc_train', 3)} on the training set. The gap shows that the tree (depth {m('tree_depth'):.0f}, chosen by cross-validation) fits the training data almost perfectly and loses about nine points on new items – a mild overfit that is worth knowing about.
- **Confusion matrix:** all mistakes are between *neighbouring* classes (A↔B: 4 + 5 items; B↔C: 3 + 2 items). **No A item was predicted as C and no C item as A**, so the model never makes a gross error – it only blurs the class boundaries.
- **Per-class quality:** C is classified best (F1 = {f('tree_f1_C', 3)}), A is good (F1 = {f('tree_f1_A', 3)}) and **B is the hardest** (F1 = {f('tree_f1_B', 3)}) because it is the "middle" class squeezed between two boundaries. Macro-F1 = {f('tree_macro_f1', 3)}.
- **Feature importance:** `Unit_Cost` ({m('imp_Unit_Cost'):.2f}), `Annual_Usage` ({m('imp_Annual_Usage'):.2f}) and `Past_Demand` ({m('imp_Past_Demand'):.2f}) drive the prediction; `Lead_Time` is almost irrelevant ({m('imp_Lead_Time'):.2f}). This is exactly what we expect: the ABC class is defined by *usage × cost*, so price and volume matter and lead time does not.
"""

    T["A2b"] = f"""
**Business interpretation – confusion matrix and importances.** The diagonal dominates the heat-map ({27+35+74} of 150 test items correct). The planner can trust a predicted "C" almost blindly (precision {f('tree_prec_C', 2)}), whereas a predicted "B" deserves a quick manual check because it is the most frequently confused class. The importance bars confirm that the model has learned the economic logic of ABC analysis (cost and volume) rather than something spurious such as lead time.
"""

    T["A2c"] = f"""
**Business interpretation – tree structure.** The first split is on **`Annual_Usage`** (≈ 752 units/year). Low-usage items (231 of 350 training items) go mostly to C unless `Unit_Cost` is high (> ≈ 7.7 sends them towards B), while the high-usage branch (119 items, 60 of them A) is separated by `Unit_Cost` (≈ 7.8) and a second usage threshold (≈ 857): **usage above ≈ 860 units and unit cost above ≈ 7.8 gives a pure class-A leaf (43 of 43 training items)**. These are human-readable rules a buyer can apply without software. The full tree has {m('tree_leaves'):.0f} leaves; only the top three levels are drawn here to keep the figure legible.
"""

    T["A3"] = f"""
**Business interpretation – demand forecast.**
- **Equation:** `Annual_Usage = {m('lr_intercept'):.2f} + {m('lr_coef'):.4f} × Past_Demand` (test-split model). A slope of {m('lr_coef'):.3f} means that next year's demand is forecast at essentially **the same level as last year's, with a ≈ 0.1 % uplift**, and the intercept is negligible.
- **R² (test) = {m('lr_r2_test'):.4f}**: last year's demand explains ≈ 99 % of the variation in this year's demand. Train R² = {m('lr_r2_train'):.4f}, so the model generalises – there is no overfitting.
- **Errors (test):** MAE = **{f('lr_mae_test')} units** and RMSE = **{f('lr_rmse_test')} units** on items whose mean annual demand is ≈ {m('mean_usage'):,.0f} units, i.e. a typical error of ≈ 7 % of mean demand (RMSE > MAE because a few high-volume items have larger absolute errors).
- The actual-vs-predicted plot hugs the 45° line and the residuals scatter around zero with a funnel shape (errors grow with volume – larger items are harder to forecast in absolute units).
- **Caution:** this very high R² is partly a property of my synthetic data (usage was generated as a noisy copy of past demand). Real retail demand has trend and seasonality and the fit would be lower.
"""

    T["A4"] = f"""
**Business interpretation – safety stock.**
- The worked example shows the mechanics: Z (1.65) × σ (10 % of predicted demand) × √lead time. Longer lead times and higher forecast demand both enlarge the buffer.
- **Total safety stock = {m('ss_total'):,.0f} units** (≈ {f('ss_pct_demand')} % of total predicted demand). Class **A holds {m('ss_A_total'):,.0f} units ({f('ss_A_share')} % of all buffer units)**, B {m('ss_B_total'):,.0f} units ({f('ss_B_share')} %) and C {m('ss_C_total'):,.0f} units ({f('ss_C_share')} %).
- Because σ is a fixed 10 % of demand, the buffer is ≈ 29 % of predicted demand in *every* class; the classes differ in **absolute size** (average buffer: A {f('ss_A_avg', 0)}, B {f('ss_B_avg', 0)}, C {f('ss_C_avg', 0)} units per item).
- **Money tied up:** valued at unit cost the buffer is ≈ {m('ss_total_value'):,.0f} currency units, and **class A alone accounts for {m('ss_A_value')/m('ss_total_value')*100:.0f} %** of it ({m('ss_A_value'):,.0f}) although it is only 21 % of the items. This is where working capital is locked up and where better forecasts or shorter lead times pay off most.
"""

    T["A5"] = f"""
**Business interpretation – visuals.**
- **Pareto chart:** the cumulative curve rises steeply – the first ≈ 100 items (class A) already reach 70 % of value, while the long tail of class C (≈ 255 items) adds only the last 10 %. The bars shrink quickly, so the few tall red bars are the items worth the planner's time.
- **Counts and value share:** class C is the *largest by count* (≈ 51 %) but the *smallest by value* (≈ 10 %); class A is the opposite. The donut chart makes the "vital few, trivial many" message obvious.
- **Safety stock by item and class:** the 25 largest buffers are **22 class-A items and 3 class-B items (none from C)**, and the biggest single SKUs hold roughly 1,000–2,000 units each – these are the **inventory-risk hot-spots** to review first for lead-time reduction or supplier reliability. Class A holds {f('ss_A_share', 0)} % of all buffer units, class C only {f('ss_C_share', 0)} %, in line with the demand each class has to cover.
"""

    T["A6"] = f"""
**Business interpretation – the three learning outcomes.**

**1. How AI enhances traditional inventory models.**
- Traditional practice computes ABC and safety stock **once, from last year's numbers**. Here ML adds (i) a *forecast* – regression replaces "next year = last year" and cuts forecast error slightly (MAE {f('lr_mae_test')} vs {f('naive_mae')} units, **{f('mae_reduction_pct')} % lower**) – and (ii) a *learned classifier* that labels items without recomputing the cumulative table.
- The honest takeaway is that **on this synthetic data the gain from regression is small** (past demand is already a very good predictor); the benefit would be larger with trend, seasonality or extra drivers (price, promotions). The forecast also changes the buffer: {m('ss_total'):,.0f} units with the regression forecast vs {m('ss_total_naive'):,.0f} with the naive forecast ({(m('ss_total')/m('ss_total_naive')-1)*100:+.1f} %), because the model removes the downward bias of last year's demand.

**2. Classification and regression for operational decisions.**
- **Classification (decision tree):** decides *how much management attention* an item gets. For the three new items, the tree labelled NEW_1 as A and NEW_3 as C correctly; **NEW_2 (value 3,500) was labelled C but the value rule makes it B** – a borderline case, consistent with B being the hardest class. Result: {m('new_items_correct'):.0f} of 3 new items correct, which is exactly the kind of boundary item a planner should double-check.
- **Regression (linear model):** decides *how much to stock*. The forecast feeds directly into the safety-stock formula, e.g. NEW_1 gets a buffer of 944 units and NEW_3 only 37 units, which turns a model output into an order-policy parameter.

**3. Visualising and interpreting inventory risk buffers.**
- The Pareto chart shows *where value is concentrated*; the safety-stock bar charts show *where the buffer (risk protection) and the money are concentrated*. Reading them together: class A needs the best forecasts (an error there costs the most), class C can run on simple rules, and the large single-item buffers are the first candidates for lead-time or variability reduction.
"""

    T["B1"] = f"""
**Business interpretation – parameters.** The three products are deliberately different:
- **A** – high volume (400/period), *stable* demand (CV = {f('B_cv_A')} %), lead time 3, holding cost 2.00.
- **B** – medium volume (250/period) but *highly volatile* demand (CV = {f('B_cv_B')} %) and the *longest* lead time (4), cheapest to hold (1.50).
- **C** – low volume (150/period), moderate variability (CV = {f('B_cv_C')} %), *shortest* lead time (2) but the *most expensive* to hold (2.50).

The column σ·√L (std. deviation of demand over the lead time) is what really scales the buffer: B ({f('B_sig_lt_B', 1)}) is about **1.9×** A ({f('B_sig_lt_A', 1)}) and **3.5×** C ({f('B_sig_lt_C', 1)}). So B will need the biggest buffers even though its average demand is not the highest.
"""

    T["B3"] = f"""
**Business interpretation – Z-scores.** The Z-score rises slowly at first and sharply at the top end: 80 % → {f('Z_80', 2)}, 90 % → {f('Z_90', 2)}, 95 % → {f('Z_95', 2)} (≈ the 1.65 used in Part A), 99 % → {f('Z_99', 2)}. Going from 80 % to 90 % (+10 points) adds {m('Z_90')-m('Z_80'):.2f} to Z, whereas going from 90 % to 99 % (+9 points) adds {m('Z_99')-m('Z_90'):.2f} – more than twice as much. The tail of the normal curve is what makes the last points of service so expensive.
"""

    T["B4"] = f"""
**Business interpretation – safety stock and holding cost, and simulation check.**
- At every service level Product **B** needs the largest buffer and Product **C** the smallest (e.g. at 95 %: B {f('B_B_ss_95')}, A {f('B_A_ss_95')}, C {f('B_C_ss_95')} units), in line with the σ·√L ranking.
- Holding cost = safety stock × cost per unit. C has the highest unit holding cost (2.50) but still the lowest *total* holding cost because its buffer is small.
- **Monte-Carlo check:** simulating {200000:,} lead-time demands per product, the achieved service levels match the targets within **{f('mc_max_err_pp', 2)} percentage points** (sampling noise), so the Z-based formula really delivers the intended probability of not stocking out – *under the normal-demand assumption*.
"""

    T["B5"] = f"""
**Business interpretation – the trade-off figure.**
- **Blue (safety stock) and green (holding cost) both rise with service level, and they rise non-linearly:** the curves are gentle between 80 % and 90 % and bend steeply above ≈ 95 %.
- **Same y-scale in all three panels** makes the comparison direct: Product **B** reaches ≈ {f('B_B_hc_99', 0)} in holding cost at 99 %, A ≈ {f('B_A_hc_99', 0)} and C ≈ {f('B_C_hc_99', 0)}; B's curves are the highest and C's the flattest.
- Green is above blue in every panel because holding cost = safety stock × cost per unit and every unit cost is above 1; the green-to-blue ratio is exactly the unit holding cost (C: 2.5×, A: 2.0×, B: 1.5×), so the two lines are parallel in shape and differ only by that factor.
- The curves are smooth because they are deterministic (Z × σ√L); the reference chart on slide 33 has small kinks, which suggests it was produced with noisy/simulated inputs. The scale, colours, layout and ranking of the products (B > A > C) are the same.
"""

    T["B6a"] = f"""
**Business interpretation – effect of service-level decisions.**
- **From 80 % to 99 %** the buffer of Product A grows from {f('B_A_ss_80')} to {f('B_A_ss_99')} units (×{m('B_A_ss_99')/m('B_A_ss_80'):.1f}); B from {f('B_B_ss_80')} to {f('B_B_ss_99')} (×{m('B_B_ss_99')/m('B_B_ss_80'):.1f}); C from {f('B_C_ss_80')} to {f('B_C_ss_99')} (×{m('B_C_ss_99')/m('B_C_ss_80'):.1f}).
- **From 95 % to 99 %** safety stock and holding cost both rise by **{f('B_inc_pct')} %** for *every* product. The relative increase is identical because safety stock is proportional to Z (2.33 / 1.64 = 1.41) – what differs is the **absolute** burden: B needs **+{f('B_B_extra_units')} units** (+{f('B_B_extra_cost')} cost/period), A +{f('B_A_extra_units')} units (+{f('B_A_extra_cost')}), C +{f('B_C_extra_units')} units (+{f('B_C_extra_cost')}).
- Four extra points of service therefore raise the holding bill by about two-fifths – a sizeable price for a gain that customers may barely notice.
"""

    T["B6b"] = f"""
**Business interpretation – non-linearity and marginal cost.**
- **Non-linear growth is confirmed numerically.** The 80 → 90 % step (10 points) adds {f('B_A_d_80_90')} / {f('B_B_d_80_90')} / {f('B_C_d_80_90')} units for A / B / C, but the 90 → 99 % step (only 9 points) adds {f('B_A_d_90_99')} / {f('B_B_d_90_99')} / {f('B_C_d_90_99')} units – **about 2.4× more** with fewer points.
- The marginal safety stock of the last point (98 → 99 %) is ≈ **{f('marg_ratio')} times** the marginal stock of the first point (80 → 81 %) for every product (e.g. A: 1.9 → 14.2 units per point; B: 3.6 → 27.3).
- The marginal holding cost of the last point is {f('B_A_marg_hc_99')} (A), **{f('B_B_marg_hc_99')} (B)** and {f('B_C_marg_hc_99')} (C) per period: the 99th point is far more expensive than the 81st for every product, and most expensive for the volatile Product B. This is the "diminishing returns" curve that the recommendation below is built on.
"""

    T["B6c"] = f"""
**Business interpretation – recommended service levels (tolerance = 15 cost units per extra point).**

| Product | Profile | Recommended service level | Safety stock | Holding cost / period |
|---|---|---|---|---|
| **A** | high volume, stable (CV 7.5 %) | **{m('rec_A')*100:.0f} %** | {f('rec_A_ss')} units | {f('rec_A_hc')} |
| **B** | volatile (CV 20 %), long lead time | **{m('rec_B')*100:.0f} %** | {f('rec_B_ss')} units | {f('rec_B_hc')} |
| **C** | low volume, short lead time, dearest to hold | **{m('rec_C')*100:.0f} %** | {f('rec_C_ss')} units | {f('rec_C_hc')} |

- **Product C → 98 %:** the buffer is small (≈ 58 units), so protecting customers is cheap in absolute terms; going to 99 % would cost only 19 extra per period. High service is affordable.
- **Product A → 97 %:** a high-volume, stable fast mover where stock-outs hurt most revenue; the buffer stays moderate (≈ 98 units) and 99 % would add 46 per period, which is only worth it if A is strategic.
- **Product B → 95 %:** B's volatility (CV 20 %) and 4-period lead time make every extra point the most expensive (up to 40.9 per point at 99 %); reaching 99 % would cost 102 more per period. A 95 % policy is the sensible ceiling, and the better lever is to *attack the causes* – improve the forecast, shorten the lead time or pool stock – rather than add buffer.
- **Portfolio view:** the recommended mix holds {f('pol_Recommended_ss', 0)} units at a holding cost of {f('pol_Recommended_hc', 0)} per period – **{m('pol_Uniform_99_hc')-m('pol_Recommended_hc'):.0f} (≈ {(1-m('pol_Recommended_hc')/m('pol_Uniform_99_hc'))*100:.0f} %) cheaper than a uniform 99 % policy ({f('pol_Uniform_99_hc', 0)})** and only {m('pol_Recommended_hc')-m('pol_Uniform_95_hc'):.0f} (≈ {(m('pol_Recommended_hc')/m('pol_Uniform_95_hc')-1)*100:.0f} %) more than a uniform 95 % policy ({f('pol_Uniform_95_hc', 0)}), while giving A and C a higher service level.
- **How robust is this?** The tolerance is a planner assumption: with a stricter tolerance of 10 the levels drop to 95 / 92 / 97 % and with a looser 25 they rise to 98 / 97 / 99 % (A / B / C), but the **ranking C ≥ A ≥ B never changes**. If the real stock-out cost per unit were known, it would replace this tolerance (newsvendor logic).
"""

    T["B7"] = f"""
**Business interpretation – sensitivity.**
- **Lead time (concave, square-root curve):** doubling lead time raises safety stock by only **{f('el_lt2')} %** (not 100 %) and quadrupling it by {f('el_lt4', 0)} %. From L = 1 to L = 12 the buffer at 95 % grows from {f('B7_A_L1')} to {f('B7_A_L12')} units for A, {f('B7_B_L1')} → {f('B7_B_L12')} for B and {f('B7_C_L1')} → {f('B7_C_L12')} for C. Shortening lead time still helps, but with diminishing returns the shorter it gets.
- **Demand variability (linear):** safety stock is directly proportional to σ – a 25 % rise in volatility raises the buffer by 25 % and a doubling raises it by 100 %. **Demand variability is therefore a much stronger lever than lead time** (σ ×2 → +100 % vs lead time ×2 → +41 %).
- The heat-maps show the two drivers together: Product B with a CV of 30 % and a 10-period lead time would need ≈ 390 units at 95 %, whereas A with CV 5 % and one period needs about 33 units. The same pair of drivers explains why B is the most expensive product: it has the highest CV (20 %) *and* the longest lead time (4 periods).
- **Policy implication:** improving forecast accuracy (lower σ) and negotiating shorter lead times both cut the buffer *without* lowering the service level – an alternative to simply accepting a lower service level.
"""

    T["CONCLUSION"] = f"""
## Conclusion

**Part A.** ABC analysis of the 500 synthetic SKUs gave a clean Pareto structure: **{m('abc_A_items'):.0f} class-A items ({f('abc_A_items_pct')} %) hold {f('abc_A_value_pct')} % of the annual value**, class B {f('abc_B_value_pct')} % and class C ({f('abc_C_items_pct')} % of the items) only {f('abc_C_value_pct')} %. A decision tree learned to predict the class from the four item features with **{m('tree_acc_test')*100:.1f} % test accuracy** (macro-F1 {f('tree_macro_f1', 3)}), making errors only between neighbouring classes, and a linear regression forecast demand with **R² = {m('lr_r2_test'):.3f}** (MAE {f('lr_mae_test')} units). Feeding the forecast into Z · σ · √LT with Z = 1.65 gives a total safety stock of **{m('ss_total'):,.0f} units**, of which class A holds {f('ss_A_share', 0)} % of the units and about {m('ss_A_value')/m('ss_total_value')*100:.0f} % of the buffer value.

**Part B.** For three products with different volatility, lead time and holding cost, raising the service level from 95 % to 99 % increases safety stock and holding cost by **{f('B_inc_pct')} %** each, while the marginal cost of the last point is about {f('marg_ratio', 1)} times that of the first. A uniform 99 % policy would cost ≈ {f('pol_Uniform_99_hc', 0)} per period against ≈ {f('pol_Recommended_hc', 0)} for the recommended differentiated policy (**A 97 %, B 95 %, C 98 %**), i.e. ≈ {(1-m('pol_Recommended_hc')/m('pol_Uniform_99_hc'))*100:.0f} % cheaper. Demand variability (linear) is a stronger lever on the buffer than lead time (square-root).
"""

    T["TAKEAWAYS"] = f"""
## Key Takeaways

1. **Prioritise:** about a fifth of the SKUs carries 70 % of the value – focus control, forecasting effort and service level on class A.
2. **ML complements, it does not replace, ABC analysis:** the decision tree reproduces the ABC rule with ≈ {m('tree_acc_test')*100:.0f} % test accuracy and is useful for labelling *new* items; borderline B items still need a human check.
3. **Forecasts feed buffers:** a regression forecast (R² ≈ {m('lr_r2_test'):.2f}) turns directly into safety-stock parameters, but on this data it improved on the naive "same as last year" forecast by only ≈ {f('mae_reduction_pct', 0)} % in MAE.
4. **Service level is not free:** safety stock grows with Z, which is convex in the service level – +4 points (95 → 99 %) costs **+{f('B_inc_pct', 0)} %** in buffer and holding cost for every product.
5. **Differentiate service levels by product:** high-volume stable items (A) and cheap-to-protect items (C) justify 97–98 %; the volatile, long-lead-time Product B is best held at 95 %, with effort put into reducing its variability.
6. **Reduce the drivers, not just the service level:** buffer ∝ σ and ∝ √L, so better forecasts and shorter lead times cut inventory without hurting customers.
"""

    T["LIMITATIONS"] = f"""
## Limitations

- **Synthetic data.** Part A uses generated data (seed 42), not real retail records; all numbers illustrate the method only. The generator was tuned so the ABC split resembles the textbook proportions, so that match is by construction.
- **Dataset size and test-set noise.** I first generated 200 SKUs; with only 60 test items the tree scored ≈ 78 % and results changed a lot with the sample size. I therefore enlarged the data to 500 SKUs (150 test items) for a more stable estimate. Even so, a single split is noisy – a ±3–5 point swing in accuracy would not be surprising.
- **The ABC label is a deterministic rule** (usage × cost, cumulative thresholds), so the classifier approximates a rule it could compute exactly; its value lies in speed for new items, not in discovering new classes. The tree also overfits slightly (train {f('tree_acc_train', 3)} vs test {f('tree_acc_test', 3)}).
- **Simple forecast model.** One predictor (last year's demand), no trend, seasonality, price or promotions; R² is inflated by how the synthetic data was built, and the improvement over a naive forecast is small ({f('mae_reduction_pct')} % in MAE).
- **σ = 10 % of predicted demand is assumed**, not estimated from forecast errors, and the lead time is used in the same unit as the demand, as in the professor's code – which is why buffers come out at ≈ {f('ss_pct_demand', 0)} % of annual demand. A strict implementation would convert σ to the lead-time period.
- **Normal, independent demand** during the lead time; no lead-time variability, no supplier unreliability, no demand correlation between periods.
- **Part B parameters and the 15-units-per-point tolerance are my assumptions**; no stock-out (shortage) cost was available, so the recommended service levels are policy suggestions, not cost-optimal solutions. The relative increase from 95 % to 99 % (+{f('B_inc_pct')} %) is identical for all products by construction.
- **Holding cost** is only the cost of the safety-stock units; order cost, cycle stock and obsolescence are not modelled.
"""


    T["A7a"] = f"""
**Business interpretation – classification, before vs after AI.**
- Judged against the true value-based ABC class on the same {m('tree_test_n'):.0f} test items, the usage-only rule of thumb is right for **{m('ba_cls_acc_before')*100:.1f} %** of the items; the decision tree is right for **{m('ba_cls_acc_after')*100:.1f} %** (**+{(m('ba_cls_acc_after')-m('ba_cls_acc_before'))*100:.1f} percentage points**). Macro-F1 rises from {m('ba_cls_f1_before'):.2f} to {m('ba_cls_f1_after'):.2f}.
- **The costly mistake is missing class-A items.** The rule flags only **{m('ba_cls_a_total')-m('ba_cls_a_missed_before'):.0f} of {m('ba_cls_a_total'):.0f}** A items (recall {m('ba_cls_recallA_before'):.0%}); 11 of the missed ones are called B and 2 are called C. The tree finds **{m('ba_cls_a_total')-m('ba_cls_a_missed_after'):.0f} of {m('ba_cls_a_total'):.0f}** (recall {m('ba_cls_recallA_after'):.0%}) and none is called C.
- Why: the rule looks at volume only, so a cheap high-volume item looks like A and an expensive moderate-volume item is overlooked. The tree learns that **unit cost is the most important feature** (A2) and picks up the thresholds from data.
- *Fair reading:* this compares AI with a quick rule of thumb. The exact value-based ABC (A1) is perfectly accurate by definition but needs the whole cumulative table to be recomputed; the tree's practical value is labelling *new or changed* items instantly, with the borderline B items still deserving a manual check.
"""

    T["A7b"] = f"""
**Business interpretation – forecast, before vs after AI.**
- **The gain is small.** Test MAE falls from {m('ba_fc_mae_before'):.1f} to **{m('ba_fc_mae_after'):.1f} units** ({(1-m('ba_fc_mae_after')/m('ba_fc_mae_before'))*100:.1f} % lower) and RMSE from {m('ba_fc_rmse_before'):.1f} to {m('ba_fc_rmse_after'):.1f} ({(1-m('ba_fc_rmse_after')/m('ba_fc_rmse_before'))*100:.1f} % lower). R² is {m('ba_fc_r2_before'):.3f} vs {m('ba_fc_r2_after'):.3f}.
- **What the regression does fix is the systematic bias:** the naive forecast under-forecasts by {m('ba_fc_bias_before'):.1f} units per item on average (last year's demand was about 2 % lower than this year's in the data), the regression by {m('ba_fc_bias_after'):.1f} – roughly **{(1-m('ba_fc_bias_after')/m('ba_fc_bias_before'))*100:.0f} % less bias**. In percentage terms the picture is mixed: MAPE is {m('ba_fc_mape_before'):.2f} % for the naive forecast and {m('ba_fc_mape_after'):.2f} % for the regression, i.e. slightly *worse*, because the regression trades a little accuracy on small items for less bias on large ones.
- **Honest conclusion:** the two scatter plots look almost the same. On this synthetic data last year's demand is already an excellent predictor, so a one-variable regression cannot add much. Claims in the literature of 20–50 % lower forecast error come from richer models and real data with trend, seasonality and promotions; **they are not reproduced here**.
"""

    T["A7c"] = f"""
**Business interpretation – safety stock, before vs after AI (same total budget).**
- Both approaches hold exactly **{m('ba_ss_units_after'):,.0f} units** of buffer (worth ≈ {m('ba_ss_value_before'):,.0f} vs {m('ba_ss_value_after'):,.0f} at unit cost). The flat rule uses {m('ba_ss_flat_pct'):.1f} % of last year's demand for every item.
- **What changes is how the protection is spread.** The flat rule ignores lead time, so the left plot shows no relation between buffer and lead time. Under the same risk model, it gives **{m('ba_ss_below90_before'):.0f} items less than 90 % service** (the worst item only {m('ba_ss_csl_min_before')*100:.1f} %) while others get close to 100 %. The Z · σ · √LT buffer gives every item ≈ 95 %: **no item below 90 %**, worst item {m('ba_ss_csl_min_after')*100:.1f} %, spread between items {m('ba_ss_csl_sd_before'):.2f} → {m('ba_ss_csl_sd_after'):.2f} percentage points.
- In business terms: with the same inventory investment, the AI-based rule moves units from short-lead-time, low-risk items to long-lead-time, high-risk items, so nothing is left dangerously unprotected.
- *Limit of this test:* both rules are evaluated with my assumed σ model (10 % of predicted demand), so it shows consistency of protection, not measured stock-outs.
"""

    T["A7"] = f"""
**Business interpretation – Part A scorecard.** Before → after AI on the same items:
- **Classification:** {m('ba_cls_acc_before')*100:.1f} % → **{m('ba_cls_acc_after')*100:.1f} %** accuracy; class-A items found {m('ba_cls_a_total')-m('ba_cls_a_missed_before'):.0f} → **{m('ba_cls_a_total')-m('ba_cls_a_missed_after'):.0f}** of {m('ba_cls_a_total'):.0f}. *Clear gain.*
- **Forecast:** MAE {m('ba_fc_mae_before'):.1f} → {m('ba_fc_mae_after'):.1f}, bias +{m('ba_fc_bias_before'):.1f} → +{m('ba_fc_bias_after'):.1f}. *Marginal gain – honest result on this data.*
- **Safety stock (same budget):** items below 90 % service {m('ba_ss_below90_before'):.0f} → **{m('ba_ss_below90_after'):.0f}**; lowest item {m('ba_ss_csl_min_before')*100:.1f} % → **{m('ba_ss_csl_min_after')*100:.1f} %**. *Clear gain in risk consistency.*

The pattern is typical: AI adds the most where the traditional method **ignores information** (cost in the classification, lead time in the buffer) and the least where the traditional method is already close to the best possible (a near-perfect last-year forecast).
"""

    T["B8"] = f"""
**Business interpretation – Part B, before vs after AI.**
- **Before (uniform 95 %):** total safety stock {m('ba_B_b95_ss'):.0f} units, holding cost {m('ba_B_b95_hc'):.0f} per period, **{m('ba_B_b95_short'):.2f} expected units short per cycle** across the three products.
- **After (A 97 %, B 95 %, C 98 %):** {m('ba_B_after_ss'):.0f} units and {m('ba_B_after_hc'):.0f} per period – **+{m('ba_B_after_hc')-m('ba_B_b95_hc'):.0f} (+{(m('ba_B_after_hc')/m('ba_B_b95_hc')-1)*100:.0f} %) holding cost**, but expected shortage falls to **{m('ba_B_after_short'):.2f} units (−{(1-m('ba_B_after_short')/m('ba_B_b95_short'))*100:.0f} %)**. Product A's shortage drops from {m('ba_B_b95_A_short'):.2f} to {m('ba_B_after_A_short'):.2f} and Product C's from {m('ba_B_b95_C_short'):.2f} to {m('ba_B_after_C_short'):.2f}; Product B is deliberately left at 95 % ({m('ba_B_after_B_short'):.2f}).
- **Reference (uniform 99 %):** shortage only {m('ba_B_b99_short'):.2f} but at {m('ba_B_b99_hc'):.0f} per period (+{(m('ba_B_b99_hc')/m('ba_B_b95_hc')-1)*100:.0f} % vs uniform 95 %) – it buys the lowest risk at the highest price, and most of the extra money goes to the volatile Product B.
- **Reading the curves:** the grey square (before) and green dot (after) sit on the same cost curve; the differentiated policy moves A and C up the curve where the extra points are cheap and leaves B where the next points would be most expensive. Product B still carries **{m('ba_B_after_B_short')/m('ba_B_after_short')*100:.0f} % of the remaining expected shortage** – the lever there is lower demand variability or shorter lead time (B7), not more buffer.
- *Caveat:* "after AI" here means a data-driven, simulation-based policy built on my assumed parameters and the 15-unit cost tolerance; it is not trained on real data and the gain is a trade (more cost for less shortage), not a free improvement.
"""

    return T.get(key)
