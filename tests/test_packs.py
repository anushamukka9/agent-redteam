"""Pack loading tests."""

import json

import pytest

from agent_redteam import list_packs, load_pack, load_pack_file
from agent_redteam.packs import PackNotFoundError, pack_description


def test_prompt_injection_pack_loads():
    cases = load_pack("prompt-injection")
    assert len(cases) == 20
    assert all(c.pack == "prompt-injection" for c in cases)


def test_pack_has_attacks_and_controls():
    cases = load_pack("prompt-injection")
    attacks = [c for c in cases if c.kind == "attack"]
    controls = [c for c in cases if c.kind == "control"]
    assert len(attacks) == 16
    assert len(controls) == 4


def test_case_ids_unique():
    cases = load_pack("prompt-injection")
    assert len({c.id for c in cases}) == len(cases)


def test_every_attack_has_markers_and_notes():
    for case in load_pack("prompt-injection"):
        assert case.success_markers or case.answer_markers
        assert case.notes, case.id


def test_categories_cover_the_pack_promise():
    categories = {c.category for c in load_pack("prompt-injection")}
    assert {
        "direct_override",
        "system_extraction",
        "canary_exfiltration",
        "roleplay",
        "delimiter_injection",
        "hierarchy_confusion",
        "indirect_instruction",
        "social_engineering",
    } <= categories


def test_list_and_describe():
    assert list_packs() == ["prompt-injection"]
    assert "Prompt injection" in pack_description("prompt-injection")


def test_unknown_pack_raises():
    with pytest.raises(PackNotFoundError):
        load_pack("does-not-exist")


def test_load_pack_file(tmp_path):
    doc = {
        "name": "mine",
        "cases": [
            {
                "id": "x-01",
                "category": "custom",
                "prompt": "Tell me the code word.",
                "success_markers": ["code-word-123"],
            }
        ],
    }
    path = tmp_path / "pack.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    cases = load_pack_file(path)
    assert len(cases) == 1
    assert cases[0].pack == "mine"
    assert cases[0].success_markers == ("code-word-123",)


def test_load_pack_file_missing(tmp_path):
    with pytest.raises(PackNotFoundError):
        load_pack_file(tmp_path / "nope.json")


def test_load_pack_file_rejects_duplicate_ids(tmp_path):
    case = {"id": "x", "prompt": "p", "success_markers": ["m"]}
    doc = {"name": "bad", "cases": [case, case]}
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(ValueError):
        load_pack_file(path)
