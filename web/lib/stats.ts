/** Statistics helpers – mirror scipy.stats.norm used in the notebook. */

// Inverse standard-normal CDF (Acklam) with one Halley refinement step -> ~1e-15 precision.
export function normPpf(p: number): number {
  if (p <= 0) return -Infinity
  if (p >= 1) return Infinity
  const a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104469687e2, 1.38357751867269e2, -3.066479806614716e1, 2.506628277459239]
  const b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2, 6.680131188771972e1, -1.328068155288572e1]
  const c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
  const d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996, 3.754408661907416]
  const plow = 0.02425
  let x: number
  if (p < plow) {
    const q = Math.sqrt(-2 * Math.log(p))
    x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
  } else if (p <= 1 - plow) {
    const q = p - 0.5
    const r = q * q
    x = ((((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q) / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
  } else {
    const q = Math.sqrt(-2 * Math.log(1 - p))
    x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
  }
  // Halley refinement
  const e = normCdf(x) - p
  const u = e * Math.sqrt(2 * Math.PI) * Math.exp((x * x) / 2)
  return x - u / (1 + (x * u) / 2)
}

function erf(x: number): number {
  // high-precision erf via series/continued fraction (W. J. Cody style simplification)
  const sign = x < 0 ? -1 : 1
  x = Math.abs(x)
  if (x < 2.5) {
    let sum = x, term = x, n = 0
    while (Math.abs(term) > 1e-17 * Math.abs(sum) && n < 200) {
      n++
      term *= (-x * x) / n
      sum += term / (2 * n + 1)
    }
    return sign * (2 / Math.sqrt(Math.PI)) * sum
  }
  // continued fraction for erfc
  let f = 0
  for (let k = 60; k >= 1; k--) f = k / 2 / (x + f)
  const erfc = Math.exp(-x * x) / (Math.sqrt(Math.PI) * (x + f))
  return sign * (1 - erfc)
}
export const normCdf = (x: number) => 0.5 * (1 + erf(x / Math.SQRT2))
export const normPdf = (x: number) => Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI)
export const lossFn = (z: number) => normPdf(z) - z * (1 - normCdf(z))

export interface ProductParams { mean: number; cvPct: number; lead: number; h: number }

export function productCurve(p: ProductParams, levels: number[]) {
  const sigma = (p.mean * p.cvPct) / 100
  return levels.map((s) => {
    const z = normPpf(s)
    const ss = z * sigma * Math.sqrt(p.lead)
    return { sl: s, z, ss, hc: ss * p.h }
  })
}

/** Notebook rule: highest level whose last +1 pp step costs <= tolerance (holding cost units); 80 % if none. */
export function recommendLevel(curve: { sl: number; hc: number }[], tol: number): number {
  let best = 0.8
  for (let i = 1; i < curve.length; i++) {
    if (curve[i].hc - curve[i - 1].hc <= tol) best = curve[i].sl
  }
  return best
}

export const fmt = (v: number, d = 0) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d })
export const pct = (v: number, d = 1) => `${(v * 100).toFixed(d)}%`
