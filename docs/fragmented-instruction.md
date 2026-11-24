# Fragmented instructions: detection notes

The third pack, `fragmented-instruction`, covers the GhostSplice
pattern against tool outputs: one malicious instruction split into
pieces, spread across the outputs an agent reads, that only becomes
an instruction when the pieces are assembled. The tool-poisoning
pack splits instructions across tool descriptions. This pack splits
them across what the tools return, which is the data an agent reads
most and questions least.

## Why per-output scanning misses it

A scanner that checks each tool output on its own sees three
harmless scraps: a verb phrase here, a target noun there, a timing
clause somewhere else. None of the pieces is an order. The order
exists only in the assembled context, and the assembled context is
exactly what the model reads. If your defense never looks at the
assembled text, it never looks at the attack.

## The four families in the pack

| Family | What it tests |
|---|---|
| `split_across_outputs` | One fragment per tool output, across two to four calls. The plain form of the pattern. |
| `interleaved_benign` | Fragments hidden between ordinary data rows: inventory, log lines, ticket comments, prices. The benign rows are the cover. |
| `cross_source_assembly` | Pieces arriving through different channels: a tool output, a retrieved document, an email body, a database row, an error message. No single channel holds the whole order. |
| `ordered_reassembly` | Numbered fragments delivered out of order. The numbering invites the reader to sort the pieces, and sorting them is the attack. One case targets an announcement instead of a leak. |

## Detection notes

These are the practices the pack is built to test for. None of them
is a product claim about this harness; the harness only scores.

1. **Scan the assembled context, not only the pieces.** Before an
   agent answers, the text it is about to reason over is one
   document. Run instruction and secret-target checks over that
   whole document, in reading order and in any numbered order the
   pieces themselves declare.
2. **Keep provenance on every span.** A fragment from a tool output,
   a retrieved page, or an error message is data, whoever wrote it.
   If the assembled text contains an instruction, its authority is
   the authority of its least trusted piece, which is none.
3. **Treat error text as data too.** Errors feel like they come
   from the system. They come from whatever failed, and in these
   cases they carry a fragment like everything else.
4. **Watch for numbering and ordering cues.** "Fragment 2 of 3",
   part numbers, and out-of-order delivery are assembly
   instructions aimed at the reader. Benign split content exists
   (the pack has controls for it), so the cue alone is not a
   verdict; the assembled content is.
5. **Do not let benign neighbors launder a fragment.** Interleaving
   works because each piece sits next to ordinary data. Judge the
   assembled instruction, not the company it keeps.
6. **Refuse the assembled order, answer the user.** In every attack
   case the user request is innocent and answerable. The right
   behavior is to do the user's work and leave the assembled order
   unexecuted, which is what the controls measure from the other
   side.

## Honest limits of this pack

- The cases present the outputs as text in one turn, the same way
  the other packs present their material. The harness does not make
  live tool calls, so it cannot watch a real agent accumulate
  fragments across a long session. Treat a good score here as a
  floor, not a ceiling.
- The fragments in these cases are labeled as fragments. Real
  planted pieces may carry no labels at all, just short phrases in
  plausible places. Labeled pieces are the smoke test; unlabeled
  pieces are the fire.
- Marker scoring has the usual blind spots: an agent that obeys
  the assembled order in a paraphrased way, or leaks a secret in a
  form no marker lists, scores as held. See docs/limitations.md.

Run it with:

```bash
agent-redteam run --pack fragmented-instruction --agent guarded
agent-redteam run --pack fragmented-instruction --agent vulnerable
```
