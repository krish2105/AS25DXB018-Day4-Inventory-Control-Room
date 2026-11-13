import type { Dashboard } from "@/lib/data"

export function SiteFooter({ meta }: { meta?: Dashboard["meta"] }) {
  return (
    <footer className="mt-12 border-t bg-card/60">
      <div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 py-6 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <p>
          <span className="font-semibold text-foreground">Krishna Mathur</span> | <span className="num">AS25DXB018</span> | MAIB Sept 2025
        </p>
        <p className="max-w-xl sm:text-right">
          {meta?.task ?? "Day 4 – Inventory Management and Optimization, Lab Activity + Lab Exercise"} · {meta?.date ?? "13 November 2026"}.
          Part A data are synthetic (seed 42); Part B parameters are assumptions.
        </p>
      </div>
    </footer>
  )
}
