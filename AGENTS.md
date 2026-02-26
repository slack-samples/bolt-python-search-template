# AGENTS.md — bolt-python-search-template

## Project Overview

This is a Slack sample app demonstrating **Enterprise Search** using [Bolt for Python](https://docs.slack.dev/bolt-python). It serves as a template for building search integrations that appear natively in Slack's search experience.

- **Repo:** [slack-samples/bolt-python-search-template](https://github.com/slack-samples/bolt-python-search-template)
- **README:** [README.md](./README.md) — setup instructions, environment variables, and project structure overview
- **Docs:** [Enterprise Search](https://docs.slack.dev/surfaces/search)
- **Framework:** Bolt for Python (`slack-bolt`)
- **Runtime:** Python (see `requires-python` in `pyproject.toml`), Socket Mode

## Architecture

The app registers two **custom functions** (`search` and `filters`) and one **event listener** (`entity_details_requested`) with Slack. These are declared in `manifest.json` and wired up via the listener registration pattern.

### Listener Registration Pattern

`app.py` creates the Bolt `App` and calls `register_listeners(app)` from `listeners/__init__.py`. This delegates to sub-modules:

- `listeners/functions/__init__.py` — registers `search` and `filters` function callbacks via `app.function()`
- `listeners/events/__init__.py` — registers the `entity_details_requested` event callback via `app.event()`

### Data Flow

1. **Filters request** → `listeners/functions/filters.py` returns predefined filter definitions (languages, templates, samples) from `listeners/filters.py`
2. **Search request** → `listeners/functions/search.py` calls `fetch_sample_data()` from `listeners/sample_data_service.py`, which hits the `developer.sampleData.get` Slack API, then passes samples through as search results
3. **Entity details** → `listeners/events/entity_details_requested.py` fetches sample data and presents entity details via `entity.presentDetails` API

## Key Files & Directories

```
app.py                              # Entry point — creates App, registers listeners, starts SocketModeHandler
manifest.json                       # Slack app manifest — defines functions, events, scopes, features
pyproject.toml                      # Build config, dependencies, ruff + pytest settings
listeners/
  __init__.py                       # register_listeners(app) — delegates to functions/ and events/
  filters.py                        # Predefined filter constants (plain dicts)
  sample_data_service.py            # fetch_sample_data() — calls developer.sampleData.get API
  functions/
    __init__.py                     # Registers search and filters function callbacks
    search.py                       # search_step_callback — handles search function execution
    filters.py                      # filters_step_callback — returns available search filters
  events/
    __init__.py                     # Registers entity_details_requested event callback
    entity_details_requested.py     # Handles rich preview entity detail requests
tests/                              # Mirrors listeners/ structure
  listeners/
    test_sample_data_service.py
    functions/
      test_search.py
      test_filters.py
    events/
      test_entity_details_requested.py
.github/workflows/
  lint.yml                          # Ruff linting on push/PR
  tests.yml                         # pytest on Python 3.11, 3.12, 3.13
  dependencies.yml                  # Dependabot auto-merge
```

## Development Commands

> **IMPORTANT: A Python virtual environment MUST be activated before running ANY command in this project.**
> Before executing any command below, first verify the virtual environment is active by running `echo $VIRTUAL_ENV` — it MUST output a path.
> If it outputs nothing, do NOT proceed. Ask the user to activate a virtual environment first.

```bash
# Install dependencies (editable mode)
pip install -e .

# Run the app (Socket Mode)
python3 app.py
# Or via Slack CLI
slack run

# Lint
ruff check

# Format
ruff format
ruff check --fix

# Run tests
pytest .
```

## Code Style & Tooling

- **Linter/Formatter:** Ruff (see `[tool.ruff]` in `pyproject.toml` for line length, lint rules, and other settings)
- **Testing:** pytest (see `[tool.pytest.ini_options]` in `pyproject.toml` for test paths and logging config)
- **Python:** see `requires-python` in `pyproject.toml`

## CI Pipeline

| Workflow | File | What it does |
|---|---|---|
| Lint | `.github/workflows/lint.yml` | Runs `ruff check` on Python 3.13 |
| Tests | `.github/workflows/tests.yml` | Runs `pytest .` on Python 3.11, 3.12, 3.13 |
| Dependencies | `.github/workflows/dependencies.yml` | Dependabot auto-merge for patch/minor updates |

## Test Patterns

- Tests use `pytest` with class-based organization (e.g., `TestSearch`)
- `setup_method` creates `MagicMock` instances for Bolt primitives (`Ack`, `Complete`, `Fail`, `WebClient`, `Logger`)
- External calls (e.g., `fetch_sample_data`) are patched with `@patch` decorators
- Tests verify: correct arguments passed to service calls, expected outputs, error handling paths, and that `ack()` is always called

## Common Contribution Workflows

### Adding a new filter

1. Define the filter constant in `listeners/filters.py` as a plain dict
2. Add it to the `complete(outputs=...)` list in `listeners/functions/filters.py`
3. If it affects search, handle it in `listeners/sample_data_service.py`'s filter processing
4. Add tests in `tests/listeners/functions/test_filters.py`

### Modifying search results

1. Update `search_step_callback` in `listeners/functions/search.py`
2. Update tests in `tests/listeners/functions/test_search.py`

### Fixing a bug

1. Run `pytest .` to confirm current test state
2. Write a failing test that reproduces the bug
3. Fix the bug
4. Run `ruff check` and `pytest .` to verify
