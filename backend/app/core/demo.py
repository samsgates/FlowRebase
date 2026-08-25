from .uam import Determinism, Evidence, NodeKind, UAMEdge, UAMIntent, UAMNode, UAMPolicy, UAMProcess


def demo_uam() -> UAMProcess:
    return UAMProcess(
        id="uam-demo-invoice",
        name="Vendor Invoice Processing",
        version="1.0.0",
        source={"type": "demo", "platform": "UiPath"},
        intent=UAMIntent(
            objective="Validate and route supplier invoices",
            business_outcomes={"status": "processed"},
            owner="Finance Operations",
            criticality="high",
        ),
        applications=["Microsoft Outlook", "SAP", "Microsoft Excel"],
        nodes=[
            UAMNode(id="start", kind=NodeKind.START, name="Invoice received", criticality="high"),
            UAMNode(id="extract", kind=NodeKind.DOCUMENT, name="Extract invoice", determinism=Determinism.PROBABILISTIC, config={"sim_latency_ms": 450, "sim_failure_rate": 0.02}),
            UAMNode(id="validate", kind=NodeKind.POLICY, name="Validate vendor and amount", config={"sim_latency_ms": 80}),
            UAMNode(id="decision", kind=NodeKind.DECISION, name="High value?", config={"expression": "input.amount > 5000"}),
            UAMNode(id="approval", kind=NodeKind.APPROVAL, name="Manager approval", determinism=Determinism.HUMAN_ACCOUNTABLE, criticality="mission_critical", config={"sim_latency_ms": 240000}),
            UAMNode(id="post", kind=NodeKind.API_CALL, name="Post to SAP", application="SAP", criticality="mission_critical", config={"sim_latency_ms": 500, "sim_failure_rate": 0.01, "set_output": {"status": "processed", "approved": True}}),
            UAMNode(id="post-low", kind=NodeKind.API_CALL, name="Post low-value invoice to SAP", application="SAP", criticality="high", config={"sim_latency_ms": 500, "sim_failure_rate": 0.01, "set_output": {"status": "processed", "approved": True}}),
            UAMNode(id="end", kind=NodeKind.END, name="Completed"),
        ],
        edges=[
            UAMEdge(source="start", target="extract"),
            UAMEdge(source="extract", target="validate"),
            UAMEdge(source="validate", target="decision"),
            UAMEdge(source="decision", target="approval", condition="input.amount > 5000", label="yes"),
            UAMEdge(source="decision", target="post-low", condition="input.amount <= 5000", label="no"),
            UAMEdge(source="approval", target="post"),
            UAMEdge(source="post", target="end"),
            UAMEdge(source="post-low", target="end"),
        ],
        policies=[
            UAMPolicy(id="payment-approval", name="High-value approval", effect="require_approval", action="deploy", when={"max_payment": {"gt": 5000}}, reason="Financial control requires approval above $5,000")
        ],
        evidence=[Evidence(id="ev-demo", source_type="demo-sop", source_ref="finance-sop#approval", excerpt="Invoices above $5,000 require manager approval", confidence=1)],
        economics={"annual_cost": 180000},
    )
