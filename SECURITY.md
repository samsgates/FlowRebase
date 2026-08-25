# Security Policy

Please report suspected vulnerabilities privately to the project maintainers. Do not open public issues containing credentials, exploit details, customer automation source code, or sensitive workflow data.

FlowRebase treats imported automation assets as untrusted input. Production deployments should isolate parser/compiler workers, disable arbitrary code execution in the control plane, use least-privilege workload identities, and store only secret references rather than raw credentials.
