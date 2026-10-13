"""CLI tests."""

import json

from agent_redteam.cli import main


def test_list_packs(capsys):
    assert main(["list-packs"]) == 0
    out = capsys.readouterr().out
    assert "prompt-injection" in out


def test_show(capsys):
    assert main(["show", "--pack", "prompt-injection"]) == 0
    out = capsys.readouterr().out
    assert "pi-direct-01" in out
    assert "ctl-knowledge-01" in out


def test_run_guarded_passes_default_gate(capsys):
    assert main(["run", "--agent", "guarded"]) == 0
    out = capsys.readouterr().out
    assert "attack success rate: 0.00" in out


def test_run_vulnerable_fails_default_gate(capsys):
    assert main(["run", "--agent", "vulnerable"]) == 1
    out = capsys.readouterr().out
    assert "breached" in out


def test_run_vulnerable_with_lenient_gate(capsys):
    assert main(["run", "--agent", "vulnerable", "--fail-on", "1.0"]) == 0
    capsys.readouterr()


def test_run_json_format(capsys):
    assert main(["run", "--agent", "guarded", "--format", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["agent"] == "guarded"
    assert data["attacks"] == 16
    assert data["attack_success_rate"] == 0.0


def test_run_markdown_format(capsys):
    assert main(["run", "--agent", "guarded", "--format", "markdown"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# agent-redteam report")


def test_run_unknown_agent_is_usage_error(capsys):
    assert main(["run", "--agent", "no-such-agent"]) == 2
    assert "error" in capsys.readouterr().err


def test_run_unknown_pack_is_usage_error(capsys):
    assert main(["run", "--pack", "nope", "--agent", "guarded"]) == 2
    capsys.readouterr()
