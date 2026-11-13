"use client"
import { useMemo, useState } from "react"
import { Bar, Cell, ComposedChart, Line, Pie, PieChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts"
import { ArrowDown, ArrowUp, ArrowUpDown, Download, Search } from "lucide-react"
import type { ABC, Dashboard, Item } from "@/lib/data"
import { fmt } from "@/lib/stats"
import { abcColor, COLORS, ChartTip, Panel, Segmented } from "./ui"

type SortKey = keyof Item
const COLS: { key: SortKey; label: string; num?: boolean }[] = [
  { key: "Rank", label: "Rank", num: true }, { key: "Item", label: "Item" }, { key: "Annual_Usage", label: "Usage", num: true },
  { key: "Unit_Cost", label: "Unit cost", num: true }, { key: "Lead_Time", label: "Lead time", num: true },
  { key: "Annual_Value", label: "Annual value", num: true }, { key: "Cumulative%", label: "Cum. %", num: true },
  { key: "ABC_Category", label: "Class" }, { key: "Predicted_ABC", label: "AI class" },
]

export function ABCAnalysis({ d }: { d: Dashboard }) {
  const [cls, setCls] = useState<"ALL" | ABC>("ALL")
  const [q, setQ] = useState("")
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 }>({ key: "Rank", dir: 1 })
  const [page, setPage] = useState(0)
  const PAGE = 12

  const rows = useMemo(() => {
    const ql = q.trim().toLowerCase()
    let r = d.items.filter((i) => (cls === "ALL" || i.ABC_Category === cls) && (!ql || i.Item.toLowerCase().includes(ql)))
    r = [...r].sort((a, b) => {
      const x = a[sort.key] as any, y = b[sort.key] as any
      return (typeof x === "number" ? x - y : String(x).localeCompare(String(y))) * sort.dir
    })
    return r
  }, [d.items, cls, q, sort])
  const pages = Math.max(1, Math.ceil(rows.length / PAGE))
  const cur = Math.min(page, pages - 1)

  const pareto = useMemo(() => d.items.map((i) => ({ rank: i.Rank, value: i.Annual_Value, cum: i["Cumulative%"], c: i.ABC_Category, item: i.Item })), [d.items])
  const donut = d.abc_summary.map((s) => ({ name: `Class ${s.Category}`, value: s.Items, share: s["Value_%"], c: s.Category }))

  function exportCsv() {
    const head = COLS.map((c) => c.label).join(",")
    const body = rows.map((r) => COLS.map((c) => JSON.stringify(r[c.key])).join(",")).join("\n")
    const blob = new Blob([head + "\n" + body], { type: "text/csv" })
    const a = document.createElement("a")
    a.href = URL.createObjectURL(blob); a.download = `abc_items_${cls}.csv`; a.click(); URL.revokeObjectURL(a.href)
  }
  const th = (k: SortKey) => setSort((s) => (s.key === k ? { key: k, dir: (s.dir * -1) as 1 | -1 } : { key: k, dir: 1 }))

  return (
    <div className="space-y-6">
      <Panel title="Pareto chart – annual consumption value" desc="Bars: annual value per item, ranked. Line: cumulative share of total value. Dashed lines mark the 70% (A/B) and 90% (B/C) cut-offs. Use the filter to highlight one class."
        right={<Segmented label="Highlight class" value={cls} onChange={(v) => { setCls(v); setPage(0) }} options={[{ value: "ALL", label: "All" }, { value: "A", label: "A" }, { value: "B", label: "B" }, { value: "C", label: "C" }]} />}>
        <ul className="mb-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-xs text-muted-foreground" aria-label="Legend">
          {(["A", "B", "C"] as const).map((c) => <li key={c} className="flex items-center gap-2"><span className="h-3 w-3 rounded-sm" style={{ background: abcColor(c) }} />Class {c}</li>)}
          <li className="flex items-center gap-2"><span className="h-0.5 w-5 bg-foreground" />Cumulative % of value</li>
        </ul>
        <div className="h-80" role="img" aria-label="Pareto chart: the first 103 items account for 70 percent of annual value">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={pareto} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
              <CartesianGrid stroke="var(--grid)" vertical={false} />
              <XAxis dataKey="rank" type="number" domain={[0, 500]} ticks={[1, 100, 200, 300, 400, 500]} tickLine={false} label={{ value: "Items ranked by annual value (1 = highest)", position: "insideBottom", offset: -4, fill: "var(--axis)", fontSize: 11 }} height={42} />
              <YAxis yAxisId="l" tickLine={false} axisLine={false} tickFormatter={(v) => `${v / 1000}k`} width={44} />
              <YAxis yAxisId="r" orientation="right" domain={[0, 100]} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} width={44} />
              <Tooltip content={<ChartTip labelFmt={(l: number) => `Rank ${l}`} valFmt={(v: number, n: string) => (n.startsWith("Cum") ? `${v.toFixed(1)}%` : fmt(v))} />} />
              <Bar yAxisId="l" dataKey="value" name="Annual value" barSize={2} isAnimationActive={false}>
                {pareto.map((p) => <Cell key={p.rank} fill={abcColor(p.c)} fillOpacity={cls === "ALL" || cls === p.c ? 1 : 0.15} />)}
              </Bar>
              <Line yAxisId="r" dataKey="cum" name="Cumulative % of value" stroke="var(--foreground)" strokeWidth={2} dot={false} isAnimationActive={false} />
              <ReferenceLine yAxisId="r" y={70} stroke="var(--axis)" strokeDasharray="4 4" label={{ value: "70%", position: "insideTopLeft", fill: "var(--axis)", fontSize: 11 }} />
              <ReferenceLine yAxisId="r" y={90} stroke="var(--axis)" strokeDasharray="4 4" label={{ value: "90%", position: "insideTopLeft", fill: "var(--axis)", fontSize: 11 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <div className="grid gap-6 lg:grid-cols-5">
        <Panel title="Category distribution" desc="Number of items per class." className="lg:col-span-2">
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie isAnimationActive={false} data={donut} dataKey="value" nameKey="name" innerRadius="55%" outerRadius="88%" paddingAngle={2} stroke="var(--card)" strokeWidth={2}
                  label={({ name, value }: any) => `${name.slice(-1)} · ${value}`} labelLine={false}>
                  {donut.map((e) => <Cell key={e.c} fill={(COLORS as any)[e.c]} />)}
                </Pie>
                <Tooltip content={<ChartTip valFmt={(v: number, _n: string, p: any) => `${v} items · ${p.payload.share.toFixed(1)}% of value`} />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Share of items vs share of value" desc="The ‘vital few, trivial many’ pattern." className="lg:col-span-3">
          <div className="space-y-3">
            {d.abc_summary.map((s) => (
              <div key={s.Category}>
                <div className="mb-1 flex items-center justify-between text-sm"><span className="font-semibold" style={{ color: abcColor(s.Category) }}>Class {s.Category}</span>
                  <span className="num text-muted-foreground">{s["Items_%"].toFixed(1)}% of items → {s["Value_%"].toFixed(1)}% of value</span></div>
                <div className="space-y-1">
                  <div className="h-2.5 rounded-full bg-muted"><div className="h-full rounded-full" style={{ width: `${s["Items_%"]}%`, background: "var(--before)" }} /></div>
                  <div className="h-2.5 rounded-full bg-muted"><div className="h-full rounded-full" style={{ width: `${s["Value_%"]}%`, background: abcColor(s.Category) }} /></div>
                </div>
              </div>
            ))}
            <p className="text-xs text-muted-foreground">Grey bar = share of items · coloured bar = share of annual value.</p>
          </div>
        </Panel>
      </div>

      <Panel title="Items" desc={`${fmt(rows.length)} of ${fmt(d.items.length)} items shown. Click a column header to sort.`}
        right={
          <div className="flex flex-wrap items-center gap-2">
            <label className="relative">
              <span className="sr-only">Search items</span>
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
              <input value={q} onChange={(e) => { setQ(e.target.value); setPage(0) }} placeholder="Search SKU…" className="h-10 w-44 rounded-lg border bg-background pl-9 pr-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring" />
            </label>
            <Segmented label="Class filter" value={cls} onChange={(v) => { setCls(v); setPage(0) }} options={[{ value: "ALL", label: "All" }, { value: "A", label: "A" }, { value: "B", label: "B" }, { value: "C", label: "C" }]} />
            <button onClick={exportCsv} className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary px-3 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring">
              <Download className="h-4 w-4" aria-hidden /> Export CSV
            </button>
          </div>}>
        <div className="overflow-x-auto scrollbar-thin rounded-lg border">
          <table className="w-full min-w-[760px] text-sm">
            <thead className="bg-muted/60 text-left text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                {COLS.map((c) => (
                  <th key={c.key} scope="col" className={`px-3 py-2.5 ${c.num ? "text-right" : ""}`} aria-sort={sort.key === c.key ? (sort.dir === 1 ? "ascending" : "descending") : "none"}>
                    <button onClick={() => th(c.key)} className="inline-flex items-center gap-1 font-semibold hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring">
                      {c.label}{sort.key === c.key ? (sort.dir === 1 ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />) : <ArrowUpDown className="h-3 w-3 opacity-40" />}
                    </button>
                  </th>))}
              </tr>
            </thead>
            <tbody>
              {rows.slice(cur * PAGE, cur * PAGE + PAGE).map((r) => (
                <tr key={r.Item} className="border-t hover:bg-muted/40">
                  <td className="num px-3 py-2 text-right text-muted-foreground">{r.Rank}</td>
                  <td className="num px-3 py-2 font-medium">{r.Item}</td>
                  <td className="num px-3 py-2 text-right">{fmt(r.Annual_Usage)}</td>
                  <td className="num px-3 py-2 text-right">{r.Unit_Cost.toFixed(2)}</td>
                  <td className="num px-3 py-2 text-right">{r.Lead_Time}</td>
                  <td className="num px-3 py-2 text-right">{fmt(r.Annual_Value)}</td>
                  <td className="num px-3 py-2 text-right">{r["Cumulative%"].toFixed(1)}%</td>
                  <td className="px-3 py-2"><Chip c={r.ABC_Category} /></td>
                  <td className="px-3 py-2"><Chip c={r.Predicted_ABC} wrong={r.Predicted_ABC !== r.ABC_Category} /></td>
                </tr>))}
              {rows.length === 0 && <tr><td colSpan={COLS.length} className="px-3 py-10 text-center text-muted-foreground">No items match. Clear the search or choose another class.</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="mt-3 flex items-center justify-between text-sm text-muted-foreground">
          <span>Page <span className="num">{cur + 1}</span> of <span className="num">{pages}</span></span>
          <div className="flex gap-2">
            <button disabled={cur === 0} onClick={() => setPage(cur - 1)} className="h-10 rounded-lg border px-3 disabled:opacity-40 hover:bg-muted">Previous</button>
            <button disabled={cur >= pages - 1} onClick={() => setPage(cur + 1)} className="h-10 rounded-lg border px-3 disabled:opacity-40 hover:bg-muted">Next</button>
          </div>
        </div>
      </Panel>
    </div>
  )
}

function Chip({ c, wrong }: { c: ABC; wrong?: boolean }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold" style={{ background: `color-mix(in srgb, ${abcColor(c)} 18%, transparent)`, color: abcColor(c), outline: wrong ? "1.5px dashed var(--destructive)" : undefined }}
      title={wrong ? "AI class differs from the value-based class" : undefined}>
      {c}{wrong && <span aria-label="differs from value-based class">≠</span>}
    </span>
  )
}
