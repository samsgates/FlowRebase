# Build Validation

Validation performed on August 25, 2026.

## Passed

- Python core source compiles with `compileall`.
- 13 backend unit tests pass.
- UiPath sample parses into valid UAM.
- UAM CLI validation passes.
- Python target compiler emits a candidate artifact.
- ProofRun historical replay passes the included invoice cases at 100% with no critical control failure.
- Digital Twin simulation executes deterministically with a fixed seed.
- Docker Compose YAML parses successfully.
- Kubernetes manifests parse successfully.
- OpenTelemetry collector configuration parses successfully.

## Frontend dependency validation

The execution environment used to create this archive could not complete npm dependency resolution before the network timeout. The Next.js source was therefore statically reviewed but not dependency-built in this environment. Run `npm install && npm run typecheck && npm run build` in `frontend/` in a connected environment before release.

## Production integration boundary

Power Automate output is intentionally emitted as a deployment draft because real connection references and environment IDs are tenant-specific. Production adapters must bind those references through supported vendor APIs. The same rule applies to future UiPath, ServiceNow, Automation Anywhere and Blue Prism deployment adapters.
