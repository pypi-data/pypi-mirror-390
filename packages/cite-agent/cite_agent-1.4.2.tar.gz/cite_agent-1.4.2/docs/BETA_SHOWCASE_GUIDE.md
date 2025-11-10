# Beta Showcase Guide

Use this quick guide when you need to demonstrate Cite Agent during the private beta.

## 1. Regenerate Autonomy Artifacts

```bash
PYTHONPATH=. python3 -m scripts.run_beta_showcase
```

This runs the offline autonomy harness, writes `artifacts_autonomy.json`, and prints a metrics summary (scenario count, total runtime, guardrail pass rate, tool usage).

## 2. Review Metrics In The CLI

```bash
PYTHONPATH=. python3 -m cite_agent.cli --metrics
```

Displays the latest guardrail status and tool usage so you can cite results during demos. If the artifact is missing the CLI will remind you to run the showcase script first.

## 3. Launch With Showcase Presets

```bash
PYTHONPATH=. python3 -m cite_agent.cli --presets
```

Prints curated prompts for research, analytics, finance, and memory workflows. Pick a preset and run it directly with `nocturnal "<prompt>"` during the live demo.

## 4. Recommended Live Flow

1. Run the finance preset to show FinSight integration.
2. Trigger the multi-hop research prompt for Archive + FinSight reasoning.
3. Execute the analytics preset to highlight shell/CSV analysis.
4. End with the archive memory prompt to prove continuity.

## 5. Before Each Demo

- Re-run `PYTHONPATH=. python3 -m scripts.run_beta_showcase` to refresh artifacts.
- Skim `artifacts_autonomy.json` for scenario transcripts.
- Pull a quick token snapshot with `PYTHONPATH=. python3 -m cite_agent.cli --token-report` (or `python3 scripts/token_report.py`).
- Update your talking points with any new guardrail notices or tool usage spikes.

Keeping these steps handy ensures every beta walkthrough feels deliberate and data-backed.
