from app.core.proofrun import ProofRunEngine
from app.core.demo import demo_uam


def test_proofrun_passes_demo_cases():
    process = demo_uam()
    cases = [
        {"name": "low", "input": {"amount": 2000}, "expected": {"status": "processed", "approved": True}, "critical_paths": ["status"]},
        {"name": "high", "input": {"amount": 12000}, "expected": {"status": "processed", "approved": True}, "critical_paths": ["status"]},
    ]
    report = ProofRunEngine().run(process, cases)
    assert report["status"] == "passed"
    assert report["score"] == 100


def test_proofrun_blocks_critical_difference():
    report = ProofRunEngine().run(
        demo_uam(),
        [{"name": "bad", "input": {"amount": 2000}, "expected": {"status": "rejected"}, "critical_paths": ["status"]}],
    )
    assert report["status"] == "failed"
    assert report["critical_failure"] is True
