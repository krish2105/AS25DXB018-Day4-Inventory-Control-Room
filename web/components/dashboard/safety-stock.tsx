"use client"
import { useMemo, useState } from "react"
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import type { Dashboard } from "@/lib/data"
import { fmt, normPpf } from "@/lib/stats"
import { abcColor, COLORS, ChartTip, DataNote, KpiCard, Panel, Segmented } from "./ui"

export function SafetyStock({ d }: { d: Dashboard }) {
  const [sl, setSl] = useState(0.95)
  const z = sl === 0.95 ? d.safety_stock.z_95 : normPpf(sl)           // Part A uses Z = 1.65 at 95 %
  const calc = useMemo(() => d.items.map((i) => ({ ...i, ss: Math.round(z * i.Std_Dev * Math.sqrt(i.Lead_Time)) })), [d.items, z])
  const total = calc.reduce((s, i) => s + i.ss, 0)
  const value = calc.reduce((s, i) => s + i.ss * i.Unit_Cost, 0)
  const demand = calc.reduce((s, i) => s + i.Predicted_Demand, 0)
  const byClass = (["A", "B", "C"] as const).map((c) => {
    const r = calc.filter((i) => i.ABC_Category === c)
    const t = r.reduce((s, i) => s + i.ss, 0)
    const dm = r.reduce((s, i) => s + i.Predicted_Demand, 0)
    return { c, name: `Class ${c}`, items: r.length, total: t, avg: t / r.length, pctDemand: (t / dm) * 100, value: r.reduce((s, i) => s + i.ss * i.Unit_Cost, 0), lt: r.reduce((s, i) => s + i.Lead_Time, 0) / r.length }
  })
  const top = [...calc].sort((a, b) => b.ss - a.ss).slice(0, 25)
  const matches = sl === 0.95 && Math.abs(total - d.safety_stock.total) < 1
  const opts = [0.9, 0.95, 0.97, 0.99]

  return (
    <div className="space-y-6">
      <Panel title="Service level" desc="Safety stock = Z × σ × √Lead time, with σ = 10% of the predicted demand. The default is 95% with Z = 1.65, as on the slides."
        right={<div className="flex flex-wrap items-center gap-3">
          <Segmented label="Service level" value={sl} onChange={setSl} options={opts.map((v) => ({ value: v, label: `${v * 100}%` }))} />
          <label className="flex items-center gap-2 text-sm text-muted-foreground">Custom
            <select value={sl} onChange={(e) => setSl(parseFloat(e.target.value))} className="h-10 rounded-lg border bg-background px-2 text-sm text-foreground focus-visible:ring-2 focus-visible:ring-ring">
              {Array.from({ length: 20 }, (_, k) => 0.8 + k / 100).map((v) => <option key={v} value={Number(v.toFixed(2))}>{(v * 100).toFixed(0)}%</option>)}
            </select></label>
        </div>}>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <KpiCard label="Z-score" value={z.toFixed(sl === 0.95 ? 2 : 3)} sub={sl === 0.95 ? "slide value (norm.ppf gives 1.645)" : "scipy.stats.norm.ppf equivalent"} accent={COLORS.C} />
          <KpiCard label="Total safety stock" value={fmt(total)} sub={<><span className="num">{((total / demand) * 100).toFixed(1)}%</span> of predicted demand</>} accent={COLORS.A} />
          <KpiCard label="Buffer value" value={fmt(value)} sub="units × unit cost" />
          <KpiCard label="Class A share" value={`${((byClass[0].total / total) * 100).toFixed(1)}%`} sub="of buffer units" accent={COLORS.A} />
        </div>
        {matches && <p className="mt-3 text-xs font-medium text-primary">✓ Matches the notebook total ({fmt(d.safety_stock.total)} units).</p>}
      </Panel>

      <div className="grid gap-6 lg:grid-cols-3">
        <Panel title="By item – 25 largest buffers" desc="Bars are coloured by ABC class. These items are the first candidates for lead-time or variability reduction." className="lg:col-span-2">
          <div className="h-80" role="img" aria-label="Safety stock of the 25 items with the largest buffers">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={top} margin={{ top: 8, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid stroke="var(--grid)" vertical={false} />
                <XAxis dataKey="Item" tickLine={false} tickFormatter={(v: string) => v.replace("SKU_", "")} interval={0} angle={-90} textAnchor="end" height={44} fontSize={10} />
                <YAxis tickLine={false} axisLine={false} tickFormatter={(v) => fmt(v)} width={48} />
                <Tooltip cursor={{ fill: "var(--muted)" }} content={<ChartTip valFmt={(v: number) => `${fmt(v)} units`} />} />
                <Bar isAnimationActive={false} dataKey="ss" name="Safety stock" radius={[4, 4, 0, 0]}>{top.map((i) => <Cell key={i.Item} fill={abcColor(i.ABC_Category)} />)}</Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="By class" desc="Total safety stock per ABC class.">
          <div className="h-80" role="img" aria-label="Total safety stock by class">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byClass} margin={{ top: 24, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid stroke="var(--grid)" vertical={false} />
                <XAxis dataKey="name" tickLine={false} />
                <YAxis tickLine={false} axisLine={false} tickFormatter={(v) => fmt(v)} width={52} />
                <Tooltip cursor={{ fill: "var(--muted)" }} content={<ChartTip valFmt={(v: number) => `${fmt(v)} units`} />} />
                <Bar isAnimationActive={false} dataKey="total" name="Total safety stock" radius={[6, 6, 0, 0]} label={{ position: "top", fill: "var(--foreground)", fontSize: 11, formatter: (v: any) => fmt(Number(v)) }}>
                  {byClass.map((c) => <Cell key={c.c} fill={abcColor(c.c)} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel title="Summary table" desc="Computed live from the selected service level.">
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full min-w-[640px] text-sm">
            <thead className="bg-muted/60 text-left text-xs uppercase tracking-wide text-muted-foreground"><tr>
              <th className="px-3 py-2">Class</th><th className="px-3 py-2 text-right">Items</th><th className="px-3 py-2 text-right">Avg lead time</th><th className="px-3 py-2 text-right">Total safety stock</th>
              <th className="px-3 py-2 text-right">Avg per item</th><th className="px-3 py-2 text-right">% of demand</th><th className="px-3 py-2 text-right">Buffer value</th></tr></thead>
            <tbody>
              {byClass.map((c) => (<tr key={c.c} className="border-t"><td className="px-3 py-2 font-semibold" style={{ color: abcColor(c.c) }}>{c.name}</td>
                <td className="num px-3 py-2 text-right">{c.items}</td><td className="num px-3 py-2 text-right">{c.lt.toFixed(2)}</td><td className="num px-3 py-2 text-right">{fmt(c.total)}</td>
                <td className="num px-3 py-2 text-right">{fmt(c.avg, 1)}</td><td className="num px-3 py-2 text-right">{c.pctDemand.toFixed(1)}%</td><td className="num px-3 py-2 text-right">{fmt(c.value)}</td></tr>))}
              <tr className="border-t bg-muted/40 font-semibold"><td className="px-3 py-2">Total</td><td className="num px-3 py-2 text-right">{calc.length}</td><td className="px-3 py-2" />
                <td className="num px-3 py-2 text-right">{fmt(total)}</td><td className="num px-3 py-2 text-right">{fmt(total / calc.length, 1)}</td><td className="num px-3 py-2 text-right">{((total / demand) * 100).toFixed(1)}%</td><td className="num px-3 py-2 text-right">{fmt(value)}</td></tr>
            </tbody>
          </table>
        </div>
      </Panel>
      <DataNote>Because σ is a fixed 10% of demand and lead time is used in the professor’s units, buffers come out near 29% of annual demand in every class; classes differ in absolute size, not in ratio.</DataNote>
    </div>
  )
}
