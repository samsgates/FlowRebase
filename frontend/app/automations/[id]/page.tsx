import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, Binary, CircleDollarSign, ShieldCheck } from "lucide-react";
import { RiskBadge } from "@/components/risk-badge";
import { api } from "@/lib/api";

export default async function AutomationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = await api.automation(id);
  if (!item) notFound();
  const rec = item.recommendation;
  return (
    <>
      <header className="topbar"><div><div className="eyebrow">Automation · {item.source_type}</div><h1>{item.name}</h1><p>Normalized source asset with health, risk and modernization intelligence.</p></div>{item.process ? <Link className="button" href={`/processes/${item.process.id}`}>Open UAM process <ArrowRight size={16} /></Link> : null}</header>
      <section className="stats stats-3"><article className="stat-card"><div className="eyebrow">Health</div><div className="stat-value">{Math.round(item.health_score)}</div><div className="muted">out of 100</div></article><article className="stat-card"><div className="eyebrow">Risk</div><div className="stat-value"><RiskBadge score={item.risk_score} /></div><div className="muted">architecture and runtime exposure</div></article><article className="stat-card"><div className="eyebrow">Process model</div><div className="stat-value">{item.process ? item.process.uam.nodes.length : 0}</div><div className="muted">UAM nodes</div></article></section>
      <section className="split">
        <article className="panel">
          <div className="eyebrow">Rebase Advisor</div>
          <h2>{rec?.disposition ?? "Not analyzed"}</h2>
          <p className="lead">{rec ? `${Math.round(rec.confidence * 100)}% recommendation confidence` : "Run the Advisor to generate an evidence-backed modernization disposition."}</p>
          <ul className="reason-list">{rec?.rationale?.map(x => <li key={x}><Binary size={16} /> {x}</li>)}</ul>
        </article>
        <article className="panel">
          <div className="eyebrow">Economics</div>
          <h2>Modernization opportunity</h2>
          <div className="economics"><div><CircleDollarSign size={18} /><span>Current annual cost<strong>${Number(rec?.economics?.current_annual_cost ?? 0).toLocaleString()}</strong></span></div><div><ShieldCheck size={18} /><span>Estimated annual savings<strong>${Number(rec?.economics?.estimated_annual_savings ?? 0).toLocaleString()}</strong></span></div></div>
        </article>
      </section>
      {item.process ? <section className="panel"><div className="panel-head"><div><span className="eyebrow">Dependencies</span><h2>Applications discovered</h2></div></div><div className="chips">{item.process.uam.applications.length ? item.process.uam.applications.map(x => <span key={x}>{x}</span>) : <span>No application metadata yet</span>}</div></section> : null}
    </>
  );
}
