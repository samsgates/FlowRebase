import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { RiskBadge } from "@/components/risk-badge";
import { api } from "@/lib/api";

export default async function AutomationsPage() {
  const automations = await api.automations();
  return (
    <>
      <header className="topbar"><div><div className="eyebrow">Portfolio</div><h1>Automation estate</h1><p>Inventory, health, risk and modernization readiness across every discovered automation.</p></div></header>
      <section className="panel">
        {automations.length ? <div className="table-wrap"><table><thead><tr><th>Name</th><th>Platform</th><th>Health</th><th>Risk</th><th>Status</th><th /></tr></thead><tbody>{automations.map(a => <tr key={a.id}><td><strong>{a.name}</strong></td><td><span className="platform">{a.source_type}</span></td><td><div className="meter"><span style={{ width: `${a.health_score}%` }} /></div><small>{Math.round(a.health_score)}/100</small></td><td><RiskBadge score={a.risk_score} /></td><td><span className="status">{a.status}</span></td><td><Link className="icon-link" href={`/automations/${a.id}`} aria-label={`Open ${a.name}`}><ArrowRight size={17} /></Link></td></tr>)}</tbody></table></div> : <div className="empty"><h3>Your estate is empty</h3><p>Use the import API or seed the included demo data to explore the product.</p></div>}
      </section>
    </>
  );
}
