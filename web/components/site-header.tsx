"use client"
import { Logo } from "@/components/logo"
import { ThemeToggle } from "@/components/theme-toggle"
import type { Dashboard } from "@/lib/data"

export function SiteHeader({ meta }: { meta?: Dashboard["meta"] }) {
  return (
    <header className="band">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-4 px-4 py-5 sm:px-6 lg:px-8">
        <div className="flex min-w-0 flex-1 items-center gap-3">
          <Logo />
          <div className="min-w-0">
            <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-emerald-200/80">AI in Operations · Day 4</p>
            <h1 className="truncate text-xl font-semibold leading-tight sm:text-2xl">Inventory Control Room</h1>
          </div>
        </div>
        <div className="hidden text-right text-xs leading-5 text-emerald-100/85 md:block">
          <p className="font-semibold text-white">{meta?.name ?? "Krishna Mathur"} · <span className="num">{meta?.enrollment_id ?? "AS25DXB018"}</span></p>
          <p>{meta?.program ?? "MAIB, September 2025"} · {meta?.professor ?? "Prof. Dr. Sandip Kumar Roy"}</p>
        </div>
        <ThemeToggle />
      </div>
    </header>
  )
}
