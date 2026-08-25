import pytest

from app.core.digital_twin import DigitalTwinSimulator
from app.core.policy import PolicyEngine
from app.core.demo import demo_uam


@pytest.mark.asyncio
async def test_local_policy_requires_approval():
    result = await PolicyEngine().evaluate(demo_uam(), "deploy", {"max_payment": 9000})
    assert result.allowed
    assert result["requires_approval"] is True


def test_digital_twin_is_deterministic_for_seed():
    simulator = DigitalTwinSimulator()
    a = simulator.simulate(demo_uam(), runs=100, seed=7)
    b = simulator.simulate(demo_uam(), runs=100, seed=7)
    assert a == b
    assert 0 <= a["predicted_success_rate"] <= 1
