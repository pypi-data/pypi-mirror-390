# CodeSentinel Legacy Feature Map and Port Plan

Created: 2025-11-02

Principle: SECURITY > EFFICIENCY > MINIMALISM

This document maps the legacy application (quarantine_legacy_archive/legacy_v0) and defines the modern, minimal v2 design implemented in this repo.

## 1) Legacy Inventory (high-level)

Location: `quarantine_legacy_archive/legacy_v0/`

- GUI Setup Wizard (monolith)
  - `codesentinel/gui_setup_wizard.py` (~3,500 LOC):
    - Multi-step GUI (Welcome → Install Location → Requirements → Env Setup → Alert System → Code Formatting → GitHub Integration → IDE Integration → Optional Features → Summary)
    - Scrollable areas, navigation fixes, persistent Tk variables
    - Repo detection, GitHub path selection (init/clone/connect)
    - IDE detection across 8 IDEs
    - Extensive state and validation
  - `codesentinel/setup_wizard.py` (~1,300 LOC):
    - Terminal wizard: repo detection, alerts, IDE, GitHub, optional features

- Maintenance and Alerts
  - `codesentinel/scheduler.py` (~600 LOC):
    - Daily/weekly/monthly pipelines; Change Detection must run first
    - JSON-based config with deep-merge; logging to tools/monitoring/scheduler
  - `codesentinel/alert_system.py` (~350 LOC):
    - Multi-channel alerting: console/file/email/slack
    - Analyzes results JSON and dispatches alerts
  - `weekly_maintenance.py`, `monthly_maintenance.py`: suites for audits (security/deps/perf)

- Utility/Integration
  - `dependency_suggester.py`: proposes missing Python packages
  - `path_configurator.py`: path calculations across layouts
  - `setup_launcher.py`, `gui_demo.py`, documentation READMEs

- Tests and Debug Aids
  - Many focused tests: navigation, validation, rendering, repo/IDE integration
  - Summaries: canvas scroll fix, rendering fixes, validation lock fixes

## 2) Legacy Style Elements

- Typography: Segoe UI/Arial; headers bold; compact 9–11pt body text
- Layout: ttk Frames, LabelFrames; scrollable content using Canvas + Scrollbar
- Visual markers: ✓ and ✗ (policy). GUI texts sometimes used emojis; permitted for GUI
- Colors: neutral grayscale, subtle section headers
- UX fixes: Avoid relative packing issues; prefer direct pack and scroll containers; navigation locking for validation

## 3) Problems Identified (legacy)

- Monolithic GUI (3k+ LOC), large state surface, duplicated logic
- Plaintext credentials/tokens in configs
- Multiple entry points and scattered configs
- Over-engineered experiments kept post-tests

## 4) v2 Design Parameters (derived)

- Security-first: no plaintext credentials; configs saved minimally; secrets deferred to system stores
- Efficiency: load fast; shallow detection scans; limit search depth and count
- Minimalism: single `codesentinel.json`; modular GUI; small surfaces; clear responsibilities
- Robust UI: scrollable sections, clear next actions, no broken CTAs

## 5) v2 Modules (implemented or stubbed)

- CLI: `codesentinel.cli` (dev-audit, status, maintenance, alert; `setup --gui` opens wizard)
- Core: `codesentinel.core` (satisfies tests, subprocess probes)
- Alerts: `codesentinel.utils.alerts` (console/file/email/slack)
- Config: `codesentinel.utils.config` (single JSON; defaults; validation)
- GUI
  - Dependency/Launcher: `codesentinel.gui_launcher` (checks deps and launches wizard)
  - Setup Wizard v2: `codesentinel.gui_wizard_v2` (new, modular)
  - Minimal Project Setup: `codesentinel.gui_project_setup` (fallback)

## 6) Wizard v2 Feature Coverage

- Installation Location
  - Smart Git repo detection: limited depth (3), count (10), common roots (Documents/Projects/Code + cwd and parent)
  - Manual browse; pick detected repo
- Alert Preferences
  - Console/File/Email/Slack with compact fields; saved to `codesentinel.json`
- GitHub Integration
  - Options: initialize, clone, connect (configuration-only in wizard); stores URL/selection
- IDE Integration
  - Detects 8 IDEs via PATH probing; shows ✓ or not detected
- Optional Features
  - Scheduler, Git hooks, CI templates; stored in config
- Summary & Save
  - Writes single `codesentinel.json` to chosen location; optionally `git init` if initialize mode

## 7) Next Upgrades (safe, scoped)

- Secure credentials: integrate OS keyring for email password and GitHub token
- GitHub workflow: optional `gh` CLI automation gated by availability
- IDE actions: per-IDE setup hints, links, and extensions list
- Scheduler wiring: CLI to generate Git hooks and CI templates from toggles
- Alert tests: add unit tests covering config-driven alert routes

## 8) Commands

- Launch wizard after dependency installer:
  - `codesentinel-setup-gui`
  - Fallback: `python -m codesentinel.cli setup --gui`

---

This document is the authoritative map from the legacy test-bed to the v2 modular implementation, ensuring feature parity where meaningful and removing unsafe or redundant behaviors.
