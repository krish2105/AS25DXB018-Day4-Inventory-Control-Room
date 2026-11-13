"use client"
import { useMemo, useState } from "react"
import { CartesianGrid, Legend, Line, LineChart, ReferenceDot, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { RotateCcw } from "lucide-react"
import type { Dashboard } from "@/lib/data"
import { ProductParams, fmt, normPpf, productCurve, recommendLevel } from "@/lib/stats"
import { ChartTip, COLORS, Panel, Range } from "./ui"

const PRODUCTS = ["A", "B", "C"] as const
type P = (typeof PRODUCTS)[number]

export function Simulator({ d }: { d: Dashboard }) {
  const levels = d.partB.service_levels
  const defaults = useMemo(() => {
    const o = {} as Record<P, ProductParams>
    d.partB.parameters.forEach((p) => { o[p.Product as P] = { mean: p.Avg_Demand, cvPct: (p.Demand_Std / p.Avg_Demand) * 100, lead: p.Lead_Time, h: p.Holding_Cost } })
    return o
  }, [d])
  const [params, setParams] = useState<Record<P, ProductParams>>(defaults)
  const [slPct, setSlPct] = useState(95)
  const [tol, setTol] = useState(d.partB.recommendation.tolerance)
  const set = (p: P, k: keyof ProductParams, v: number) => setParams((s) => ({ ...s, [p]: { ...s[p], [k]: v } }))
  const isDefault = PRODUCTS.every((p) => (Object.keys(defaults[p]) as (keyof ProductParams)[]).every((k) => Math.abs(defaults[p][k] - params[p][k]) < 1e-9))

  const curves = useMemo(() => Object.fromEntries(PRODUCTS.map((p) => [p, productCurve(params[p], levels)])) as Record<P, ReturnType<typeof productCurve>>, [params, levels])
  const ymax = Math.max(...PRODUCTS.flatMap((p) => curves[p].map((c) => Math.max(c.ss, c.hc))))
  const at = (p: P, s: number) => curves[p].find((c) => Math.abs(c.sl - s) < 1e-9)!
  const sl = slPct / 100

  // match against the notebook at default parameters
  const maxDiff = useMemo(() => {
    let m = 0
    d.partB.curves.forEach((r) => {
      const c = productCurve(defaults[r.Product as P], [r.Service_Level])[0]
      m = Math.max(m, Math.abs(c.ss - r.Safety_Stock), Math.abs(c.hc - r.Holding_Cost))
    })
    return m
  }, [d, defaults])

  const rec = Object.fromEntries(PRODUCTS.map((p) => [p, recommendLevel(curves[p], tol)])) as Record<P, number>
  const policy = (lv: Record<P, number>) => PRODUCTS.reduce((a, p) => ({ ss: a.ss + at(p, lv[p]).ss, hc: a.hc + at(p, lv[p]).hc }), { ss: 0, hc: 0 })
  const pol = { u95: policy({ A: 0.95, B: 0.95, C: 0.95 }), rec: policy(rec), u99: policy({ A: 0.99, B: 0.99, C: 0.99 }) }
  const prodColor: Record<P, string> = { A: "var(--abc-a)", B: "var(--abc-b)", C: "var(--abc-c)" }

  return (
    <div className="space-y-6">
      <Panel title="What-if parameters" desc="Change any product’s demand, variability, lead time or holding cost. Everything below recalculates instantly with Safety stock = Z × σ × √Lead time and Holding cost = Safety stock × cost per unit."
        right={<button onClick={() => { setParams(defaults); setSlPct(95); setTol(d.partB.recommendation.tolerance) }} className="inline-flex h-10 items-center gap-2 rounded-lg border px-3 text-sm font-medium hover:bg-muted focus-visible:outline-2 focus-visible:outline-ring"><RotateCcw className="h-4 w-4" aria-hidden />Reset to notebook values</button>}>
        <div className="grid gap-4 lg:grid-cols-3">
          {PRODUCTS.map((p) => (
            <fieldset key={p} className="min-w-0 rounded-xl border bg-muted/30 p-4">
              <legend className="flex items-center gap-2 px-2 text-sm font-semibold"><span className="h-3 w-3 rounded-full" style={{ background: prodColor[p] }} aria-hidden />Product {p}</legend>
              <div className="space-y-4">
                <Range label="Mean demand (units / period)" value={params[p].mean} min={50} max={800} step={5} onChange={(v) => set(p, "mean", v)} />
                <Range label="Demand variability (CV)" value={params[p].cvPct} min={1} max={40} step={0.01} unit="%" display={params[p].cvPct.toFixed(1)} onChange={(v) => set(p, "cvPct", v)} />
                <Range label="Lead time (periods)" value={params[p].lead} min={1} max={12} step={1} onChange={(v) => set(p, "lead", v)} />
                <Range label="Holding cost (per unit / period)" value={params[p].h} min={0.5} max={5} step={0.05} display={params[p].h.toFixed(2)} onChange={(v) => set(p, "h", v)} />
                <p className="num text-xs text-muted-foreground">σ = {fmt((params[p].mean * params[p].cvPct) / 100, 1)} · σ√L = {fmt((params[p].mean * params[p].cvPct) / 100 * Math.sqrt(params[p].lead), 1)}</p>
              </div>
            </fieldset>))}
        </div>
        <div className="mt-5 grid gap-5 sm:grid-cols-2">
          <Range label="Service level (marker on the charts)" value={slPct} min={80} max={99} step={1} unit="%" onChange={setSlPct} />
          <Range label="Recommendation tolerance (extra holding cost allowed per +1 pp)" value={tol} min={2} max={60} step={1} onChange={setTol} />
        </div>
      </Panel>

      <Panel title="Service Level Trade-offs in Inventory Optimization" desc="Product A | B | C on one y-scale. Blue = safety stock (units), green = holding cost. The vertical line is the selected service level."
        right={<span className={`rounded-full px-3 py-1 text-xs font-semibold ${isDefault && maxDiff < 1e-4 ? "bg-primary/15 text-primary" : "bg-muted text-muted-foreground"}`} title="Maximum absolute difference from the notebook's B4 table at the default parameters">
          {isDefault ? (maxDiff < 1e-4 ? `✓ Matches notebook (max Δ ${maxDiff.toExponential(0)}, JSON rounding)` : `Δ vs notebook ${maxDiff.toFixed(6)}`) : "Custom parameters"}</span>}>
        <div className="grid gap-4 lg:grid-cols-3">
          {PRODUCTS.map((p, idx) => {
            const data = curves[p].map((c) => ({ sl: c.sl, ss: c.ss, hc: c.hc }))
            const cur = at(p, sl)
            return (
              <figure key={p} className="rounded-xl border bg-card p-3" aria-label={`Product ${p} trade-off curves`}>
                <figcaption className="mb-1 flex items-baseline justify-between px-1"><span className="text-sm font-semibold">Product {p}</span>
                  <span className="num text-xs text-muted-foreground">at {slPct}%: SS {fmt(cur.ss, 1)} · HC {fmt(cur.hc, 1)}</span></figcaption>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data} margin={{ top: 8, right: 12, left: idx === 0 ? 0 : -8, bottom: 4 }}>
                      <CartesianGrid stroke="var(--grid)" />
                      <XAxis dataKey="sl" type="number" domain={[0.795, 0.995]} ticks={[0.8, 0.85, 0.9, 0.95, 0.99]} tickFormatter={(v) => `${Math.round(v * 100)}%`} tickLine={false} height={34} label={{ value: "Service Level", position: "insideBottom", offset: -2, fill: "var(--axis)", fontSize: 11 }} />
                      <YAxis domain={[0, Math.ceil((ymax * 1.08) / 50) * 50]} tickLine={false} axisLine={false} width={40} label={idx === 0 ? { value: "Units / Cost", angle: -90, position: "insideLeft", fill: "var(--axis)", fontSize: 11 } : undefined} />
                      <Tooltip content={<ChartTip labelFmt={(l: number) => `Service level ${(l * 100).toFixed(0)}% (Z = ${normPpf(l).toFixed(3)})`} valFmt={(v: number, n: string) => (n === "Safety Stock" ? `${v.toFixed(1)} units` : v.toFixed(1))} />} />
                      <Legend verticalAlign="top" height={26} iconType="plainline" wrapperStyle={{ fontSize: 12 }} />
                      <ReferenceLine x={sl} stroke="var(--foreground)" strokeDasharray="4 4" strokeOpacity={0.5} />
                      <Line dataKey="ss" name="Safety Stock" stroke={COLORS.ss} strokeWidth={2.5} dot={false} isAnimationActive={false} />
                      <Line dataKey="hc" name="Holding Cost" stroke={COLORS.hc} strokeWidth={2.5} dot={false} isAnimationActive={false} />
                      <ReferenceDot x={sl} y={cur.ss} r={5} fill={COLORS.ss} stroke="var(--card)" strokeWidth={2} />
                      <ReferenceDot x={sl} y={cur.hc} r={5} fill={COLORS.hc} stroke="var(--card)" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </figure>)
          })}
        </div>
        <p className="mt-3 text-sm text-muted-foreground">Both curves bend upward: safety stock grows with Z, and Z grows faster the closer the service level gets to 100%. Products differ because σ√L and the holding cost per unit differ.</p>
      </Panel>

      <div className="grid gap-6 xl:grid-cols-2">
        <Panel title="Comparison at 80 / 90 / 95 / 99%" desc="Safety stock (SS, units) and holding cost (HC) with the increase from 95% to 99%.">
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full min-w-[620px] text-sm">
              <thead className="bg-muted/60 text-xs uppercase tracking-wide text-muted-foreground"><tr>
                <th className="px-3 py-2 text-left">Product</th>{[80, 90, 95, 99].map((s) => <th key={s} className="px-2 py-2 text-right">SS {s}%</th>)}
                {[80, 90, 95, 99].map((s) => <th key={s} className="px-2 py-2 text-right">HC {s}%</th>)}<th className="px-3 py-2 text-right">95→99%</th></tr></thead>
              <tbody>
                {PRODUCTS.map((p) => (<tr key={p} className="border-t"><td className="px-3 py-2 font-semibold" style={{ color: prodColor[p] }}>{p}</td>
                  {[0.8, 0.9, 0.95, 0.99].map((s) => <td key={s} className="num px-2 py-2 text-right">{fmt(at(p, s).ss, 1)}</td>)}
                  {[0.8, 0.9, 0.95, 0.99].map((s) => <td key={s} className="num px-2 py-2 text-right">{fmt(at(p, s).hc, 1)}</td>)}
                  <td className="num px-3 py-2 text-right font-semibold text-primary">+{((at(p, 0.99).ss / at(p, 0.95).ss - 1) * 100).toFixed(1)}%</td></tr>))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">The relative increase is the same for every product (Z(99%)/Z(95%) − 1) – only the absolute amounts differ.</p>
        </Panel>

        <Panel title="Portfolio policies" desc="Total safety stock and holding cost for the three products.">
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/60 text-xs uppercase tracking-wide text-muted-foreground"><tr><th className="px-3 py-2 text-left">Policy</th><th className="px-3 py-2 text-right">Safety stock</th><th className="px-3 py-2 text-right">Holding cost / period</th></tr></thead>
              <tbody>
                {[["Uniform 95%", pol.u95], [`Recommended (${PRODUCTS.map((p) => `${Math.round(rec[p] * 100)}`).join(" / ")}%)`, pol.rec], ["Uniform 99%", pol.u99]].map(([n, v]: any, i) => (
                  <tr key={n} className={`border-t ${i === 1 ? "bg-primary/10 font-semibold" : ""}`}><td className="px-3 py-2">{n}</td><td className="num px-3 py-2 text-right">{fmt(v.ss, 1)}</td><td className="num px-3 py-2 text-right">{fmt(v.hc, 1)}</td></tr>))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">Recommended is {((1 - pol.rec.hc / pol.u99.hc) * 100).toFixed(0)}% cheaper than a uniform 99% policy and {fmt(pol.rec.hc - pol.u95.hc, 1)} dearer than uniform 95%.</p>
        </Panel>
      </div>

      <Panel title="Recommended service level per product" desc={`Rule: raise the service level while the next +1 percentage point costs at most ${tol} holding-cost units. Change the tolerance above to see how the advice moves.`}>
        <div className="grid gap-4 md:grid-cols-3">
          {PRODUCTS.map((p) => {
            const r = at(p, rec[p]), extra = at(p, 0.99).hc - r.hc
            const note = p === "B" ? "Volatile and long lead time – every point is costly. Cut variability rather than add buffer." : p === "A" ? "Stable, high volume: protect it while the price per point stays low." : "Small buffer, so high service is cheap in absolute terms."
            return (
              <div key={p} className="card-surface relative overflow-hidden p-5">
                <span aria-hidden className="absolute inset-y-0 left-0 w-1" style={{ background: prodColor[p] }} />
                <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Product {p}</p>
                <p className="num mt-2 text-4xl font-semibold text-primary">{Math.round(rec[p] * 100)}%</p>
                <dl className="mt-3 grid grid-cols-3 gap-2 text-xs">
                  <div><dt className="text-muted-foreground">Safety stock</dt><dd className="num text-sm font-semibold">{fmt(r.ss, 1)}</dd></div>
                  <div><dt className="text-muted-foreground">Holding cost</dt><dd className="num text-sm font-semibold">{fmt(r.hc, 1)}</dd></div>
                  <div><dt className="text-muted-foreground">+ to reach 99%</dt><dd className="num text-sm font-semibold">{fmt(extra, 1)}</dd></div>
                </dl>
                <p className="mt-3 text-sm text-muted-foreground">{note}</p>
              </div>)
          })}
        </div>
      </Panel>
    </div>
  )
}
