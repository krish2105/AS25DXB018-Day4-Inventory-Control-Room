"use client"
import { useMemo } from "react"
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ReferenceDot, ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, LabelList } from "recharts"
import type { Dashboard } from "@/lib/data"
import { fmt } from "@/lib/stats"
import { ChartTip, COLORS, DataNote, Panel, Verdict } from "./ui"
import { ConfusionMatrix } from "./confusion"

const AXIS = { tickLine: false as const }

export function BeforeAfter({ d }: { d: Dashboard }) {
  const ba = d.before_after, m = d.metrics
  const cls = ba.classification, fc = ba.forecast
  const metricBars = [
    { name: "Accuracy", before: cls.before.accuracy, after: cls.after.accuracy },
    { name: "Macro-F1", before: cls.before.macro_f1, after: cls.after.macro_f1 },
    { name: "Class-A recall", before: cls.before.recall_A, after: cls.after.recall_A },
  ]
  const fcBars = [
    { name: "MAE", before: fc.before["MAE"], after: fc.after["MAE"] },
    { name: "RMSE", before: fc.before["RMSE"], after: fc.after["RMSE"] },
    { name: "|Bias|", before: Math.abs(fc.before["Bias"]), after: Math.abs(fc.after["Bias"]) },
  ]
  const hist = useMemo(() => {
    const bins = Array.from({ length: 20 }, (_, k) => ({ lo: 0.8 + k / 100, label: `${80 + k}%`, before: 0, after: 0 }))
    d.items.forEach((i) => {
      const b = Math.min(19, Math.max(0, Math.floor((i.CSL_Before - 0.8) * 100 + 1e-9))); if (i.CSL_Before >= 0.8) bins[b].before++
      const a = Math.min(19, Math.max(0, Math.floor((i.CSL_After - 0.8) * 100 + 1e-9))); if (i.CSL_After >= 0.8) bins[a].after++
    })
    return bins
  }, [d.items])
  const ss = ba.safety_stock.summary
  const L = (k: string) => ss[k]
  const bTot = d.partB.before_after_totals
  const rec = d.partB.recommendation.levels
  const curveOf = (p: string) => d.partB.curves.filter((c) => c.Product === p)
  const hcAt = (p: string, s: number) => d.partB.curves.find((c) => c.Product === p && Math.abs(c.Service_Level - s) < 1e-9)!.Holding_Cost
  const ymax = Math.max(...d.partB.curves.map((c) => Math.max(c.Safety_Stock, c.Holding_Cost)))
  const portfolio = [
    { name: "Safety stock", before: bTot[0].Total_Safety_Stock, after: bTot[1].Total_Safety_Stock, ref: bTot[2].Total_Safety_Stock },
    { name: "Holding cost", before: bTot[0].Total_Holding_Cost, after: bTot[1].Total_Holding_Cost, ref: bTot[2].Total_Holding_Cost },
    { name: "Units short / cycle", before: bTot[0].Total_Units_Short_per_Cycle, after: bTot[1].Total_Units_Short_per_Cycle, ref: bTot[2].Total_Units_Short_per_Cycle },
  ]
  const pt = (k: string) => `${(m[k] * 100).toFixed(1)}%`

  const scorecard: { area: string; metric: string; before: string; after: string; v: "clear" | "marginal" | "tradeoff" }[] = [
    { area: "Classification", metric: "Accuracy (150 test items)", before: pt("ba_cls_acc_before"), after: pt("ba_cls_acc_after"), v: "clear" },
    { area: "Classification", metric: "Class-A items flagged", before: `${m.ba_cls_a_total - m.ba_cls_a_missed_before} of ${m.ba_cls_a_total}`, after: `${m.ba_cls_a_total - m.ba_cls_a_missed_after} of ${m.ba_cls_a_total}`, v: "clear" },
    { area: "Forecast", metric: "MAE (units)", before: m.ba_fc_mae_before.toFixed(1), after: m.ba_fc_mae_after.toFixed(1), v: "marginal" },
    { area: "Forecast", metric: "Bias (units)", before: `+${m.ba_fc_bias_before.toFixed(1)}`, after: `+${m.ba_fc_bias_after.toFixed(1)}`, v: "marginal" },
    { area: "Safety stock", metric: "Items below 90% service (same budget)", before: `${m.ba_ss_below90_before}`, after: `${m.ba_ss_below90_after}`, v: "clear" },
    { area: "Safety stock", metric: "Lowest item service level", before: pt("ba_ss_csl_min_before"), after: pt("ba_ss_csl_min_after"), v: "clear" },
    { area: "Service levels (Part B)", metric: "Holding cost per period", before: m.ba_B_b95_hc.toFixed(1), after: m.ba_B_after_hc.toFixed(1), v: "tradeoff" },
    { area: "Service levels (Part B)", metric: "Expected units short per cycle", before: m.ba_B_b95_short.toFixed(2), after: m.ba_B_after_short.toFixed(2), v: "tradeoff" },
  ]

  return (
    <div className="space-y-6">
      <Panel title="Before AI vs after AI – scorecard" desc="Before = the traditional way of working; after = the models built in this lab. Same items, same data. The verdict column is honest: not every comparison is a big win.">
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full min-w-[680px] text-sm">
            <thead className="bg-muted/60 text-left text-xs uppercase tracking-wide text-muted-foreground"><tr><th className="px-3 py-2">Area</th><th className="px-3 py-2">Metric</th><th className="px-3 py-2 text-right">Before AI</th><th className="px-3 py-2 text-right">After AI</th><th className="px-3 py-2 text-right">Verdict</th></tr></thead>
            <tbody>
              {scorecard.map((r, i) => (<tr key={i} className="border-t"><td className="px-3 py-2 text-muted-foreground">{r.area}</td><td className="px-3 py-2">{r.metric}</td>
                <td className="num px-3 py-2 text-right" style={{ color: "var(--before)" }}>{r.before}</td><td className="num px-3 py-2 text-right font-semibold text-primary">{r.after}</td>
                <td className="px-3 py-2 text-right"><Verdict kind={r.v} /></td></tr>))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel title="1 · Classification" desc="Before: rank items by annual usage only (top 20% = A, next 30% = B, rest = C), ignoring unit cost. After: decision tree on usage, cost, lead time and past demand. Both are scored against the value-based ABC class.">
        <div className="grid gap-6 lg:grid-cols-3">
          <ConfusionMatrix cm={cls.before.confusion} hue="var(--before)" title="Before AI – usage-only rule" />
          <ConfusionMatrix cm={cls.after.confusion} hue="var(--after)" title="After AI – decision tree" />
          <div className="h-64" role="img" aria-label="Classification quality before and after AI">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metricBars} margin={{ top: 20, right: 8, left: -12, bottom: 0 }}>
                <CartesianGrid stroke="var(--grid)" vertical={false} /><XAxis dataKey="name" {...AXIS} fontSize={11} /><YAxis domain={[0, 1]} {...AXIS} axisLine={false} />
                <Tooltip cursor={{ fill: "var(--muted)" }} content={<ChartTip valFmt={(v: number) => v.toFixed(3)} />} />
                <Legend wrapperStyle={{ fontSize: 12 }} iconType="square" />
                <Bar isAnimationActive={false} dataKey="before" name="Before AI" fill={COLORS.before} radius={[4, 4, 0, 0]}><LabelList dataKey="before" position="top" formatter={(v: any) => Number(v).toFixed(2)} fontSize={10} fill="var(--foreground)" /></Bar>
                <Bar isAnimationActive={false} dataKey="after" name="After AI" fill={COLORS.after} radius={[4, 4, 0, 0]}><LabelList dataKey="after" position="top" formatter={(v: any) => Number(v).toFixed(2)} fontSize={10} fill="var(--foreground)" /></Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <p className="mt-4 text-sm text-muted-foreground">The usage-only rule misses {m.ba_cls_a_missed_before} of {m.ba_cls_a_total} class-A items; the tree misses {m.ba_cls_a_missed_after}. The exact value-based ABC is perfect by definition but must be recomputed for the whole catalogue; the tree labels new items instantly.</p>
      </Panel>

      <Panel title="2 · Demand forecast" desc="Before: next year = last year (naive). After: linear regression. Same 150 test items; dashed line = perfect forecast.">
        <div className="grid gap-6 lg:grid-cols-3">
          {([["Before AI – naive (last year)", "before", COLORS.before], ["After AI – linear regression", "after", COLORS.after]] as const).map(([t, k, c]) => (
            <figure key={k} aria-label={t}>
              <figcaption className="mb-1 text-sm font-semibold">{t}</figcaption>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 8, right: 12, left: 0, bottom: 18 }}>
                    <CartesianGrid stroke="var(--grid)" />
                    <XAxis type="number" dataKey="actual" name="Actual" domain={[0, 5600]} tickFormatter={(v) => fmt(v)} {...AXIS} label={{ value: "Actual (units)", position: "insideBottom", offset: -10, fill: "var(--axis)", fontSize: 11 }} />
                    <YAxis type="number" dataKey={k} name="Forecast" domain={[0, 5600]} tickFormatter={(v) => fmt(v)} {...AXIS} axisLine={false} width={46} />
                    <Tooltip cursor={{ strokeDasharray: "3 3" }} content={<ChartTip valFmt={(v: number) => fmt(v)} />} />
                    <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 5600, y: 5600 }]} stroke="var(--foreground)" strokeDasharray="5 5" />
                    <Scatter data={fc.points} fill={c} fillOpacity={0.65} isAnimationActive={false} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </figure>))}
          <div className="h-[19rem]" role="img" aria-label="Forecast error before and after AI">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fcBars} margin={{ top: 28, right: 8, left: -8, bottom: 0 }}>
                <CartesianGrid stroke="var(--grid)" vertical={false} /><XAxis dataKey="name" {...AXIS} /><YAxis {...AXIS} axisLine={false} />
                <Tooltip cursor={{ fill: "var(--muted)" }} content={<ChartTip valFmt={(v: number) => `${v.toFixed(1)} units`} />} />
                <Legend wrapperStyle={{ fontSize: 12 }} iconType="square" />
                <Bar isAnimationActive={false} dataKey="before" name="Before AI" fill={COLORS.before} radius={[4, 4, 0, 0]}><LabelList dataKey="before" position="top" formatter={(v: any) => Number(v).toFixed(1)} fontSize={10} fill="var(--foreground)" /></Bar>
                <Bar isAnimationActive={false} dataKey="after" name="After AI" fill={COLORS.after} radius={[4, 4, 0, 0]}><LabelList dataKey="after" position="top" formatter={(v: any) => Number(v).toFixed(1)} fontSize={10} fill="var(--foreground)" /></Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <p className="mt-4 text-sm text-muted-foreground">Honest result: MAE falls only {(100 * (1 - m.ba_fc_mae_after / m.ba_fc_mae_before)).toFixed(1)}% and MAPE is slightly worse ({m.ba_fc_mape_before.toFixed(2)}% → {m.ba_fc_mape_after.toFixed(2)}%). The regression mainly removes the systematic under-forecast (bias {m.ba_fc_bias_before.toFixed(1)} → {m.ba_fc_bias_after.toFixed(1)} units). Last year’s demand is already an excellent predictor in this synthetic data.</p>
      </Panel>

      <Panel title="3 · Safety stock at the same budget" desc={`Before: one flat rule – buffer = ${ba.safety_stock.flat_pct.toFixed(1)}% of last year’s demand for every item, lead time ignored. After: Z × σ × √LT. Both hold exactly ${fmt(L("Total buffer (units)").after)} units; the chart shows the service level each item actually gets.`}>
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="h-72 lg:col-span-2" role="img" aria-label="Histogram of achieved service level per item before and after AI">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hist} margin={{ top: 8, right: 8, left: 0, bottom: 20 }} barGap={0} barCategoryGap="12%">
                <CartesianGrid stroke="var(--grid)" vertical={false} />
                <XAxis dataKey="label" {...AXIS} interval={1} fontSize={10} label={{ value: "Achieved service level of an item", position: "insideBottom", offset: -12, fill: "var(--axis)", fontSize: 11 }} />
                <YAxis {...AXIS} axisLine={false} width={40} label={{ value: "Items", angle: -90, position: "insideLeft", fill: "var(--axis)", fontSize: 11 }} />
                <Tooltip cursor={{ fill: "var(--muted)" }} content={<ChartTip labelFmt={(l: string) => `Service level ${l}`} valFmt={(v: number) => `${v} items`} />} />
                <Legend verticalAlign="top" height={26} wrapperStyle={{ fontSize: 12 }} iconType="square" />
                <Bar isAnimationActive={false} dataKey="before" name="Before AI (flat rule)" fill={COLORS.before} /><Bar isAnimationActive={false} dataKey="after" name="After AI (Z·σ·√LT)" fill={COLORS.after} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="overflow-x-auto rounded-lg border self-start">
            <table className="w-full text-sm">
              <thead className="bg-muted/60 text-xs uppercase tracking-wide text-muted-foreground"><tr><th className="px-3 py-2 text-left">Metric</th><th className="px-3 py-2 text-right">Before</th><th className="px-3 py-2 text-right">After</th></tr></thead>
              <tbody>
                {[["Mean service level", pt("ba_ss_csl_mean_before"), pt("ba_ss_csl_mean_after")], ["Lowest item", pt("ba_ss_csl_min_before"), pt("ba_ss_csl_min_after")],
                  ["Items < 90%", `${m.ba_ss_below90_before}`, `${m.ba_ss_below90_after}`], ["Spread (sd, pp)", m.ba_ss_csl_sd_before.toFixed(2), m.ba_ss_csl_sd_after.toFixed(2)],
                  ["Buffer units", fmt(m.ba_ss_units_before), fmt(m.ba_ss_units_after)]].map(([a, b, c]) => (
                  <tr key={a} className="border-t"><td className="px-3 py-2">{a}</td><td className="num px-3 py-2 text-right" style={{ color: "var(--before)" }}>{b}</td><td className="num px-3 py-2 text-right font-semibold text-primary">{c}</td></tr>))}
              </tbody>
            </table>
          </div>
        </div>
        <p className="mt-4 text-sm text-muted-foreground">With the same inventory the AI rule moves units from short-lead-time items to long-lead-time, high-risk ones. Both rules are judged with the same assumed σ model, so this shows consistency of protection, not measured stock-outs.</p>
      </Panel>

      <Panel title="4 · Part B – one service level for everyone vs a differentiated policy" desc="Before: uniform 95% for all products. After: 97% / 95% / 98% for A / B / C, chosen from the simulated cost curves. Grey square = before, green dot = after.">
        <div className="grid gap-4 lg:grid-cols-3">
          {["A", "B", "C"].map((p, idx) => (
            <figure key={p} className="rounded-xl border p-3" aria-label={`Product ${p} before and after`}>
              <figcaption className="px-1 text-sm font-semibold">Product {p}: <span style={{ color: "var(--before)" }}>95%</span> → <span className="text-primary">{Math.round(rec[p] * 100)}%</span></figcaption>
              <div className="h-60">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={curveOf(p).map((c) => ({ sl: c.Service_Level, ss: c.Safety_Stock, hc: c.Holding_Cost }))} margin={{ top: 8, right: 10, left: idx === 0 ? 0 : -10, bottom: 4 }}>
                    <CartesianGrid stroke="var(--grid)" />
                    <XAxis dataKey="sl" type="number" domain={[0.795, 0.995]} ticks={[0.8, 0.85, 0.9, 0.95, 0.99]} tickFormatter={(v) => `${Math.round(v * 100)}%`} {...AXIS} />
                    <YAxis domain={[0, Math.ceil((ymax * 1.08) / 50) * 50]} {...AXIS} axisLine={false} width={38} />
                    <Tooltip content={<ChartTip labelFmt={(l: number) => `Service level ${(l * 100).toFixed(0)}%`} valFmt={(v: number) => v.toFixed(1)} />} />
                    <Line dataKey="ss" name="Safety Stock" stroke={COLORS.ss} strokeWidth={2} dot={false} isAnimationActive={false} />
                    <Line dataKey="hc" name="Holding Cost" stroke={COLORS.hc} strokeWidth={2} dot={false} isAnimationActive={false} />
                    <ReferenceDot x={0.95} y={hcAt(p, 0.95)} r={7} shape={(pr: any) => <rect x={pr.cx - 7} y={pr.cy - 7} width={14} height={14} rx={2} fill={COLORS.before} stroke="var(--card)" strokeWidth={2} />} />
                    <ReferenceDot x={rec[p]} y={hcAt(p, rec[p])} r={7} fill={COLORS.after} stroke="var(--card)" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </figure>))}
        </div>
        <div className="mt-5 grid gap-6 lg:grid-cols-3">
          {portfolio.map((p) => {
            const data = [{ n: "Uniform 95% (before)", v: p.before, c: COLORS.before }, { n: "Differentiated (after)", v: p.after, c: COLORS.after }, { n: "Uniform 99% (ref.)", v: p.ref, c: "var(--chart-3)" }]
            return (
              <figure key={p.name} aria-label={p.name}>
                <figcaption className="mb-1 text-sm font-semibold">{p.name}</figcaption>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} margin={{ top: 22, right: 8, left: -10, bottom: 0 }}>
                      <CartesianGrid stroke="var(--grid)" vertical={false} /><XAxis dataKey="n" {...AXIS} fontSize={10} interval={0} tickFormatter={(v: string) => v.split(" ")[0] + " " + (v.split(" ")[1] ?? "")} />
                      <YAxis {...AXIS} axisLine={false} width={40} />
                      <Tooltip cursor={{ fill: "var(--muted)" }} content={<ChartTip valFmt={(v: number) => v.toFixed(2)} />} />
                      <Bar isAnimationActive={false} dataKey="v" name={p.name} radius={[5, 5, 0, 0]}>
                        {data.map((e) => <Cell key={e.n} fill={e.c} />)}
                        <LabelList dataKey="v" position="top" formatter={(v: any) => Number(v).toFixed(p.name.startsWith("Units") ? 2 : 0)} fontSize={11} fill="var(--foreground)" />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </figure>)
          })}
        </div>
        <p className="mt-4 text-sm text-muted-foreground">Trade-off, not a free win: the differentiated policy costs {fmt(m.ba_B_after_hc - m.ba_B_b95_hc, 0)} more per period ({((m.ba_B_after_hc / m.ba_B_b95_hc - 1) * 100).toFixed(0)}%) and cuts expected shortage by {((1 - m.ba_B_after_short / m.ba_B_b95_short) * 100).toFixed(0)}%. Product B keeps {((m.ba_B_after_B_short / m.ba_B_after_short) * 100).toFixed(0)}% of the remaining shortage – reduce its variability instead of adding buffer.</p>
      </Panel>
      <DataNote>“After AI” for Part B means a data-driven, simulation-based policy built on assumed parameters and a 15-unit cost tolerance, not a model trained on real data.</DataNote>
    </div>
  )
}
