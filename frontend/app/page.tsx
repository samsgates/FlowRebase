import Link from "next/link";
import { ArrowRight, CheckCircle2, CircleDollarSign, ShieldAlert } from "lucide-react";
import { StatCard } from "@/components/stat-card";
import { api } from "@/lib/api";

export default async function Dashboard() {
  const [summary, automations] = await Promise.all([api.portfolio(), api.automations()]);
  const top = automations.slice(0, 5);
  return (
    <>
      <header className="topbar"><div><div className="eyebrow">Enterprise automation modernization</div><h1>Portfolio intelligence</h1><p>Own the process model. Choose the architecture. Verify every cutover.</p></div><Link className="button" href="/automations">Explore portfolio <ArrowRight size={16} /></Link></header>
      <section className="stats">
        <StatCard label="Automation estate" value={summary.automations.toLocaleString()} note={`${summary.processes} normalized processes`} />
        <StatCard label="High risk" value={summary.high_risk} note="Needs architecture or security review" />
        <StatCard label="Average health" value={`${summary.average_health}%`} note="Reliability, maintainability and risk" />
        <StatCard label="Annual opportunity" value={`$${summary.estimated_annual_savings.toLocaleString()}`} note="Recommendation baseline estimate" />
      </section>

      <section className="split">
        <article className="panel">
          <div className="panel-head"><div><span className="eyebrow">Modernization pipeline</span><h2>From estate to verified architecture</h2></div></div>
          <div className="pipeline">
            {["Discover", "Understand", "Normalize", "Advise", "Compile", "ProofRun", "Shadow", "Control"].map((x, i) => <div key={x}><span>{String(i + 1).padStart(2, "0")}</span><strong>{x}</strong></div>)}
          </div>
        </article>
        <article className="panel insight">
          <div className="eyebrow">Control principles</div>
          <h2>Generated is not migrated.</h2>
          <p>FlowRebase keeps generation, validation, approval, shadowing and deployment as separate states.</p>
          <ul className="check-list">
            <li><CheckCircle2 size={17} /> Evidence-backed recommendations</li>
            <li><ShieldAlert size={17} /> Critical controls can block deployment</li>
            <li><CircleDollarSign size={17} /> Architecture choices include economics</li>
          </ul>
        </article>
      </section>

      <section className="panel">
        <div className="panel-head"><div><span className="eyebrow">Recent automation assets</span><h2>Modernization candidates</h2></div><Link href="/automations" className="text-link">View all <ArrowRight size={15} /></Link></div>
        {top.length ? <div className="table-wrap"><table><thead><tr><th>Automation</th><th>Source</th><th>Health</th><th>Risk</th><th>Status</th></tr></thead><tbody>{top.map(a => <tr key={a.id}><td><Link href={`/automations/${a.id}`}><strong>{a.name}</strong></Link></td><td>{a.source_type}</td><td>{Math.round(a.health_score)}</td><td>{Math.round(a.risk_score)}</td><td><span className="status">{a.status}</span></td></tr>)}</tbody></table></div> : <EmptyState />}
      </section>
    </>
  );
}

function EmptyState() {
  return <div className="empty"><h3>No automation assets yet</h3><p>Seed the demo with <code>POST /api/v1/demo/seed</code>, or import UiPath, BPMN or Python through the API.</p></div>;
}
