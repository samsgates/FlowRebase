from __future__ import annotations

from .uam import UAMProcess


def diff_uam(before: UAMProcess, after: UAMProcess) -> dict:
    before_nodes = {n.id: n for n in before.nodes}
    after_nodes = {n.id: n for n in after.nodes}
    added = [after_nodes[x].model_dump(mode="json") for x in sorted(after_nodes.keys() - before_nodes.keys())]
    removed = [before_nodes[x].model_dump(mode="json") for x in sorted(before_nodes.keys() - after_nodes.keys())]
    changed = []
    for node_id in sorted(before_nodes.keys() & after_nodes.keys()):
        a = before_nodes[node_id].model_dump(mode="json")
        b = after_nodes[node_id].model_dump(mode="json")
        if a != b:
            changed.append({"id": node_id, "before": a, "after": b})
    before_edges = {f"{e.source}|{e.target}|{e.condition or ''}" for e in before.edges}
    after_edges = {f"{e.source}|{e.target}|{e.condition or ''}" for e in after.edges}
    return {
        "from_version": before.version,
        "to_version": after.version,
        "intent_changed": before.intent.model_dump() != after.intent.model_dump(),
        "nodes": {"added": added, "removed": removed, "changed": changed},
        "edges": {"added": sorted(after_edges - before_edges), "removed": sorted(before_edges - after_edges)},
        "policies_changed": [p.model_dump(mode="json") for p in before.policies] != [p.model_dump(mode="json") for p in after.policies],
        "has_changes": bool(added or removed or changed or before_edges != after_edges or before.intent != after.intent or before.policies != after.policies),
    }
