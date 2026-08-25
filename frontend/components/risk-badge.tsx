export function RiskBadge({ score }: { score: number }) {
  const label = score >= 70 ? "High" : score >= 40 ? "Medium" : "Low";
  return <span className={`risk risk-${label.toLowerCase()}`}>{label} · {Math.round(score)}</span>;
}
