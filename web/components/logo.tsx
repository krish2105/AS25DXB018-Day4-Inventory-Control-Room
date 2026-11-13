export function Logo({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" role="img" aria-label="Stockroom logo" fill="none">
      <rect width="48" height="48" rx="12" fill="rgb(61 213 152 / 0.16)" stroke="rgb(61 213 152 / 0.5)" />
      <path d="M24 9 36 15.5v13L24 35 12 28.5v-13L24 9Z" fill="#3dd598" />
      <path d="M24 9v13m0 0 12-6.5M24 22 12 15.5" stroke="#0a3d2c" strokeWidth="1.8" strokeLinejoin="round" />
      <rect x="10" y="33" width="28" height="5" rx="2.5" fill="#e8f4ed" />
      <rect x="10" y="33" width="17" height="5" rx="2.5" fill="#3dd598" opacity=".55" />
    </svg>
  )
}
