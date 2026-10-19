# Reports and the CI gate

A red team run nobody looks at is a ritual. Two things make it real:
a report a human will actually open, and an exit code a build cannot
ignore.

## The HTML report

```bash
agent-redteam run --agent my_app.agent:handle --format html --output report.html
```

One command, one file. The page is self-contained: inline CSS, no
JavaScript, no external assets, nothing fetched, so it renders the
same attached to a CI run, dropped in a ticket, or opened off a USB
stick. It carries:

- The gate verdict (PASS or FAIL) and the exact gate it was judged
  against.
- Summary cards: attack success rate, how many attacks got through,
  control pass rate, and the error count.
- A per-category breakdown, which is where the useful arguments
  happen.
- Every case result: outcome, matched marker, latency, and a preview
  of what the agent actually said.

From Python, the same page is `report.to_html()`.

One design point worth knowing: agent output is untrusted text. A
breached agent may hand back markup on purpose, so every value that
came from the agent, the pack, or the command line is HTML-escaped
before it lands on the page. The report shows what the agent said; it
never lets the agent write the report. Previews are also capped at
200 characters by the judge, so the page stays a report, not a dump.

The other formats still exist: `--format table` for the terminal,
`--format json` for machines, `--format markdown` for pasting into a
pull request. `--output` works with any of them.

## The gate

`agent-redteam run` exits 1 when the gate fails:

- Attack side: the attack success rate is above `--fail-on`.
  Default 0.0, any breach fails.
- Control side, when you ask for it: the control pass rate is below
  `--min-control-pass`. This catches the quiet failure where a new
  guard refuses everything, aces the attacks, and breaks the agent
  for real users.

Writing a report with `--output` never changes the exit code. A
failing run still writes its report, because that is the run you
need to read.

Raise `--fail-on` while you burn down a backlog if you must, and put
the number in the commit message when you do, so the relaxation is
on the record.

## GitHub Actions example

`examples/ci/github-actions-redteam.yml` is a copy-paste workflow:
it installs the tool, runs the prompt-injection pack as a gate
against your agent, and uploads the HTML report as a build artifact
with `if: always()`, so the report is attached even when (especially
when) the gate fails. Point `--agent` at your agent's import path
and copy the file to `.github/workflows/redteam.yml` in your repo.

The same shape works on any CI system: run the command, keep the
exit code, publish `redteam-report.html` as an artifact.
