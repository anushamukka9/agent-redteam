"""Tool poisoning: run the second pack against both demo agents.

The cases present a poisoned MCP tool description next to a plain
user request. The vulnerable agent treats the description as orders
from a trusted peer. The guarded agent treats it as data.

Run: python examples/tool_poisoning.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agent_redteam import GuardedAgent, VulnerableAgent, run_pack  # noqa: E402


def main() -> None:
    for agent in (VulnerableAgent(), GuardedAgent()):
        report = run_pack(agent, "tool-poisoning")
        print(
            f"{report.agent_name}: attack success {report.attack_success_rate:.2f} "
            f"({report.breached}/{len(report.attacks)}), "
            f"controls passed {report.control_pass_rate:.2f}"
        )
        for category, counts in sorted(report.by_category().items()):
            print(f"  {category}: {counts['breached']} breached of {counts['total']}")
    print(
        "Note: the cases show the agent the poisoned description as text. "
        "A live MCP connection adds tool calls on top, which this harness "
        "does not observe. See docs/limitations.md."
    )


if __name__ == "__main__":
    main()
