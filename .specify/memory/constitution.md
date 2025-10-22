<!--
Sync Impact Report

- Version change: template (no version) → 1.0.0
- Modified principles: added/filled 5 principles (Simplicity First; Excel Live Integration; Real-time Data Updates; Configuration Transparency; No Testing Overhead)
- Added sections: Technical Constraints, Development Workflow (code organization)
- Removed sections: none (template placeholders replaced)
- Templates requiring updates:
	- .specify/templates/spec-template.md: ✅ updated (testing marked contextual/optional)
	- .specify/templates/plan-template.md: ⚠ pending (Constitution Check references - aligned but manual review advised)
	- .specify/templates/tasks-template.md: ⚠ pending (tasks/tests language may conflict with No Testing Overhead)
	- .specify/templates/checklist-template.md: ⚠ pending
	- .specify/templates/agent-file-template.md: ⚠ pending
- Follow-up TODOs:
	- TODO(RATIFICATION_DATE): If the ratification date should reflect an earlier adoption, update the metadata.
	- Manual review: run a quick review of all speckit command templates under `.specify/templates/commands/` to remove agent-specific references if any.
-->

# EPGB Options Market Data Constitution

## Core Principles

### I. Simplicity First

Keep the script straightforward and maintainable. Use vanilla Python with minimal
dependencies beyond essential libraries (xlwings, pyRofex, pandas). Avoid
over-engineering solutions for this utility script. Clear, readable code is
preferred over complex optimizations.

### II. Excel Live Integration

Excel files MUST remain updatable while open. Use xlwings for seamless
integration with existing Excel workbooks. Maintain compatibility with `.xlsb`
format. Preserve existing Excel structure and formatting when updating data.

**CRITICAL: All Excel updates MUST use bulk range updates for performance.**
Instead of updating individual cells or rows in a loop, collect all changes and
write them in a single operation using xlwings range assignments (e.g.,
`sheet.range('B3:O34').value = bulk_data`). This minimizes COM calls to Excel and
dramatically improves update speed, especially for real-time market data
streaming. Individual cell updates in loops are prohibited due to severe
performance degradation.

### III. Real-time Data Updates

Market data updates MUST occur continuously without blocking the main execution
thread. Handle API responses asynchronously where possible. Implement proper
error handling for network failures and API rate limits.

### IV. Configuration Transparency

All symbol lists, broker credentials, and data ranges MUST be clearly defined
and easily modifiable. Use the Tickers sheet for symbol configuration. Keep
sensitive credentials clearly marked but separate from core logic.

### V. No Testing Overhead

This utility script does NOT require unit tests or TDD practices. Focus on
operational reliability through clear error handling and logging rather than
formal testing frameworks. Simplicity over test coverage for this specific use
case. Tests are OPTIONAL and should be added only when they materially improve
operational reliability or are requested by stakeholders.

## Technical Constraints

### Technology Stack

- Python 3.x with essential libraries: xlwings, pyRofex, pandas
- Excel integration via xlwings (supports `.xlsb` format)
- pyRofex library for market data
- Direct Excel file manipulation while files remain open

### Performance Standards

- Market data updates should complete within reasonable timeframes (typically
	under 30 seconds)
- Excel updates must not interfere with user interaction
- **All Excel writes MUST use bulk range updates** - Single operation for the
	entire data range instead of per-row/per-cell loops
- Memory usage should remain reasonable for continuous operation

## Development Workflow

### Code Organization

- Clear separation between data fetching, processing, and Excel updating.
- Keep configuration and credentials separate from core logic (use an explicit
	configuration module or `.env` when appropriate).
- Use descriptive module and function names; prefer simple, well-documented
	functions over complex one-off scripts.

### Operational Considerations

- Logging: Provide clear, contextual logs for connection status, data
	ingestion, and Excel write operations. Use structured logging where practical.
- Error handling: Retry network calls with exponential backoff; surface
	unrecoverable errors to the operator UI or logs.
- Deployment: This is an operational utility; package and deploy in a way that
	preserves access to live Excel workbooks (e.g., run on a workstation with
	Excel installed and xlwings available).

## Governance

Amendments to this constitution MUST follow the procedure below. The
constitution is the canonical source for development constraints and overrides
local conventions where explicitly stated (for example, Excel bulk write
requirements).

- Amendment procedure: Changes MUST be proposed via a Pull Request that:
	1. Includes a clear description of the change and rationale.
 2. Specifies the required version bump (major/minor/patch) with reasoning.
 3. Lists any migration or manual steps required to comply with the change.
 4. Receives approval from at least one project maintainer (core reviewer).

- Versioning policy:
	- MAJOR: Backwards-incompatible governance changes, principle removals, or
		redefinitions that materially change project obligations.
	- MINOR: Addition of a new principle or materially expanded guidance.
	- PATCH: Wording clarifications, typo fixes, or non-semantic refinements.

- Compliance and review expectations:
	- All PRs touching runtime behavior MUST include a short "Constitution"
		checklist entry describing how the change complies with the relevant
		principle(s) (e.g., confirm bulk Excel writes where applicable).
	- Where the constitution exempts a change (for example, tests are optional),
		the PR should still document the reason and risk mitigation.

**Version**: 1.0.0 | **Ratified**: 2025-10-22 | **Last Amended**: 2025-10-22
