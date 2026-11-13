"use client"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import type { Dashboard } from "@/lib/data"
import { fmt } from "@/lib/stats"
import { COLORS, ChartTip, DataNote, Insight, KpiCard, Panel, Reveal } from "./ui"

export function Overview({ d }: { d: Dashboard }) {
  const m = d.metrics
  const hcRec = m.ba_B_after_hc
  const donut = d.abc_summary.map((s) => ({ name: `Class ${s.Category}`, value: s["Value_%"], items: s.Items, c: s.Category }))
  return (
    <div className="space-y-6">
      <Reveal>
        <div className="card-surface flex flex-col gap-3 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-primary">Retail chain · 500 SKUs</p>
            <h2 className="mt-1 max-w-2xl text-2xl font-semibold leading-snug sm:text-3xl">
              <span className="num text-primary">{m.abc_A_items}</span> items carry <span className="num text-primary">{fmt(m.abc_A_value_pct, 0)}%</span> of annual value.
            </h2>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
              Two models classify items and forecast demand, then size each buffer at a 95% service level. Part B shows what every extra point of service costs.
            </p>
          </div>
        </div>
      </Reveal>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Total items" value={fmt(m.n_items)} sub="synthetic SKUs, seed 42" delay={0.02} />
        <KpiCard label="Class A" value={fmt(m.abc_A_items)} sub={<><span className="num">{m.abc_A_items_pct.toFixed(1)}%</span> of items · <span className="num">{m.abc_A_value_pct.toFixed(1)}%</span> of value</>} accent={COLORS.A} delay={0.04} />
        <KpiCard label="Class B" value={fmt(m.abc_B_items)} sub={<><span className="num">{m.abc_B_items_pct.toFixed(1)}%</span> of items · <span className="num">{m.abc_B_value_pct.toFixed(1)}%</span> of value</>} accent={COLORS.B} delay={0.06} />
        <KpiCard label="Class C" value={fmt(m.abc_C_items)} sub={<><span className="num">{m.abc_C_items_pct.toFixed(1)}%</span> of items · <span className="num">{m.abc_C_value_pct.toFixed(1)}%</span> of value</>} accent={COLORS.C} delay={0.08} />
        <KpiCard label="Decision tree accuracy" value={`${(d.tree.acc_test * 100).toFixed(1)}%`} sub={<>test set, <span className="num">{d.tree.test_n}</span> items · macro-F1 <span className="num">{m.tree_macro_f1.toFixed(3)}</span></>} delay={0.1} />
        <KpiCard label="Forecast R²" value={d.forecast.r2_test.toFixed(3)} sub={<>MAE <span className="num">{d.forecast.mae_test.toFixed(1)}</span> · RMSE <span className="num">{d.forecast.rmse_test.toFixed(1)}</span> units</>} delay={0.12} />
        <KpiCard label="Total safety stock" value={fmt(d.safety_stock.total)} sub={<>units at 95% (Z = 1.65) · <span className="num">{m.ss_pct_demand.toFixed(1)}%</span> of demand</>} delay={0.14} />
        <KpiCard label="Total holding cost" value={fmt(hcRec, 1)} sub="per period, Part B policy A 97% · B 95% · C 98%" delay={0.16} />
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <Panel title="Value share by class" desc="Share of annual consumption value (usage × unit cost)." className="lg:col-span-2">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie isAnimationActive={false} data={donut} dataKey="value" nameKey="name" innerRadius="58%" outerRadius="88%" paddingAngle={2} stroke="var(--card)" strokeWidth={2}>
                  {donut.map((e) => <Cell key={e.c} fill={(COLORS as any)[e.c]} />)}
                </Pie>
                <Tooltip content={<ChartTip valFmt={(v: number) => `${v.toFixed(1)}% of value`} />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="mt-2 grid grid-cols-3 gap-2 text-center text-xs">
            {donut.map((e) => (
              <li key={e.c} className="rounded-lg bg-muted/60 py-2">
                <span className="mx-auto mb-1 block h-2 w-8 rounded-full" style={{ background: (COLORS as any)[e.c] }} />
                <span className="font-semibold">{e.name}</span>
                <span className="num block text-muted-foreground">{e.value.toFixed(1)}%</span>
              </li>
            ))}
          </ul>
        </Panel>

        <Panel title="What the numbers say" desc="Insights drawn from the executed notebook." className="lg:col-span-3">
          <ul className="space-y-2.5">
            <Insight tone="good"><b>Focus on class A.</b> {m.abc_A_items} items ({m.abc_A_items_pct.toFixed(0)}%) give {m.abc_A_value_pct.toFixed(0)}% of value; class C ({m.abc_C_items_pct.toFixed(0)}% of items) gives only {m.abc_C_value_pct.toFixed(0)}%.</Insight>
            <Insight><b>The tree makes only neighbour mistakes.</b> {(d.tree.acc_test * 100).toFixed(1)}% accuracy; no A item was called C and no C item A. Class B is the hardest (F1 {m.tree_f1_B.toFixed(2)}).</Insight>
            <Insight tone="warn"><b>Forecast gain is small.</b> Regression beats “same as last year” by only {m.mae_reduction_pct.toFixed(1)}% in MAE on this synthetic data; it mainly reduces bias.</Insight>
            <Insight><b>Buffers follow value.</b> Class A holds {m.ss_A_share.toFixed(0)}% of buffer units and {(m.ss_A_value / m.ss_total_value * 100).toFixed(0)}% of buffer value.</Insight>
            <Insight tone="warn"><b>Service is not free.</b> Going from 95% to 99% adds <span className="num">{m.B_inc_pct.toFixed(1)}%</span> to safety stock and holding cost for every product; the last point costs ≈ {m.marg_ratio.toFixed(1)}× the first.</Insight>
            <Insight tone="good"><b>Differentiate.</b> A 97% · B 95% · C 98% is {((1 - m.pol_Recommended_hc / m.pol_Uniform_99_hc) * 100).toFixed(0)}% cheaper than a uniform 99% policy.</Insight>
          </ul>
        </Panel>
      </div>
      <DataNote>{d.meta.note} Every number on this dashboard is read from the executed notebook’s export (<code>dashboard_data.json</code>).</DataNote>
    </div>
  )
}
