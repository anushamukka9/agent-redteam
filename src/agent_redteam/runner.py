"""The runner: point a pack at an agent, get a scored report.

An agent is anything reasonable: a plain callable ``prompt -> str``,
an object with a ``respond`` or ``run`` method, or an object that is
itself callable. Async agents are out of scope for v1; wrap them in a
sync shim that runs the event loop for one turn.
"""

from __future__ import annotations

import importlib
import time
from collections.abc import Callable

from agent_redteam.demo_agents import DEMO_AGENTS
from agent_redteam.judge import judge
from agent_redteam.models import AttackCase, AttackResult, RunReport
from agent_redteam.packs import load_pack

AgentCallable = Callable[[str], str]


def resolve_agent_callable(agent: object) -> AgentCallable:
    """Turn the shapes an agent can take into one callable."""
    if isinstance(agent, str):
        return load_agent(agent)
    respond = getattr(agent, "respond", None)
    if callable(respond):
        return lambda prompt: str(respond(prompt))
    run = getattr(agent, "run", None)
    if callable(run):
        return lambda prompt: str(run(prompt))
    if callable(agent):
        return lambda prompt: str(agent(prompt))
    raise TypeError(
        f"agent must be a callable, or have a respond() or run() method; got {type(agent).__name__}"
    )


def load_agent(spec: str) -> AgentCallable:
    """Load an agent by name or by ``module:attribute`` import path.

    Built-in names are ``vulnerable`` and ``guarded`` (the demo
    agents). Any other spec is imported: ``my_pkg.my_agent:handle``
    where the attribute is a prompt callable, an agent object, or an
    agent class (instantiated with no arguments).
    """
    if spec in DEMO_AGENTS:
        return resolve_agent_callable(DEMO_AGENTS[spec]())
    if ":" not in spec:
        raise ValueError(
            f"unknown agent {spec!r}; use 'vulnerable', 'guarded', "
            "or a 'module:attribute' import path"
        )
    module_name, _, attr = spec.partition(":")
    module = importlib.import_module(module_name)
    target = getattr(module, attr)
    if isinstance(target, type):
        target = target()
    elif callable(target) and not hasattr(target, "respond") and not hasattr(target, "run"):
        try:
            return resolve_agent_callable(target)
        except TypeError:
            target = target()
    return resolve_agent_callable(target)


def agent_name_of(agent: object) -> str:
    if isinstance(agent, str):
        return agent
    name = getattr(agent, "name", None)
    if name:
        return str(name)
    func_name = getattr(agent, "__name__", None)
    if func_name:
        return str(func_name)
    return type(agent).__name__


def run_case(agent: object, case: AttackCase) -> AttackResult:
    """Run one case. Agent exceptions become error results, not crashes."""
    call = resolve_agent_callable(agent)
    start = time.perf_counter()
    try:
        output = call(case.prompt)
    except Exception as exc:  # the harness reports, it does not die
        latency = (time.perf_counter() - start) * 1000.0
        return AttackResult(
            case_id=case.id,
            kind=case.kind,
            category=case.category,
            outcome="error",
            latency_ms=latency,
            error=f"{type(exc).__name__}: {exc}",
        )
    latency = (time.perf_counter() - start) * 1000.0
    return judge(case, output, latency_ms=latency)


def run_cases(agent: object, cases: list[AttackCase], pack_name: str = "custom") -> RunReport:
    """Run a list of cases and aggregate the report."""
    call = resolve_agent_callable(agent)
    results = []
    for case in cases:
        start = time.perf_counter()
        try:
            output = call(case.prompt)
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000.0
            results.append(
                AttackResult(
                    case_id=case.id,
                    kind=case.kind,
                    category=case.category,
                    outcome="error",
                    latency_ms=latency,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )
            continue
        latency = (time.perf_counter() - start) * 1000.0
        results.append(judge(case, output, latency_ms=latency))
    return RunReport(agent_name=agent_name_of(agent), pack_name=pack_name, results=results)


def run_pack(agent: object, pack_name: str = "prompt-injection") -> RunReport:
    """Run a built-in pack by name."""
    return run_cases(agent, load_pack(pack_name), pack_name=pack_name)
