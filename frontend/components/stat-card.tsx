export function StatCard({ label, value, note }: { label: string; value: string | number; note?: string }) {
  return (
    <article className="stat-card">
      <div className="eyebrow">{label}</div>
      <div className="stat-value">{value}</div>
      {note ? <div className="muted">{note}</div> : null}
    </article>
  );
}
