"""Core data types for agent-redteam.

An AttackCase is one labeled probe. A case is either an ``attack`` (the
agent should refuse or deflect it; the attack got through if a success
marker appears in the output) or a ``control`` (a benign request the
agent should still answer; the control passes if an answer marker
appears). Controls matter: an agent that refuses everything scores
perfectly on attacks and is still useless.
"""

from __future__ import annotations

from dataclasses import dataclass, field

KINDS = ("attack", "control")
OUTCOMES = ("breached", "held", "control_passed", "control_failed", "error")


@dataclass(frozen=True)
class AttackCase:
    """One labeled probe in a pack."""

    id: str
    pack: str
    category: str
    prompt: str
    kind: str = "attack"
    success_markers: tuple[str, ...] = ()
    answer_markers: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"case {self.id}: kind must be one of {KINDS}")
        if self.kind == "attack" and not self.success_markers:
            raise ValueError(f"case {self.id}: attack cases need success_markers")
        if self.kind == "control" and not self.answer_markers:
            raise ValueError(f"case {self.id}: control cases need answer_markers")

    @classmethod
    def from_dict(cls, data: dict, pack: str = "") -> AttackCase:
        return cls(
            id=str(data["id"]),
            pack=str(data.get("pack", pack)),
            category=str(data.get("category", "uncategorized")),
            prompt=str(data["prompt"]),
            kind=str(data.get("kind", "attack")),
            success_markers=tuple(data.get("success_markers", ())),
            answer_markers=tuple(data.get("answer_markers", ())),
            notes=str(data.get("notes", "")),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pack": self.pack,
            "category": self.category,
            "kind": self.kind,
            "prompt": self.prompt,
            "success_markers": list(self.success_markers),
            "answer_markers": list(self.answer_markers),
            "notes": self.notes,
        }


@dataclass
class AttackResult:
    """The judged outcome of running one case against one agent."""

    case_id: str
    kind: str
    category: str
    outcome: str
    latency_ms: float
    output_preview: str = ""
    matched_marker: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"unknown outcome {self.outcome!r}")

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "kind": self.kind,
            "category": self.category,
            "outcome": self.outcome,
            "latency_ms": round(self.latency_ms, 3),
            "matched_marker": self.matched_marker,
            "output_preview": self.output_preview,
            "error": self.error,
        }


@dataclass
class RunReport:
    """Aggregate score for one agent over one pack (or set of cases)."""

    agent_name: str
    pack_name: str
    results: list[AttackResult] = field(default_factory=list)

    @property
    def attacks(self) -> list[AttackResult]:
        return [r for r in self.results if r.kind == "attack"]

    @property
    def controls(self) -> list[AttackResult]:
        return [r for r in self.results if r.kind == "control"]

    @property
    def breached(self) -> int:
        return sum(1 for r in self.attacks if r.outcome == "breached")

    @property
    def errors(self) -> int:
        return sum(1 for r in self.results if r.outcome == "error")

    @property
    def attack_success_rate(self) -> float:
        """Share of attack cases that got through. Lower is safer."""
        total = len(self.attacks)
        return self.breached / total if total else 0.0

    @property
    def control_pass_rate(self) -> float:
        """Share of benign controls the agent still answered. Higher is better."""
        total = len(self.controls)
        if not total:
            return 1.0
        passed = sum(1 for r in self.controls if r.outcome == "control_passed")
        return passed / total

    def by_category(self) -> dict[str, dict[str, int]]:
        """Per-category counts: total and breached attacks, passed controls."""
        out: dict[str, dict[str, int]] = {}
        for r in self.results:
            bucket = out.setdefault(r.category, {"total": 0, "breached": 0, "control_passed": 0})
            bucket["total"] += 1
            if r.outcome == "breached":
                bucket["breached"] += 1
            if r.outcome == "control_passed":
                bucket["control_passed"] += 1
        return out

    def to_dict(self) -> dict:
        return {
            "agent": self.agent_name,
            "pack": self.pack_name,
            "cases": len(self.results),
            "attacks": len(self.attacks),
            "breached": self.breached,
            "attack_success_rate": round(self.attack_success_rate, 4),
            "controls": len(self.controls),
            "control_pass_rate": round(self.control_pass_rate, 4),
            "errors": self.errors,
            "by_category": self.by_category(),
            "results": [r.to_dict() for r in self.results],
        }

    def to_html(self, fail_on: float = 0.0, min_control_pass: float | None = None) -> str:
        """Render this report as one self-contained HTML page.

        See agent_redteam.report for why every agent-controlled value
        on the page is escaped.
        """
        from agent_redteam.report import render_html

        return render_html(self, fail_on=fail_on, min_control_pass=min_control_pass)

    def to_markdown(self) -> str:
        lines = [
            f"# agent-redteam report: {self.agent_name} on {self.pack_name}",
            "",
            f"- Cases run: {len(self.results)} "
            f"({len(self.attacks)} attacks, {len(self.controls)} controls)",
            f"- Attacks that got through: {self.breached} "
            f"(attack success rate {self.attack_success_rate:.2f})",
            f"- Controls passed: {self.control_pass_rate:.2f}",
            f"- Agent errors: {self.errors}",
            "",
            "| Case | Category | Outcome | Matched marker |",
            "|---|---|---|---|",
        ]
        for r in self.results:
            marker = r.matched_marker or ""
            lines.append(f"| {r.case_id} | {r.category} | {r.outcome} | {marker} |")
        lines.append("")
        return "\n".join(lines)
