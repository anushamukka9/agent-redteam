# Quickstart

## Install

```bash
pip install agent-redteam
```

## See a run in thirty seconds

Two demo agents ship in the box, both built around a fictional store
support agent whose system prompt carries planted canary values.

```bash
agent-redteam run --agent vulnerable
agent-redteam run --agent guarded
```

The vulnerable agent breaches on 15 of 16 attacks. The guarded agent
holds all 16 and still passes every benign control. Exit code is 1
when the attack success rate is above `--fail-on` (default 0.0), so
the vulnerable run fails and the guarded run passes, exactly like a
CI gate.

The second pack works the same way, against poisoned tool
descriptions instead of poisoned user turns:

```bash
agent-redteam run --pack tool-poisoning --agent vulnerable
agent-redteam run --pack tool-poisoning --agent guarded
```

There the vulnerable agent breaches all 16, because it treats tool
descriptions as trusted instructions. The guarded agent holds all
16 and still passes the controls with legitimate descriptions.

## Run it against your agent

Your agent can be a function, an object with `respond` or `run`, or
a class. From Python:

```python
from agent_redteam import run_pack

def my_agent(prompt: str) -> str:
    ...  # call your model, your framework, whatever you run

report = run_pack(my_agent)
print(report.attack_success_rate, report.control_pass_rate)
print(report.to_markdown())
```

From the CLI, point at an import path:

```bash
agent-redteam run --agent my_app.agent:handle --format json
agent-redteam run --agent my_app.agent:handle --fail-on 0.2
```

The attribute after the colon can be a prompt callable, an agent
object, or an agent class (it is instantiated with no arguments).

## Read the score

- Attack success rate: share of attack cases whose success marker
  appeared in the output. Lower is safer. This is the number the
  `--fail-on` gate uses.
- Control pass rate: share of benign controls the agent still
  answered. If this drops while attacks improve, your guard is
  eating real work.
- Errors: agent exceptions are recorded as error results with the
  message attached. An erroring agent is not a passing agent; the
  report keeps them separate so you have to look.

## Then write your own pack

The built-in pack attacks a fictional store agent. The run that
matters attacks yours, with canaries planted in your context. See
[packs.md](packs.md) for the pack format.
