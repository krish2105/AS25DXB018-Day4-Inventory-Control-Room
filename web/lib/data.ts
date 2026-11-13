"use client"
import { useCallback, useEffect, useState } from "react"

export type ABC = "A" | "B" | "C"
export interface Item {
  Rank: number; Item: string; Annual_Usage: number; Unit_Cost: number; Lead_Time: number; Past_Demand: number
  Annual_Value: number; "Value_Share%": number; "Cumulative%": number; ABC_Category: ABC; Predicted_ABC: ABC; Traditional_ABC: ABC
  Predicted_Demand: number; Std_Dev: number; Safety_Stock: number; SS_Value: number
  SS_Before: number; CSL_Before: number; CSL_After: number; Tree_Split: "train" | "test"; LR_Split: "train" | "test"
}
export interface Param { Product: string; Avg_Demand: number; Demand_Std: number; Lead_Time: number; Holding_Cost: number; "CV_%": number; Sigma_x_sqrtLT: number }
export interface Dashboard {
  meta: { name: string; enrollment_id: string; program: string; course: string; professor: string; task: string; date: string; seed: number; synthetic: boolean; note: string }
  metrics: Record<string, number>
  abc_summary: { Category: ABC; Items: number; Annual_Value: number; "Items_%": number; "Value_%": number }[]
  items: Item[]
  tree: {
    depth: number; leaves: number; train_n: number; test_n: number; acc_train: number; acc_test: number; labels: ABC[]; confusion: number[][]
    report: Record<string, any>; importances: { feature: string; importance: number }[]; depth_cv: { max_depth: number; CV_accuracy: number }[]
  }
  forecast: { coef: number; intercept: number; r2_test: number; mae_test: number; rmse_test: number; r2_train: number; mae_train: number; rmse_train: number; coef_all: number; intercept_all: number }
  safety_stock: { z_95: number; sigma_pct: number; by_class: any[]; total: number; total_value: number }
  partB: {
    parameters: Param[]; service_levels: number[]
    curves: { Product: string; Service_Level: number; Z: number; Safety_Stock: number; Holding_Cost: number }[]
    recommendation: { tolerance: number; levels: Record<string, number>; sensitivity: Record<string, Record<string, string>> }
    policies: any[]
    before_after: { Policy: string; Product: string; Service_Level: number; Z: number; Safety_Stock: number; Holding_Cost: number; Stockout_Prob_per_Cycle: number; Units_Short_per_Cycle: number }[]
    before_after_totals: { Policy: string; Total_Safety_Stock: number; Total_Holding_Cost: number; Total_Units_Short_per_Cycle: number }[]
  }
  before_after: {
    classification: { before: { accuracy: number; macro_f1: number; recall_A: number; confusion: number[][] }; after: { accuracy: number; macro_f1: number; recall_A: number; confusion: number[][] } }
    forecast: { before: Record<string, number>; after: Record<string, number>; points: { item: string; actual: number; before: number; after: number }[] }
    safety_stock: { flat_pct: number; summary: Record<string, { before: number; after: number }> }
  }
}

export function useDashboard() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)
  useEffect(() => {
    let alive = true
    setError(null)
    fetch("/data/dashboard_data.json")
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then((j) => alive && setData(j))
      .catch((e) => alive && setError(String(e.message ?? e)))
    return () => { alive = false }
  }, [tick])
  const retry = useCallback(() => setTick((t) => t + 1), [])
  return { data, error, retry }
}
