"""Fragmented instructions: run the third pack against both demo agents.

The cases split one instruction across several tool outputs. The
vulnerable agent assembles the pieces and obeys the result. The
guarded agent treats tool outputs as data and answers the user.

Run: python examples/fragmented_instruction.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agent_redteam import GuardedAgent, VulnerableAgent, run_pack  # noqa: E402


def main() -> None:
    for agent in (VulnerableAgent(), GuardedAgent()):
        report = run_pack(agent, "fragmented-instruction")
        print(
            f"{report.agent_name}: attack success {report.attack_success_rate:.2f} "
            f"({report.breached}/{len(report.attacks)}), "
            f"controls passed {report.control_pass_rate:.2f}"
        )
        for category, counts in sorted(report.by_category().items()):
            print(f"  {category}: {counts['breached']} breached of {counts['total']}")
    print(
        "Note: the cases show the agent the tool outputs as text in one "
        "turn. A live agent accumulates outputs across calls, which this "
        "harness does not observe. See docs/fragmented-instruction.md."
    )


if __name__ == "__main__":
    main()
