import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.rl_arbitrator import RLArbitrator


def test_rl_agent_decision():
    strategies = ["ScalperBot", "SwingBot", "DCAInvestmentBot"]
    state_dim = 10  # adjust if your state vector has a different length
    agent = RLArbitrator(strategies=strategies, state_dim=state_dim)

    dummy_state = [0.1] * state_dim
    selected = agent.select_strategy(dummy_state)

    assert selected in strategies
    print("Selected strategy:", selected)
