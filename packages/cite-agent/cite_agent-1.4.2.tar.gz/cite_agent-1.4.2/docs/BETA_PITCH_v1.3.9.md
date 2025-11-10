# Cite-Agent v1.3.9 — Beta Launch Brief

> Academic research and finance assistant that lives in the same terminal pane researchers already use (RStudio, Jupyter, VS Code, Windows console). Zero hallucinations, full reproducibility, installable via a single Windows `.exe`.

---

## Snapshot
- **Audience:** Graduate students, academic researchers, finance analysts who live in R/Stata/Jupyter but don’t want to write boilerplate code.
- **Price (beta):** NT$300 / US$9–10 per month (auto-update CLI included).
- **Distribution:** `pip install cite-agent` on macOS/Linux; signed Windows installer (`Cite-Agent-Installer-v2.0.exe`) for GUI onboarding.
- **Baseline version:** 1.3.9 (all guardrails green, conversation archive restored, Windows packaging refreshed).

---

## Core Value
| Job to be Done | Cite-Agent Experience | Time Saved |
| --- | --- | --- |
| Explore local datasets | “load `sample_data.csv`, highlight trends” → instant Pandas summary, missing values, plots | 10–15 min/task |
| Compare company fundamentals | “compare Tesla and Ford TTM revenue & margins” → live FinSight data, citations | 20–30 min/company |
| Literature review | “find three recent EV battery storage papers with DOIs” → Archive API results, saved context | 30–60 min/review |
| Project navigation | “find my thesis folder, show `analysis.R`” → CLI handles `find/ls/cat`, infers functions | 5–10 min/session |
| Maintain continuity | “remember final report lives in `summary_v2.md`” → persisted memory, archive JSON | Avoids rework |

**Conservative user feedback target:** 2–3 hours saved per researcher per week.

---

## Capabilities (Beta)
1. **Autonomous shell planner** – safely runs `ls`, `head`, `find`, Python snippets, without asking users to do it manually. Guardrail suite (12/12 scenarios) passes.
2. **Data analysis assistant** – built-in Pandas runner for CSV aggregation, outlier checks, missing-value scans.
3. **FinSight integration** – live financial metrics (revenue, net income, margins) for US tickers with sources (SEC, Yahoo Finance).
4. **Archive integration** – semantic search over Semantic Scholar/OpenAlex with citation lists and memory logging.
5. **Conversation archive** – per-user JSON summaries saved under `~/.cite_agent` so context persists across sessions.
6. **Auto-updater** – once per day check against PyPI; upgrades happen silently (pip or pipx).
7. **Windows installer** – Inno Setup `.exe` that installs Python (if needed), cite-agent, updates PATH, creates shortcuts, and launches the CLI. New guard prevents running bootstrap scripts manually.

---

## Competitive Position
| Product | Local file access | Finance data | Research citations | Terminal-native | Price |
| --- | --- | --- | --- | --- | --- |
| **Cite-Agent** | ✅ | ✅ | ✅ | ✅ (RStudio/Jupyter/Stata via CLI) | NT$300 |
| ChatGPT | ❌ (upload only) | ⚠️ (often stale) | ⚠️ (no direct sources) | ❌ | US$20 |
| Claude Code | ⚠️ (sandbox) | ❌ | ⚠️ | ✅ (web IDE) | US$20 |
| Cursor | ✅ | ❌ | ❌ | ✅ (VS Code fork) | US$20–40 |
| Bloomberg / FactSet | ❌ | ✅ | ⚠️ (finance only) | ❌ | US$2k+/mo |

Researchers primarily value **accuracy** and **low setup friction**; undercutting premium IDE agents at NT$300 is a viable wedge as long as hallucinations are zero and onboarding stays simple.

---

## Beta Readiness Checklist (Done)
- ✅ Autonomy harness: 12/12 guardrails green (`scripts.run_beta_showcase`).
- ✅ Local tests: `tests/enhanced/test_conversation_archive.py`, `tests/enhanced/test_autonomy_harness.py` pass (with `pytest-asyncio`).
- ✅ Windows packaging: Inno Setup + PowerShell GUI, guardrails preventing direct script execution, docs refreshed.
- ✅ Docs updated: developer notes, beta showcase guide, installer README.
- ⏳ Pending: manual smoke test on Windows VM (double-click installer, verify desktop shortcut). Scheduled after zip transfer.

---

## Roadmap to GA
1. **Infrastructure**  
   - Run full pytest suite in CI with backend services (Redis/Mongo/API) on, fail on regressions.  
   - Sign the `.exe` to avoid Windows SmartScreen warnings.  
   - Add pipeline step that regenerates `scripts.run_beta_showcase` artifact and fails if guardrails regress.
2. **Integrations**  
   - Zotero sync (citation import/export, PDF linking).  
   - R/Stata notebooks: `.ado` / RStudio addin to embed cite-agent without leaving the window.  
   - Optional connectors: Canva, Overleaf, lab notebooks.
3. **Collaboration**  
   - Shared research journal/knowledge base, user accounts, telemetry dashboard, team plans.
4. **Experience polish**  
   - “Notebook mode” for cleaner output in Stata/SPSS, optional thin desktop UI (Electron/Tauri) for non-terminal users.  
   - Support & troubleshooting guide, feedback loop, SLA commitments.

---

## Messaging Highlights
- **One command, zero hallucinations** – cite-agent reads your data locally, cites sources, and remembers context without leaving RStudio or Jupyter.
- **Academic + finance dual focus** – combine peer-reviewed research with live financial metrics for interdisciplinary work.
- **Install in 60 seconds** – a Windows installer handles Python, PATH, shortcuts; macOS/Linux users keep `pip install cite-agent`.
- **Priced for individuals** – NT$300/mo makes it accessible to grad students while undercutting enterprise IDEs.

---

## Call to Action
1. Finish Windows smoke test (manual run on spare machine).  
2. Invite first beta cohort (target 20–30 researchers across economics, finance, social sciences).  
3. Collect structured feedback on: data workflows, financial accuracy, research coverage, desired integrations.  
4. Use findings to prioritize GA roadmap (Zotero, collaboration, UI polish).  
5. Plan public launch marketing once GA checklist is complete.

---

*Prepared: 2025-10-30 — aligns with `docs/DEV_NOTES_2025-10-30.md`. Update after Windows smoke test and beta feedback.*
