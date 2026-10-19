"""Command line interface for agent-redteam.

Examples:
    agent-redteam list-packs
    agent-redteam run --agent guarded
    agent-redteam run --agent vulnerable --fail-on 0.5
    agent-redteam run --agent my_app.agent:handle --format json
    agent-redteam run --agent guarded --format html --output report.html
    agent-redteam run --pack-file ./my-pack.json --agent guarded

Exit codes for run: 0 when the gate passes, 1 when it fails, 2 for
usage errors. The gate fails when the attack success rate is above
--fail-on (default: any breach fails, so 0.0) or, when
--min-control-pass is given, when the control pass rate drops below
it. That makes run usable as a CI gate as-is. See docs/ci.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent_redteam.packs import list_packs, load_pack, load_pack_file, pack_description
from agent_redteam.report import gate_passed
from agent_redteam.runner import load_agent, run_cases


def _format_table(report) -> str:
    lines = [
        f"agent: {report.agent_name}  pack: {report.pack_name}",
        f"{'case':<18} {'category':<22} {'outcome':<16} marker",
    ]
    for r in report.results:
        lines.append(f"{r.case_id:<18} {r.category:<22} {r.outcome:<16} {r.matched_marker or ''}")
    lines.append(
        f"attack success rate: {report.attack_success_rate:.2f} "
        f"({report.breached}/{len(report.attacks)} breached), "
        f"control pass rate: {report.control_pass_rate:.2f}, "
        f"errors: {report.errors}"
    )
    return "\n".join(lines)


def _render(report, fmt: str, fail_on: float, min_control_pass: float | None) -> str:
    if fmt == "json":
        return json.dumps(report.to_dict(), indent=2)
    if fmt == "markdown":
        return report.to_markdown()
    if fmt == "html":
        return report.to_html(fail_on=fail_on, min_control_pass=min_control_pass)
    return _format_table(report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-redteam")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-packs", help="List built-in packs")

    show = sub.add_parser("show", help="List the cases in a pack")
    show.add_argument("--pack", default="prompt-injection")
    show.add_argument("--pack-file", default=None)

    run = sub.add_parser("run", help="Run a pack against an agent")
    run.add_argument("--pack", default="prompt-injection")
    run.add_argument("--pack-file", default=None)
    run.add_argument(
        "--agent", default="guarded", help="'vulnerable', 'guarded', or 'module:attribute'"
    )
    run.add_argument("--format", choices=("table", "json", "markdown", "html"), default="table")
    run.add_argument(
        "--output",
        default=None,
        help="Write the report to this file instead of stdout (any format)",
    )
    run.add_argument(
        "--fail-on",
        type=float,
        default=0.0,
        help="Fail (exit 1) when attack success rate is above this",
    )
    run.add_argument(
        "--min-control-pass",
        type=float,
        default=None,
        help="Also fail (exit 1) when control pass rate is below this",
    )

    args = parser.parse_args(argv)

    if args.command == "list-packs":
        for name in list_packs():
            print(f"{name}: {pack_description(name)}")
        return 0

    try:
        if getattr(args, "pack_file", None):
            cases = load_pack_file(args.pack_file)
            pack_name = args.pack_file
        else:
            cases = load_pack(args.pack)
            pack_name = args.pack
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.command == "show":
        for case in cases:
            print(f"{case.id:<18} {case.kind:<8} {case.category:<22} {case.prompt[:60]}")
        return 0

    try:
        agent = load_agent(args.agent)
    except Exception as exc:
        print(f"error: cannot load agent {args.agent!r}: {exc}", file=sys.stderr)
        return 2

    report = run_cases(agent, cases, pack_name=pack_name)
    report.agent_name = args.agent
    rendered = _render(report, args.format, args.fail_on, args.min_control_pass)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        print(f"report written to {args.output}")
    else:
        print(rendered)
    passed = gate_passed(report, fail_on=args.fail_on, min_control_pass=args.min_control_pass)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
