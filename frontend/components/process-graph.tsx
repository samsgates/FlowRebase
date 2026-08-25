import type { UAMProcess } from "@flowrebase/uam";

export function ProcessGraph({ process }: { process: UAMProcess }) {
  return (
    <div className="graph" role="img" aria-label={`${process.name} process graph`}>
      {process.nodes.map((node, index) => (
        <div className="graph-step" key={node.id}>
          <div className={`node node-${node.kind}`}>
            <span className="node-kind">{node.kind.replaceAll("_", " ")}</span>
            <strong>{node.name}</strong>
            {node.application ? <small>{node.application}</small> : null}
          </div>
          {index < process.nodes.length - 1 ? <span className="connector">→</span> : null}
        </div>
      ))}
    </div>
  );
}
