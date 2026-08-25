import { notFound } from "next/navigation";
import { ProcessGraph } from "@/components/process-graph";
import { api } from "@/lib/api";

export default async function ProcessPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const item = await api.process(id);
  if (!item) notFound();
  const uam = item.uam;
  const critical = uam.nodes.filter(n => n.criticality === "mission_critical" || n.criticality === "high").length;
  return (
    <>
      <header className="topbar"><div><div className="eyebrow">Universal Automation Model · v{item.version}</div><h1>{item.name}</h1><p>{uam.intent.objective}</p></div></header>
      <section className="stats stats-3"><article className="stat-card"><div className="eyebrow">Nodes</div><div className="stat-value">{uam.nodes.length}</div><div className="muted">portable semantic activities</div></article><article className="stat-card"><div className="eyebrow">Evidence</div><div className="stat-value">{uam.evidence.length}</div><div className="muted">traceable source references</div></article><article className="stat-card"><div className="eyebrow">Critical controls</div><div className="stat-value">{critical}</div><div className="muted">high or mission-critical nodes</div></article></section>
      <section className="panel"><div className="panel-head"><div><span className="eyebrow">Process digital twin</span><h2>Portable process graph</h2></div></div><ProcessGraph process={uam} /></section>
      <section className="split"><article className="panel"><div className="eyebrow">Business intent</div><h2>{uam.intent.objective}</h2><dl className="definition"><dt>Owner</dt><dd>{uam.intent.owner ?? "Unassigned"}</dd><dt>Criticality</dt><dd>{uam.intent.criticality}</dd><dt>Source</dt><dd>{String(uam.source.type ?? "unknown")}</dd></dl></article><article className="panel"><div className="eyebrow">Portability</div><h2>Compile from one canonical model</h2><p>Use <code>POST /api/v1/processes/{item.id}/compile</code> with <code>python</code>, <code>bpmn</code> or <code>power_automate</code>.</p><p>ProofRun evaluates the UAM behavior before any candidate deployment is approved.</p></article></section>
    </>
  );
}
