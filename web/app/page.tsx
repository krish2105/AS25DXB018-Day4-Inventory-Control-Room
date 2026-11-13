"use client"
import { useEffect, useState } from "react"
import { AlertTriangle, BarChart3, BrainCircuit, GitCompareArrows, LayoutDashboard, ShieldCheck, SlidersHorizontal } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SiteHeader } from "@/components/site-header"
import { SiteFooter } from "@/components/site-footer"
import { useDashboard } from "@/lib/data"
import { LoadingGrid } from "@/components/dashboard/ui"
import { Overview } from "@/components/dashboard/overview"
import { ABCAnalysis } from "@/components/dashboard/abc-analysis"
import { AIModels } from "@/components/dashboard/ai-models"
import { SafetyStock } from "@/components/dashboard/safety-stock"
import { Simulator } from "@/components/dashboard/simulator"
import { BeforeAfter } from "@/components/dashboard/before-after"

const TABS = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "abc", label: "ABC Analysis", icon: BarChart3 },
  { id: "models", label: "AI Models", icon: BrainCircuit },
  { id: "safety", label: "Safety Stock", icon: ShieldCheck },
  { id: "simulator", label: "Service-Level Simulator", icon: SlidersHorizontal },
  { id: "compare", label: "Before vs After AI", icon: GitCompareArrows },
] as const

export default function Page() {
  const { data, error, retry } = useDashboard()
  const [tab, setTab] = useState<string>("overview")

  useEffect(() => {
    const read = () => {
      const h = window.location.hash.replace("#", "")
      if (TABS.some((t) => t.id === h)) setTab(h)
    }
    read()
    window.addEventListener("hashchange", read)
    return () => window.removeEventListener("hashchange", read)
  }, [])
  const change = (v: any) => { setTab(String(v)); history.replaceState(null, "", `#${v}`) }

  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground">Skip to content</a>
      <SiteHeader meta={data?.meta} />
      <Tabs value={tab} onValueChange={change} className="flex-1 gap-0">
        <div className="glass sticky top-0 z-30 border-b">
          <div className="mx-auto max-w-7xl overflow-x-auto px-4 py-2 scrollbar-thin sm:px-6 lg:px-8">
            <TabsList variant="line" className="h-auto w-max min-w-full justify-start gap-1 bg-transparent p-0" aria-label="Dashboard sections">
              {TABS.map(({ id, label, icon: Icon }) => (
                <TabsTrigger key={id} value={id} className="h-11 shrink-0 gap-2 rounded-lg px-4 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground data-active:bg-primary/10 data-active:text-primary after:hidden">
                  <Icon className="h-4 w-4" aria-hidden />{label}
                </TabsTrigger>))}
            </TabsList>
          </div>
        </div>
        <main id="main" className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {error && (
            <div role="alert" className="card-surface flex flex-col items-start gap-3 p-6">
              <p className="flex items-center gap-2 font-semibold"><AlertTriangle className="h-5 w-5 text-destructive" aria-hidden />The results file could not be loaded</p>
              <p className="text-sm text-muted-foreground">Could not read <code>/data/dashboard_data.json</code> ({error}). Run the notebook export and copy the file to <code>web/public/data/</code>, then retry.</p>
              <button onClick={retry} className="h-10 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground hover:opacity-90">Retry</button>
            </div>)}
          {!error && !data && <LoadingGrid />}
          {data && (
            <>
              <TabsContent value="overview"><Overview d={data} /></TabsContent>
              <TabsContent value="abc"><ABCAnalysis d={data} /></TabsContent>
              <TabsContent value="models"><AIModels d={data} /></TabsContent>
              <TabsContent value="safety"><SafetyStock d={data} /></TabsContent>
              <TabsContent value="simulator"><Simulator d={data} /></TabsContent>
              <TabsContent value="compare"><BeforeAfter d={data} /></TabsContent>
            </>)}
        </main>
      </Tabs>
      <SiteFooter meta={data?.meta} />
    </>
  )
}
