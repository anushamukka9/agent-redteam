"""Benchmark: the prompt-injection pack against both demo agents.

Run with: python -m agent_redteam.benchmark

This is the CI smoke check and the source of the numbers in the
README. It measures two toy agents, not yours. Its job is to prove
the harness runs, the pack is labeled correctly, and the gap between
a careless agent and a guarded one shows up in the score.
"""

from __future__ import annotations

from agent_redteam.demo_agents import GuardedAgent, VulnerableAgent
from agent_redteam.runner import run_pack


def bench_agents() -> dict[str, dict[str, float]]:
    """Run the pack against both demo agents and return the scores."""
    out: dict[str, dict[str, float]] = {}
    for agent in (VulnerableAgent(), GuardedAgent()):
        report = run_pack(agent, "prompt-injection")
        out[report.agent_name] = {
            "attack_success_rate": report.attack_success_rate,
            "control_pass_rate": report.control_pass_rate,
            "breached": float(report.breached),
            "attacks": float(len(report.attacks)),
        }
    return out


def main() -> None:
    scores = bench_agents()
    for name, row in scores.items():
        print(
            f"{name}: attack success {row['attack_success_rate']:.2f} "
            f"({int(row['breached'])}/{int(row['attacks'])}), "
            f"control pass {row['control_pass_rate']:.2f}"
        )
    vulnerable = scores["vulnerable"]["attack_success_rate"]
    guarded = scores["guarded"]["attack_success_rate"]
    assert vulnerable > guarded, "demo gap missing: check pack labels or demo agents"


if __name__ == "__main__":
    main()
