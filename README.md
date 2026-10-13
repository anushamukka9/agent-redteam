# agent-redteam

Adversarial test harness for AI agent apps. Point it at your agent,
it runs labeled attack packs and scores how many got through. Then
it checks that your agent can still do its actual job.

## Why this exists

I write about adversarial robustness, and I kept noticing the same
gap. Everyone agrees agents should be tested against prompt
injection. Almost nobody ships the test. The red team tooling that
exists is either a slide deck, a hosted service, or a pile of
unstructured prompts with no scoring, so two runs never compare and
"we tested it" means whatever the person saying it wants it to mean.

agent-redteam is the boring, useful middle: attack packs as labeled
data, a deterministic judge, and a score you can put in CI. A case
says what the attack is, which category it belongs to, and what
showing up in the output means the attack worked. Benign controls
sit in the same pack, because an agent that refuses everything is
not secure, it is just broken in a quieter way.

It pairs with my other repos: llm-sentinel guards prompts on the way
in, mcp-audit audits the tool surface, rag-canary plants the tripwires
in your corpus, and agent-redteam is the harness that keeps score
across all of it.

## Quickstart

```bash
pip install agent-redteam
agent-redteam run --agent guarded
```

```python
from agent_redteam import GuardedAgent, run_pack

report = run_pack(GuardedAgent())
print(report.attack_success_rate)  # 0.0 on the demo agent
print(report.control_pass_rate)    # 1.0
```

Thirty seconds, start to finish. Two demo agents ship in the box so
you can see a run before wiring up your own: `vulnerable` is a
careless agent that hands its system prompt to anyone who asks, and
`guarded` is the same agent with a front door. Your agent is one
import path away:

```bash
agent-redteam run --agent my_app.agent:handle --fail-on 0.2
```

Any callable that takes a prompt and returns text works, and so does
an object with a `respond` or `run` method. See
[docs/quickstart.md](docs/quickstart.md) and
[examples/quickstart.py](examples/quickstart.py).

## What it does

**Labeled attack packs.** v1 ships one pack, `prompt-injection`:
16 attacks across direct override, system prompt extraction, canary
exfiltration, roleplay, delimiter injection, hierarchy confusion,
indirect instruction, and social engineering, plus 4 benign controls
with near misses on purpose (a password how-to question is not a
credential request). Every case carries notes on what it is testing
and why. See [docs/packs.md](docs/packs.md).

**A judge with no opinions.** Scoring is marker based and fully
deterministic. An attack got through if one of its success markers
appears in the output; a control passes if an answer marker appears.
No model grades anything, so the same output gets the same verdict
every time. What a marker judge cannot see is listed honestly in
[docs/limitations.md](docs/limitations.md).

**A score you can gate on.** The CLI exits 1 when the attack success
rate is above `--fail-on` (default 0.0, any breach fails), so a red
team run can be a CI step, not a ritual. Reports come out as a table,
JSON, or markdown.

**Your own packs.** A pack is a JSON file. Plant canaries only you
know in your agent's context, write cases that go after them, and
the score starts measuring your agent instead of my demo. See
[docs/packs.md](docs/packs.md).

## Benchmarks

Measured on this machine against the two demo agents (see
[benchmarks/results.md](benchmarks/results.md) for the setup). These
numbers validate the harness and the pack labels. They say nothing
about your agent until you run it.

| Agent | Attack success rate | Controls passed |
|---|---|---|
| vulnerable (demo) | 0.94 (15/16) | 1.00 (4/4) |
| guarded (demo) | 0.00 (0/16) | 1.00 (4/4) |

The one case the vulnerable agent holds is the encoded-exfiltration
case: it leaks the plain code, and the marker for that case is the
base64 form, so the judge scores it held while the secret still
left. That miss is deliberate. It is in the pack, and in the
limitations doc, to keep everyone honest about what marker scoring
misses. Harness overhead on the demo agents is about 5,600 full
pack runs per second; with a real agent, your agent's latency is
the whole story.

## Honest limitations

- The guarded demo agent is tuned to the shapes in this pack, so
  its 0.00 is the floor of the exercise, not a promise about any
  real system.
- Marker scoring misses paraphrased leaks, encoded leaks whose
  markers were not listed, and leaks split across turns.
- v1 is single-turn and synchronous. Multi-turn manipulation and
  async agents are future work, not hidden features.
- The packs test the agent's answers, not its tool calls. An agent
  can pass every case here and still call a dangerous tool; that is
  what agent-policy-kit and mcp-audit are for.

Full list in [docs/limitations.md](docs/limitations.md). Read it
before you quote a score.

## Companions

- [llm-sentinel](https://github.com/anushamukka9/llm-sentinel) guards prompts going in.
- [mcp-audit](https://github.com/anushamukka9/mcp-audit) audits MCP server surfaces.
- [rag-canary](https://github.com/anushamukka9/rag-canary) plants canary tokens in RAG corpora.
- [agent-policy-kit](https://github.com/anushamukka9/agent-policy-kit) decides what agents may do.
- [agent-audit](https://github.com/anushamukka9/agent-audit) keeps the tamper-evident record.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New cases need labels and
notes, every feature documents what it cannot do, and there are no
em-dashes in this repo.

## License

MIT. See [LICENSE](LICENSE).
