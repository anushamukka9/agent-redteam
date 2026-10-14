"""agent-redteam: adversarial test harness for AI agent apps.

Point it at your agent, it runs labeled attack packs and scores how
many attacks got through, plus whether benign controls still pass.

Quickstart:
    from agent_redteam import run_pack, GuardedAgent

    report = run_pack(GuardedAgent())
    print(report.attack_success_rate, report.control_pass_rate)
"""

from agent_redteam.demo_agents import GuardedAgent, VulnerableAgent
from agent_redteam.judge import judge
from agent_redteam.models import AttackCase, AttackResult, RunReport
from agent_redteam.packs import (
    PackNotFoundError,
    list_packs,
    load_pack,
    load_pack_file,
)
from agent_redteam.runner import load_agent, run_case, run_cases, run_pack

__version__ = "0.2.0"

__all__ = [
    "AttackCase",
    "AttackResult",
    "GuardedAgent",
    "PackNotFoundError",
    "RunReport",
    "VulnerableAgent",
    "judge",
    "list_packs",
    "load_agent",
    "load_pack",
    "load_pack_file",
    "run_case",
    "run_cases",
    "run_pack",
]
