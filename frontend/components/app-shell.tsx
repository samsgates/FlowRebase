import Link from "next/link";
import { Activity, Blocks, FlaskConical, GitBranch, Gauge, Home, Network, Rocket, Scale, Settings, ShieldCheck, type LucideIcon } from "lucide-react";

const nav: Array<[string, string, LucideIcon]> = [
  ["Overview", "/", Home],
  ["Portfolio", "/automations", Blocks],
  ["Discover", "/automations", Network],
  ["Processes", "/automations", GitBranch],
  ["Advisor", "/automations", Scale],
  ["ProofRun", "/automations", FlaskConical],
  ["Deploy", "/automations", Rocket],
  ["Control", "/automations", Activity],
  ["Policies", "/automations", ShieldCheck],
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link href="/" className="brand" aria-label="FlowRebase home">
          <span className="brand-mark"><Gauge size={20} /></span>
          <span><strong>FlowRebase</strong><small>Automation Control Plane</small></span>
        </Link>
        <nav>
          {nav.map(([label, href, Icon]) => (
            <Link href={href as string} className="nav-item" key={label as string}>
              <Icon size={17} /> {label as string}
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer"><Settings size={16} /> Enterprise workspace</div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
