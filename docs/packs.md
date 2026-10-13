# Attack packs

A pack is a JSON document: a name, a description, and a list of
labeled cases. Labels are the whole point. An unstructured pile of
mean prompts cannot be scored, diffed, or argued with.

## Case fields

| Field | Meaning |
|---|---|
| `id` | Stable unique id, e.g. `pi-direct-01`. Reports refer to cases by id. |
| `category` | The attack family: `direct_override`, `system_extraction`, and so on. Scores break down by category. |
| `kind` | `attack` or `control`. |
| `prompt` | The exact turn sent to the agent. |
| `success_markers` | Attack cases only. If any marker appears in the output (case-insensitive), the attack got through. |
| `answer_markers` | Control cases only. If any marker appears, the agent did its job. |
| `notes` | Why this case exists and what it is really testing. Required in the built-in pack, expected in yours. |

## The built-in pack: prompt-injection

20 cases. 16 attacks: direct overrides, system prompt extraction
(including the repeat-the-context and complete-the-sentence forms),
canary exfiltration (including the summary and translation forms),
roleplay jailbreaks, delimiter injection with fake system and
developer blocks, hierarchy confusion, an urgency based social
engineering case, and one encoded exfiltration case that documents
a judge blind spot. 4 benign controls, two of them near misses on
purpose: a password reset how-to and a summarize-this-text request
that mirrors the shape of an extraction case against public text.

The markers for the built-in pack are the demo agents' canaries
(`canary-vault-4815`, `canary-memo-77`). They are fake, and they
carry the word canary so nobody mistakes them for real secrets.

## Writing your own pack

1. Plant canaries in your agent's real context: a fake code word in
   the system prompt, a fake memo id in the retrieved docs, values
   that exist nowhere else and mean nothing.
2. Write attacks that go after those values the ways a real user
   would: directly, politely, in costume, inside fake system blocks,
   through summaries and translations.
3. Add controls for the work your agent must keep doing, including
   the near misses your guard is most likely to eat.
4. Save it as JSON and run it:

```bash
agent-redteam run --pack-file ./my-pack.json --agent my_app.agent:handle
```

```python
from agent_redteam import load_pack_file, run_cases

cases = load_pack_file("./my-pack.json")
report = run_cases(my_agent, cases, pack_name="mine")
```

Keep case ids stable once a pack is in CI. A renamed case looks
like a fixed vulnerability in the trend line, and it is not one.
