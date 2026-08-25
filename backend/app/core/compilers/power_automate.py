from __future__ import annotations

import json

from .base import CompiledArtifact, TargetCompiler
from ..uam import UAMProcess


class PowerAutomateDraftCompiler(TargetCompiler):
    target = "power_automate"

    def compile(self, process: UAMProcess) -> CompiledArtifact:
        """Emit a vendor-neutral deployment draft for a Power Automate adapter.

        Microsoft solution/package formats and connector identifiers are environment-specific. This
        artifact is intentionally not represented as a magically importable package. A production
        target adapter must resolve connection references and deploy through supported Microsoft APIs.
        """
        definition = {
            "$schema": "https://flowrebase.dev/schemas/power-automate-draft-v1.json",
            "name": process.name,
            "sourceUamId": process.id,
            "trigger": next((n.model_dump(mode="json") for n in process.nodes if n.kind.value == "start"), None),
            "actions": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.kind.value,
                    "config": n.config,
                    "application": n.application,
                    "policyRefs": n.policy_refs,
                }
                for n in process.nodes
                if n.kind.value not in {"start", "end"}
            ],
            "edges": [e.model_dump(mode="json") for e in process.edges],
            "connectionReferences": sorted(set(process.applications)),
        }
        return CompiledArtifact(
            self.target,
            f"{process.id}.power-automate-draft.json",
            "application/json",
            json.dumps(definition, indent=2),
            [
                "Draft requires environment-specific connector IDs and connection references before deployment.",
                "Run ProofRun after target binding and before production cutover.",
            ],
        )
