---
name: code-review
description: >-
  Use this skill when the user asks for a code review, PR review, diff review,
  or asks you to review changes, a branch, or specific files in the InGen
  repository. Activate for any request that involves evaluating code quality,
  correctness, or adherence to project conventions.
---

# InGen Code Review Skill

Perform a thorough, structured code review of the requested changes (diff, branch, files, or PR).
Produce a single review artifact at `<appDataDir>/brain/<conversation-id>/code_review.md`.

---

## 1 — Determine Scope

Identify what to review based on the user's request:

| User says | What to review |
|---|---|
| "review my changes" / "review my diff" | `git diff HEAD` (unstaged + staged) |
| "review branch X" | `git diff main...X` |
| "review PR #N" | Fetch PR diff from GitHub |
| "review `<file>`" | The specified file(s) |
| "review last commit" | `git diff HEAD~1` |

If ambiguous, ask the user to clarify scope.

## 2 — Gather Context

Before reviewing, collect the information needed to give accurate feedback:

1. **Read the diff** — run the appropriate `git diff` command.
2. **Read surrounding code** — open the full files touched by the diff so you understand the context (callers, sibling methods, class hierarchy).
3. **Read related tests** — tests live in `test/` and mirror `ingen/` structure (e.g. `ingen/reader/` → `test/reader/`).
4. **Check the config reference** — if the change touches metadata parsing or YAML config handling, cross-reference with `docs/config_reference.md`.

## 3 — Review Checklist

Work through **every** section below. Skip a section only if it is genuinely inapplicable to the diff.

---

### 3.1 Architecture & Design

InGen follows these architectural patterns — verify changes respect them:

- **Factory pattern** — new data source types go through `SourceFactory` (`ingen/data_source/source_factory.py`); new readers through `ReaderFactory` (`ingen/reader/file_reader.py`); new preprocessors are registered in `PreProcessor.PRE_PROCESSORS` (`ingen/pre_processor/pre_processor.py`).
- **Template Method** — `BaseInterfaceGenerator.generate()` defines the skeleton: read → validate → pre_process → format → post_process → validate → notify → write. Subclasses override individual steps. Do NOT add logic that bypasses this pipeline.
- **Abstract base classes** — `Reader` (ABCMeta), `BaseInterfaceGenerator` (ABC), `DataSource`. New concrete classes MUST implement all abstract methods.
- **Separation of concerns** — readers only read, formatters only format, writers only write, validators only validate. Flag any code that crosses these boundaries.
- **Module structure** — each module (`reader/`, `writer/`, `formatters/`, `pre_processor/`, `post_processor/`, `validation/`, `data_source/`, `metadata/`, `utils/`, `lib/`) is self-contained. Cross-module imports should flow downward (generators → readers/writers/formatters) not upward.

### 3.2 Python Style & Conventions

InGen uses these conventions — flag deviations:

- **Copyright header** — every `.py` file must start with:
  ```python
  #  Copyright (c) 2023 BlackRock, Inc.
  #  All Rights Reserved.
  ```
- **Logging** — use Python's `logging` module. Module-level loggers:
  - `log = logging.getLogger()` or `log = logging.getLogger(__name__)` or `logger = logging.getLogger("module_name")`.
  - Use f-strings in log messages (this is the established pattern, not lazy %).
  - Log at appropriate levels: `info` for flow, `error` for failures, `exception` for caught exceptions.
- **Docstrings** — use the `:param name: description` / `:return: description` format for method docstrings (Sphinx/reST style). The project does NOT use Google-style or NumPy-style docstrings.
- **Type hints** — the codebase does NOT use type annotations. Do not introduce them in existing files unless the user explicitly requests a migration.
- **Import style** — explicit imports preferred. `from module import *` is used in `writer/__init__.py` and `writer/writer.py` but should be discouraged in new code.
- **String formatting** — f-strings are the standard. No `.format()` or `%` formatting.
- **Line length** — no strict enforced limit, but keep lines readable (~120 chars).
- **Python version** — must support Python >=3.9, <3.13 (see `setup.py` `python_requires`).

### 3.3 Pandas Usage

InGen is built on pandas — review pandas code carefully:

- **Version constraint** — `pandas >=2.2.2, <3.0`. Do not use pandas 3.0+ APIs or Copy-on-Write patterns.
- **DataFrame construction** — prefer `pd.DataFrame(...)` with explicit column names.
- **Chained indexing** — avoid chained indexing (`df['a']['b']`); use `.loc` / `.iloc`.
- **`.convert_dtypes()`** — used in `CSVFileReader.read()`. Be aware this converts to nullable types (Int64, StringDtype, etc.) which may behave differently than numpy dtypes.
- **In-place mutations** — the codebase mutates DataFrames in-place in formatters. Verify that mutations don't cause `SettingWithCopyWarning`.
- **great_expectations** — InGen uses the **legacy** GE API (`ge.from_pandas` + `expect_*` methods), capped at `<1.0`. Do NOT introduce GE 1.0+ patterns.

### 3.4 Error Handling

- **Exception granularity** — catch specific exceptions (`TypeError`, `FileNotFoundError`, `ValueError`, `KeyError`, `NameError`), not bare `except Exception`.
- **Re-raising** — the pattern is: log the error, then `raise` (re-raise). See `file_reader.py` for the canonical example.
- **Fallback behavior** — `return_empty_if_not_exist` flag pattern: if the flag is set in config, return an empty DataFrame on `FileNotFoundError` instead of crashing.
- **Bare `except:`** — never allowed.
- **Custom exceptions** — the project does NOT define custom exception classes; it uses built-in exceptions.

