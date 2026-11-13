"use client"
import type { ABC } from "@/lib/data"

/** Accessible heat-map confusion matrix (rows = actual, columns = predicted). */
export function ConfusionMatrix({ cm, labels = ["A", "B", "C"], hue = "var(--primary)", title }: { cm: number[][]; labels?: ABC[] | string[]; hue?: string; title: string }) {
  const max = Math.max(...cm.flat())
  const total = cm.flat().reduce((a, b) => a + b, 0)
  const correct = cm.reduce((s, r, i) => s + r[i], 0)
  return (
    <figure aria-label={`${title}: ${correct} of ${total} correct`}>
      <div className="grid grid-cols-[auto_repeat(3,minmax(0,1fr))] gap-1.5 text-sm">
        <div />
        {labels.map((l) => <div key={l} className="pb-1 text-center text-xs font-semibold text-muted-foreground">Pred {l}</div>)}
        {cm.map((row, i) => (
          <div key={i} className="contents">
            <div className="flex items-center pr-2 text-xs font-semibold text-muted-foreground">Actual {labels[i]}</div>
            {row.map((v, j) => {
              const a = v / max
              return (
                <div key={j} className="num flex h-16 items-center justify-center rounded-lg text-xl font-semibold"
                  style={{ background: `color-mix(in srgb, ${hue} ${Math.round(8 + a * 80)}%, var(--card))`, color: a > 0.55 ? "var(--primary-foreground)" : "var(--foreground)", outline: i === j ? `2px solid ${hue}` : undefined, outlineOffset: -2 }}>
                  {v}
                </div>)
            })}
          </div>))}
      </div>
      <figcaption className="mt-2 text-center text-xs text-muted-foreground">{title} · <span className="num">{correct}</span> of <span className="num">{total}</span> correct (<span className="num">{((correct / total) * 100).toFixed(1)}%</span>)</figcaption>
    </figure>
  )
}
