# Universal Automation Model

UAM is FlowRebase's canonical vendor-neutral process representation. Source adapters parse vendor assets into UAM. All analysis, modernization advice, verification and target compilation operate on UAM rather than directly on source code.

## Design constraints

- Preserve business intent independently of implementation.
- Preserve evidence and provenance for extracted rules.
- Make deterministic, probabilistic and human-accountable work explicit.
- Keep policies independent from runtime implementation.
- Allow vendor extensions without polluting the core schema.
- Keep graph validation deterministic.
- Version every process change.

## Minimal process

```yaml
schema_version: "1.0"
id: hello
name: Hello Process
intent:
  objective: Return a greeting
nodes:
  - id: start
    kind: start
    name: Start
  - id: set-output
    kind: task
    name: Set output
    config:
      set_output:
        message: hello
  - id: end
    kind: end
    name: End
edges:
  - source: start
    target: set-output
  - source: set-output
    target: end
```