### 3.5 Testing

Tests use `unittest` (NOT `pytest`). Review test changes for:

- **Location** — tests go in `test/`, mirroring the `ingen/` package structure.
- **Framework** — `unittest.TestCase` classes. Test methods named `test_<description>`.
- **Mocking** — `unittest.mock.Mock`, `unittest.mock.patch`, `@patch` decorators. Patches target the import location, not the definition location (e.g., `@patch('ingen.reader.file_reader.pd')`).
- **Assertions** — use `self.assertEqual`, `self.assertTrue`, `self.assertRaises`, `pd.testing.assert_frame_equal`, `pd.DataFrame.equals`.
- **setUp** — use `setUp(self, mock)` when patches are needed at fixture level.
- **Temp files** — use `tempfile.NamedTemporaryFile()` for file-based tests.
- **Coverage** — every new public method should have at least one test. Every new branch (if/else) should have tests for both paths.
- **Test runner** — `python -m unittest discover -s test` (NOT pytest). Verify commands work with `python3` since `python` may not be available.

### 3.6 Dependencies & Packaging

- **requirements.txt** — dependencies pinned with lower bounds (`>=`) and upper bounds where needed (`<`). Each cap must have a comment explaining WHY.
- **setup.py** — version uses `{{VERSION_PLACEHOLDER}}` replaced by CI. The `resolve_version()` fallback returns `0.0.0.dev0` for local installs.
- **python_requires** — `>=3.9,<3.13`. Do not widen without addressing the numpy<2 constraint.
- **New dependencies** — must be added to BOTH `requirements.txt` AND justified. Avoid adding heavy transitive dependencies.
- **openpyxl** — explicitly required because pandas doesn't bundle it. If adding Excel read/write features, it's already available.
- **pyproject.toml** — build system is `setuptools>=65`. Do NOT migrate to a different build backend without explicit approval.

### 3.7 Security

- **Secrets** — credentials go through `utils/app_secrets.py` (HashiCorp Vault via `hvac`). NEVER hardcode secrets, tokens, passwords, or API keys.
- **config.properties** — uses placeholder tokens (`<host_ip_or_url>`, `<password>`). Verify no real credentials leaked.
- **Encryption** — `lib/cryptor.py` handles encryption via `pycryptodome`. Review any crypto changes with extra scrutiny.
- **SQL injection** — `utils/sql_query_parser.py` handles query construction. Verify parameterized queries, not string concatenation.
- **File paths** — watch for path traversal. `utils/path_parser.py` parses file paths from config; ensure no user-controlled input can escape intended directories.

### 3.8 Configuration & Metadata

- **YAML metadata** — `metadata/metadata_parser.py` parses user-provided YAML configs. Changes here affect all users.
- **Config reference** — if adding new config options, verify they are documented in `docs/config_reference.md`.
- **Backward compatibility** — new config keys must have sensible defaults so existing YAML files continue to work.

### 3.9 CI/CD & Release

- **GitHub Actions** — `.github/workflows/python-publish.yml` publishes to PyPI on tag push. It uses `sed` to replace `{{VERSION_PLACEHOLDER}}` in `setup.py`.
- **DCO** — all commits must be signed off (`Signed-off-by:` line). See `CONTRIBUTING.md`.
- **PR template** — `.github/pull_request_template.md` defines the DoD checklist. Remind the user to fill it out.

### 3.10 Documentation

- **Docstrings** — public methods should have docstrings with `:param` and `:return` tags.
- **README** — update `README.md` if the change introduces new user-facing features or changes installation steps.
- **Config reference** — update `docs/config_reference.md` for new YAML configuration options.
- **Examples** — add to `examples/` if the change enables a new workflow.

---

## 4 — Classify Findings

Categorize each finding using these severity levels:

| Severity | Icon | Meaning |
|---|---|---|
| **Blocker** | 🔴 | Must fix before merge — bugs, data loss, security issues, broken tests |
| **Major** | 🟠 | Should fix — design issues, missing tests, error handling gaps |
| **Minor** | 🟡 | Nice to fix — style inconsistencies, documentation gaps, naming |
| **Nit** | 🔵 | Optional — personal preference, micro-optimizations |
| **Praise** | 🟢 | Good work — highlight well-written code, clever solutions, good test coverage |

## 5 — Produce the Review Artifact

Write the review to `code_review.md` using this structure:

```markdown
# Code Review: <brief title>

## Summary
<1-3 sentence overview: what the changes do, overall quality assessment>

## Scope
<what was reviewed: files, diff range, branch, etc.>

## Findings

### 🔴 Blockers
<!-- List each blocker with file link, line reference, and explanation -->

### 🟠 Major
<!-- ... -->

### 🟡 Minor
<!-- ... -->

### 🔵 Nits
<!-- ... -->

### 🟢 Praise
<!-- Highlight what was done well -->

## Test Coverage Assessment
<Are new/changed code paths tested? What tests are missing?>

## Recommendation
- [ ] ✅ **Approve** — good to merge
- [ ] 🔄 **Request changes** — fix blockers/majors first
- [ ] 💬 **Comment** — questions to discuss before deciding
```

## 6 — Verify Your Review

Before presenting the review:

1. **Re-read each finding** — make sure the issue is real, not a misreading of the diff.
2. **Check line references** — verify file links and line numbers are correct.
3. **Cross-check test claims** — if you say "this isn't tested", confirm by searching the test directory.
4. **Avoid false positives** — do not flag code that exists in the diff context but was NOT changed.
