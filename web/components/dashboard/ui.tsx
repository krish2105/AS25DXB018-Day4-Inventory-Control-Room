"use client"
import { motion, useReducedMotion } from "framer-motion"
import { ReactNode } from "react"
import { cn } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"
import { Info } from "lucide-react"

export const COLORS = {
  A: "var(--abc-a)", B: "var(--abc-b)", C: "var(--abc-c)",
  before: "var(--before)", after: "var(--after)", ss: "var(--ss-blue)", hc: "var(--hc-green)",
  grid: "var(--grid)", primary: "var(--primary)",
} as const
export const abcColor = (c: string) => (c === "A" ? COLORS.A : c === "B" ? COLORS.B : COLORS.C)

export function Reveal({ children, delay = 0, className }: { children: ReactNode; delay?: number; className?: string }) {
  const reduce = useReducedMotion()
  return (
    <motion.div className={className} initial={reduce ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: [0.22, 1, 0.36, 1] }}>
      {children}
    </motion.div>
  )
}

export function KpiCard({ label, value, sub, accent, hint, delay = 0 }: { label: string; value: ReactNode; sub?: ReactNode; accent?: string; hint?: string; delay?: number }) {
  return (
    <Reveal delay={delay} className="h-full">
      <div className="card-surface relative h-full overflow-hidden p-5" title={hint}>
        {accent && <span aria-hidden className="absolute inset-y-0 left-0 w-1" style={{ background: accent }} />}
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{label}</p>
        <p className="num mt-2 text-3xl font-semibold leading-none text-foreground">{value}</p>
        {sub && <p className="mt-2 text-sm text-muted-foreground">{sub}</p>}
      </div>
    </Reveal>
  )
}

export function Panel({ title, desc, children, className, right, id }: { title: string; desc?: ReactNode; children: ReactNode; className?: string; right?: ReactNode; id?: string }) {
  return (
    <section id={id} className={cn("card-surface min-w-0 p-5 sm:p-6", className)} aria-label={title}>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="text-base font-semibold sm:text-lg">{title}</h3>
          {desc && <p className="mt-1 max-w-3xl text-sm text-muted-foreground">{desc}</p>}
        </div>
        {right}
      </div>
      {children}
    </section>
  )
}

export function ChartTip({ active, payload, label, labelFmt, valFmt }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border bg-popover px-3 py-2 text-xs shadow-lg" role="status">
      {label !== undefined && <p className="mb-1 font-semibold text-foreground">{labelFmt ? labelFmt(label) : String(label)}</p>}
      {payload.filter((p: any) => p.value !== undefined && p.value !== null && p.name !== "_").map((p: any, i: number) => (
        <p key={i} className="flex items-center gap-2 text-muted-foreground">
          <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: p.color ?? p.fill ?? p.stroke }} />
          <span>{p.name}</span>
          <span className="num ml-auto pl-3 font-semibold text-foreground">{valFmt ? valFmt(p.value, p.name, p) : typeof p.value === "number" ? p.value.toLocaleString("en-US", { maximumFractionDigits: 2 }) : p.value}</span>
        </p>
      ))}
    </div>
  )
}

export function Insight({ children, tone = "info" }: { children: ReactNode; tone?: "info" | "good" | "warn" }) {
  const c = tone === "good" ? "var(--abc-a)" : tone === "warn" ? "var(--abc-b)" : "var(--abc-c)"
  return (
    <li className="flex gap-3 rounded-lg border bg-muted/40 p-3 text-sm leading-6">
      <span aria-hidden className="mt-2 h-2 w-2 shrink-0 rounded-full" style={{ background: c }} />
      <span>{children}</span>
    </li>
  )
}

export function Verdict({ kind }: { kind: "clear" | "marginal" | "tradeoff" }) {
  const map = {
    clear: { t: "Clear gain", c: "bg-primary/15 text-primary" },
    marginal: { t: "Marginal gain", c: "bg-amber-500/15 text-amber-700 dark:text-amber-300" },
    tradeoff: { t: "Trade-off", c: "bg-sky-500/15 text-sky-700 dark:text-sky-300" },
  }[kind]
  return <span className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold", map.c)}>{map.t}</span>
}

export function DataNote({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-dashed bg-accent/50 px-3 py-2 text-xs text-muted-foreground" role="note">
      <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden />
      <span>{children}</span>
    </div>
  )
}

export function LoadingGrid() {
  return (
    <div className="space-y-6" aria-busy="true" aria-live="polite">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
      </div>
      <Skeleton className="h-80 rounded-xl" />
    </div>
  )
}

export function Segmented<T extends string | number>({ value, onChange, options, label }: { value: T; onChange: (v: T) => void; options: { value: T; label: string }[]; label: string }) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-lg border bg-muted/60 p-1">
      {options.map((o) => (
        <button key={String(o.value)} role="radio" aria-checked={o.value === value} onClick={() => onChange(o.value)}
          className={cn("min-h-9 rounded-md px-3 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-ring",
            o.value === value ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:text-foreground")}>
          {o.label}
        </button>
      ))}
    </div>
  )
}

export function Range({ label, value, min, max, step, onChange, unit, display }: { label: string; value: number; min: number; max: number; step: number; onChange: (v: number) => void; unit?: string; display?: string }) {
  const fill = ((value - min) / (max - min)) * 100
  return (
    <label className="block">
      <span className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>{label}</span>
        <span className="num text-sm font-semibold text-foreground">{display ?? value}{unit}</span>
      </span>
      <input type="range" className="range" min={min} max={max} step={step} value={value} aria-label={label}
        style={{ ["--fill" as any]: `${fill}%` }} onChange={(e) => onChange(parseFloat(e.target.value))} />
    </label>
  )
}
