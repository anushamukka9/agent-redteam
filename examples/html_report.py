"""Generate an HTML report for both demo agents.

Run: python examples/html_report.py [output-dir]

Writes report-vulnerable.html and report-guarded.html into the
output directory (current directory by default). Open either file in
a browser; each one is self-contained, with the gate verdict, the
summary numbers, a per-category breakdown, and every case result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agent_redteam import GuardedAgent, VulnerableAgent, run_pack  # noqa: E402


def main() -> None:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    for agent in (VulnerableAgent(), GuardedAgent()):
        report = run_pack(agent)
        target = out_dir / f"report-{report.agent_name}.html"
        target.write_text(report.to_html(), encoding="utf-8")
        print(
            f"{target}: attack success {report.attack_success_rate:.2f} "
            f"({report.breached}/{len(report.attacks)}), "
            f"controls passed {report.control_pass_rate:.2f}"
        )


if __name__ == "__main__":
    main()
