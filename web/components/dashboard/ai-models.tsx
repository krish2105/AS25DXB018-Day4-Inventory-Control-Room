"use client"
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts"
import type { Dashboard } from "@/lib/data"
import { fmt } from "@/lib/stats"
import { COLORS, ChartTip, DataNote, KpiCard, Panel } from "./ui"
import { ConfusionMatrix } from "./confusion"

const FEAT: Record<string, string> = { Annual_Usage: "Annual usage", Unit_Cost: "Unit cost", Lead_Time: "Lead time", Past_Demand: "Past demand" }

export function AIModels({ d }: { d: Dashboard }) {
  const t = d.tree, f = d.forecast
  const test = d.items.filter((i) => i.LR_Split === "test").map((i) => ({ actual: i.Annual_Usage, pred: i.Predicted_Demand, item: i.Item }))
  const imp = t.importances.map((x) => ({ name: FEAT[x.feature] ?? x.feature, v: x.importance }))
  const rows = ["A", "B", "C"].map((l) => ({ l, ...t.report[l] }))
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard label="Test accuracy" value={`${(t.acc_test * 100).toFixed(1)}%`} sub={<>train <span className="num">{(t.acc_train * 100).toFixed(1)}%</span> · mild overfit</>} accent={COLORS.A} />
        <KpiCard label="Split" value={`${t.train_n}/${t.test_n}`} sub="stratified 70 / 30 · seed 42" />
        <KpiCard label="Tree depth · leaves" value={`${t.depth} · ${t.leaves}`} sub="depth chosen by 5-fold CV" />
        <KpiCard label="Forecast R² (test)" value={f.r2_test.toFixed(3)} sub={<>MAE <span className="num">{f.mae_test.toFixed(1)}</span> · RMSE <span className="num">{f.rmse_test.toFixed(1)}</span></>} accent={COLORS.C} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Decision tree – confusion matrix" desc="Test set (150 items). Rows are the true class, columns the predicted class. Every mistake is between neighbouring classes.">
          <ConfusionMatrix cm={t.confusion} title="Decision tree, test set" />
        </Panel>
        <Panel title="Feature importances" desc="Share of the impurity reduction each feature explains. Lead time barely matters because ABC depends on usage × cost.">
          <div className="h-60" role="img" aria-label="Feature importances bar chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={imp} layout="vertical" margin={{ left: 8, right: 36, top: 4, bottom: 4 }}>
                <CartesianGrid stroke="var(--grid)" horizontal={false} />
                <XAxis type="number" domain={[0, 0.6]} ticks={[0, 0.2, 0.4, 0.6]} tickLine={false} axisLine={false} tickFormatter={(v) => v.toFixed(1)} />
                <YAxis type="category" dataKey="name" tickLine={false} axisLine={false} width={92} />
                <Tooltip cursor={{ fill: "var(--muted)" }} content={<ChartTip valFmt={(v: number) => v.toFixed(3)} />} />
                <Bar isAnimationActive={false} dataKey="v" name="Importance" radius={[0, 6, 6, 0]} label={{ position: "right", fill: "var(--foreground)", fontSize: 11, formatter: (v: any) => Number(v).toFixed(2) }}>
                  {imp.map((_, i) => <Cell key={i} fill={i === 0 ? "var(--primary)" : "color-mix(in srgb, var(--primary) 55%, var(--card))"} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Classification report (test)" desc="Precision, recall and F1 per class.">
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/60 text-left text-xs uppercase tracking-wide text-muted-foreground"><tr><th className="px-3 py-2">Class</th><th className="px-3 py-2 text-right">Precision</th><th className="px-3 py-2 text-right">Recall</th><th className="px-3 py-2 text-right">F1</th><th className="px-3 py-2 text-right">Support</th></tr></thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.l} className="border-t"><td className="px-3 py-2 font-semibold" style={{ color: (COLORS as any)[r.l] }}>Class {r.l}</td>
                    <td className="num px-3 py-2 text-right">{r.precision.toFixed(3)}</td><td className="num px-3 py-2 text-right">{r.recall.toFixed(3)}</td>
                    <td className="num px-3 py-2 text-right">{r["f1-score"].toFixed(3)}</td><td className="num px-3 py-2 text-right">{r.support}</td></tr>))}
                <tr className="border-t bg-muted/40 font-semibold"><td className="px-3 py-2">Macro avg</td><td className="num px-3 py-2 text-right">{t.report["macro avg"].precision.toFixed(3)}</td>
                  <td className="num px-3 py-2 text-right">{t.report["macro avg"].recall.toFixed(3)}</td><td className="num px-3 py-2 text-right">{t.report["macro avg"]["f1-score"].toFixed(3)}</td><td className="num px-3 py-2 text-right">{t.test_n}</td></tr>
              </tbody>
            </table>
          </div>
        </Panel>
        <Panel title="Choosing the tree depth" desc="5-fold cross-validation accuracy on the training set only; the test set is never used for tuning.">
          <div className="h-52" role="img" aria-label="Cross-validated accuracy by tree depth">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={t.depth_cv} margin={{ left: 0, right: 16, top: 8, bottom: 4 }}>
                <CartesianGrid stroke="var(--grid)" vertical={false} />
                <XAxis dataKey="max_depth" tickLine={false} label={{ value: "max_depth", position: "insideBottom", offset: -2, fill: "var(--axis)", fontSize: 11 }} height={36} />
                <YAxis domain={[0.6, 0.95]} tickLine={false} axisLine={false} tickFormatter={(v) => v.toFixed(2)} width={40} />
                <Tooltip content={<ChartTip labelFmt={(l: number) => `Depth ${l}`} valFmt={(v: number) => v.toFixed(3)} />} />
                <ReferenceLine x={t.depth} stroke="var(--primary)" strokeDasharray="4 4" />
                <Line isAnimationActive={false} dataKey="CV_accuracy" name="CV accuracy" stroke="var(--primary)" strokeWidth={2.5} dot={{ r: 4, fill: "var(--card)", strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel title="Demand forecast – actual vs predicted" desc={`Linear regression Annual_Usage = ${f.intercept.toFixed(2)} + ${f.coef.toFixed(4)} × Past_Demand, evaluated on ${d.metrics.lr_test_n} unseen items. Points on the dashed line are perfect forecasts.`}>
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="h-80 lg:col-span-2" role="img" aria-label="Scatter plot of actual versus predicted demand">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 8, right: 16, left: 0, bottom: 20 }}>
                <CartesianGrid stroke="var(--grid)" />
                <XAxis type="number" dataKey="actual" name="Actual" tickLine={false} tickFormatter={(v) => fmt(v)} label={{ value: "Actual annual demand (units)", position: "insideBottom", offset: -12, fill: "var(--axis)", fontSize: 11 }} />
                <YAxis type="number" dataKey="pred" name="Predicted" tickLine={false} axisLine={false} tickFormatter={(v) => fmt(v)} width={52} label={{ value: "Predicted (units)", angle: -90, position: "insideLeft", fill: "var(--axis)", fontSize: 11 }} />
                <Tooltip cursor={{ strokeDasharray: "3 3" }} content={<ChartTip valFmt={(v: number) => fmt(v)} />} />
                <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 5600, y: 5600 }]} stroke="var(--foreground)" strokeDasharray="5 5" />
                <Scatter data={test} name="Item" fill="var(--primary)" fillOpacity={0.7} isAnimationActive={false} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <dl className="grid grid-cols-2 content-start gap-3 text-sm">
            {[["R² (test)", f.r2_test.toFixed(4)], ["R² (train)", f.r2_train.toFixed(4)], ["MAE (test)", `${f.mae_test.toFixed(2)} units`], ["RMSE (test)", `${f.rmse_test.toFixed(2)} units`], ["Slope", f.coef.toFixed(4)], ["Intercept", f.intercept.toFixed(3)]].map(([k, v]) => (
              <div key={k} className="rounded-lg bg-muted/50 p-3"><dt className="text-xs text-muted-foreground">{k}</dt><dd className="num mt-1 text-lg font-semibold">{v}</dd></div>))}
          </dl>
        </div>
      </Panel>
      <DataNote>R² is high partly because the synthetic usage was generated as a noisy copy of past demand; real data with trend and seasonality would fit less well.</DataNote>
    </div>
  )
}
