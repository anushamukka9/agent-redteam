"""Quickstart: run the prompt-injection pack against both demo agents.

Run: python examples/quickstart.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agent_redteam import GuardedAgent, VulnerableAgent, run_pack  # noqa: E402


def main() -> None:
    for agent in (VulnerableAgent(), GuardedAgent()):
        report = run_pack(agent)
        print(
            f"{report.agent_name}: attack success {report.attack_success_rate:.2f} "
            f"({report.breached}/{len(report.attacks)}), "
            f"controls passed {report.control_pass_rate:.2f}"
        )
        for result in report.results:
            if result.outcome in ("breached", "control_failed", "error"):
                print(f"  {result.case_id}: {result.outcome} (marker: {result.matched_marker})")


if __name__ == "__main__":
    main()
