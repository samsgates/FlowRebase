# Security Architecture

FlowRebase treats all imported automation assets as untrusted.

- The control plane never executes imported source code.
- UAM simulation uses a restricted AST evaluator with no function calls, imports or arbitrary attribute access.
- Production compiler/runtime adapters should execute in isolated worker pools.
- Secrets are represented as references. Raw secret material should stay in enterprise secret managers.
- OIDC is the recommended production authentication mode.
- High-risk deployment requires a passing ProofRun and role-authorized approval.
- OPA can be used as an external policy decision point.
- AI calls are optional and must pass through the AI gateway/policy boundary.
