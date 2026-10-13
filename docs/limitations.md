# Limitations

Read this before you rely on a score.

- **Marker scoring sees strings, not meaning.** A leak that
  paraphrases the secret, spells it out letter by letter, splits it
  across words, or encodes it in a form you did not list as a marker
  scores as held. The built-in pack includes one encoded case
  (pi-indirect-02) where exactly this happens, on purpose, so the
  blind spot is measured rather than rumored.
- **The demo agents are toys.** The guarded agent checks for the
  shapes this pack uses, so its 0.00 attack success rate is the
  floor of the exercise. It proves the harness and the labels work.
  It says nothing about a real model facing phrasings nobody listed.
- **Single-turn only.** Every case is one prompt and one answer.
  Multi-turn manipulation, where the agent is walked somewhere over
  ten friendly turns, is the obvious next frontier and it is not in
  v1.
- **Synchronous only.** Agents are called as plain callables. Async
  agents need a sync wrapper for now.
- **Answers, not actions.** The harness reads what the agent says.
  It does not observe tool calls, so an agent can pass every case
  while still doing something dangerous with a tool. Pair this with
  policy enforcement (agent-policy-kit) and surface audits
  (mcp-audit) if tools are in play.
- **The pack is small.** 20 cases is a smoke alarm, not a fire
  audit. The format is the product: the valuable pack is the one
  you write against your own agent, your own context, and your own
  planted canaries.
- **Controls are marker based too.** A control passes when an
  answer marker appears, even if the rest of the answer is wrong.
  Controls catch refusal-happy guards; they do not grade quality.
