"""Benchmarks for agent-redteam. Run: python benchmarks/bench.py [--quick]

Runs both built-in packs against both demo agents, reports the
attack success and control pass rates per pack, and measures harness
throughput on the guarded demo agent. Writes benchmarks/results.md.
--quick does not write results.md (used for smoke checks).
"""

import argparse
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agent_redteam import GuardedAgent, VulnerableAgent, list_packs, run_pack  # noqa: E402

HERE = Path(__file__).resolve().parent
PACK_NOTES = {
    "prompt-injection": (
        "The vulnerable agent's one held case is pi-indirect-02 (encoded "
        "exfiltration): it leaks the plain code, the marker is the base64 "
        "form, so the judge scores it held. That miss is deliberate and "
        "documented in docs/limitations.md."
    ),
    "tool-poisoning": (
        "The vulnerable agent breaches every tool-poisoning case: it "
        "treats tool descriptions as trusted instructions, including a "
        "description changed after approval and an instruction split "
        "into fragments across tools. The guarded agent treats tool "
        "descriptions as data and holds every case while passing every "
        "control."
    ),
}


def bench_throughput(iterations: int = 200) -> float:
    agent = GuardedAgent()
    start = time.perf_counter()
    for _ in range(iterations):
        run_pack(agent)
    elapsed = time.perf_counter() - start
    return iterations / elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    all_rows = {}
    for pack_name in list_packs():
        rows = []
        for agent in (VulnerableAgent(), GuardedAgent()):
            report = run_pack(agent, pack_name)
            rows.append(
                (
                    report.agent_name,
                    report.attack_success_rate,
                    report.breached,
                    len(report.attacks),
                    report.control_pass_rate,
                )
            )
        all_rows[pack_name] = rows
        for name, asr, breached, total, cpr in rows:
            print(f"{pack_name} / {name}: attack success {asr:.2f} ({breached}/{total}), "
                  f"controls {cpr:.2f}")
    runs_per_sec = bench_throughput(50 if args.quick else 200)
    print(f"harness throughput (guarded demo, prompt-injection): {runs_per_sec:,.0f} pack runs/sec")

    if args.quick:
        return
    lines = [
        "# Benchmark results",
        "",
        f"Machine: {platform.platform()}, Python {platform.python_version()}.",
        "Demo agents only. These numbers validate the harness and the pack",
        "labels. They say nothing about your agent until you run it.",
        "",
    ]
    for pack_name, rows in all_rows.items():
        attacks = rows[0][3]
        lines += [
            f"## Pack: {pack_name} ({attacks} attacks, 4 controls)",
            "",
            "| Agent | Attack success rate | Breached | Control pass rate |",
            "|---|---|---|---|",
        ]
        for name, asr, breached, total, cpr in rows:
            lines.append(f"| {name} | {asr:.2f} | {breached}/{total} | {cpr:.2f} |")
        lines += ["", PACK_NOTES.get(pack_name, ""), ""]
    lines += [
        f"Harness throughput on the guarded demo agent: {runs_per_sec:,.0f} "
        "full pack runs per second. With a real agent, the agent's own "
        "latency dominates and this number stops mattering.",
        "",
    ]
    (HERE / "results.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote benchmarks/results.md")


if __name__ == "__main__":
    main()
