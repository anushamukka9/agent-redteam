"""Benchmark: both built-in packs against both demo agents.

Run with: python -m agent_redteam.benchmark

This is the CI smoke check and the source of the numbers in the
README. It measures two toy agents, not yours. Its job is to prove
the harness runs, the packs are labeled correctly, and the gap
between a careless agent and a guarded one shows up in the score
on every pack, not just the first one.
"""

from __future__ import annotations

from agent_redteam.demo_agents import GuardedAgent, VulnerableAgent
from agent_redteam.packs import list_packs
from agent_redteam.runner import run_pack


def bench_agents(pack_name: str = "prompt-injection") -> dict[str, dict[str, float]]:
    """Run one pack against both demo agents and return the scores."""
    out: dict[str, dict[str, float]] = {}
    for agent in (VulnerableAgent(), GuardedAgent()):
        report = run_pack(agent, pack_name)
        out[report.agent_name] = {
            "attack_success_rate": report.attack_success_rate,
            "control_pass_rate": report.control_pass_rate,
            "breached": float(report.breached),
            "attacks": float(len(report.attacks)),
        }
    return out


def bench_all_packs() -> dict[str, dict[str, dict[str, float]]]:
    """Run every built-in pack against both demo agents."""
    return {name: bench_agents(name) for name in list_packs()}


def main() -> None:
    for pack_name, scores in bench_all_packs().items():
        for name, row in scores.items():
            print(
                f"{pack_name} / {name}: attack success {row['attack_success_rate']:.2f} "
                f"({int(row['breached'])}/{int(row['attacks'])}), "
                f"control pass {row['control_pass_rate']:.2f}"
            )
        vulnerable = scores["vulnerable"]["attack_success_rate"]
        guarded = scores["guarded"]["attack_success_rate"]
        assert vulnerable > guarded, f"demo gap missing on {pack_name}: check labels or agents"


if __name__ == "__main__":
    main()
