# Contributing to agent-redteam

Thanks for considering a contribution. This is a small, focused
library and we want to keep it that way.

## What fits here

- New attack cases with labels and notes: the case id, the category,
  what marker proves it worked, and a sentence on what it is really
  testing. Unlabeled prompts do not fit; labels are the product.
- New packs for attack families the built-in pack does not cover,
  with benign controls in the same pack, including near misses.
- Judge and runner improvements that stay deterministic. A smarter
  judge that gives different verdicts on different days is a
  regression, not an improvement.
- Docs, examples, and benchmark additions.

## What does not fit

- A hosted service, a dashboard, or anything that phones home. The
  harness runs where your agent runs, on purpose.
- Dependencies in the core. It is stdlib-only and it should stay
  that way.
- Cases whose markers are real secrets or real provider key shapes.
  Plant canaries: fake values with the word canary in them.

## How to contribute

1. Fork the repo and create a branch: `git checkout -b fix/short-desc`.
2. Add your change plus tests. Case work needs a demo-agent result:
   show which demo agent the case breaches or holds against, and
   why that is the right label.
3. Run the gates: `pytest` and `ruff check` / `ruff format --check`.
   Both must be clean.
4. Write your feature's limitations honestly. Every part of this
   library documents what it cannot do. That is a requirement, not
   a suggestion.
5. Open a PR with a short description: what it does, why, and the
   test evidence. Keep the human voice: plain sentences, no hype.

## A note on example secrets

GitHub's secret scanner blocks pushes containing real provider key
formats, even obviously fake ones. If a test fixture or example
needs a secret-shaped value, keep it clearly fake (`canary-...`
values, or a value built in code) and never in a real provider's
exact format. Do not disable push protection to land a fixture.

## Style

- Python 3.10+, `src/` layout, type hints on public APIs.
- Line length 100, ruff-enforced.
- No em-dashes anywhere. This is a hard rule for this repo.
- Commit messages in imperative mood: `feat: add tool-poisoning pack`,
  not `added tool-poisoning pack`.
