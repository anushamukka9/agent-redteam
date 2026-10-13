"""Attack packs: labeled case sets, loaded from JSON.

A pack is a JSON document with a name, a description, and a list of
cases. Built-in packs ship inside the package; you can also load your
own file with :func:`load_pack_file` and run it the same way. Writing
your own pack for your own agent's secrets is where this tool gets
useful: plant canaries only you know, and the markers stop being
generic.
"""

from __future__ import annotations

import json
from pathlib import Path

from agent_redteam.models import AttackCase

_PACKS_DIR = Path(__file__).resolve().parent / "packs"
_BUILTIN = {"prompt-injection": _PACKS_DIR / "prompt_injection.json"}


class PackNotFoundError(KeyError):
    """Raised when a pack name or file does not exist."""


def list_packs() -> list[str]:
    """Names of the built-in packs."""
    return sorted(_BUILTIN)


def _cases_from_doc(doc: dict) -> list[AttackCase]:
    name = str(doc.get("name", "custom"))
    cases = [AttackCase.from_dict(raw, pack=name) for raw in doc.get("cases", [])]
    ids = [c.id for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError(f"pack {name}: duplicate case ids")
    if not cases:
        raise ValueError(f"pack {name}: no cases")
    return cases


def load_pack(name: str) -> list[AttackCase]:
    """Load a built-in pack by name."""
    path = _BUILTIN.get(name)
    if path is None:
        raise PackNotFoundError(f"unknown pack {name!r}; built-in packs: {list_packs()}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    return _cases_from_doc(doc)


def load_pack_file(path: str | Path) -> list[AttackCase]:
    """Load a pack from a JSON file of your own."""
    target = Path(path)
    if not target.exists():
        raise PackNotFoundError(f"pack file not found: {target}")
    doc = json.loads(target.read_text(encoding="utf-8"))
    return _cases_from_doc(doc)


def pack_description(name: str) -> str:
    path = _BUILTIN.get(name)
    if path is None:
        raise PackNotFoundError(f"unknown pack {name!r}; built-in packs: {list_packs()}")
    doc = json.loads(path.read_text(encoding="utf-8"))
    return str(doc.get("description", ""))
