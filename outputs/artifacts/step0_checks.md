# Step 0: tooling check

Run on 2026-11-10 in the repository root, through `uv run --no-project --with-requirements requirements.txt`.

## Gateway variables (set or not, values not printed)
- `ANTHROPIC_BASE_URL`: set
- `ANTHROPIC_AUTH_TOKEN`: set
- `ANTHROPIC_MODEL`: set. Model id used: `claude-haiku-5-5`. The shell value had a trailing space; it is trimmed for runs. See `decisions.md`, "Other decisions".

## Offline tests (before the gaps were closed)
`outputs/artifacts/pytest_before.txt`: 52 collected, 32 passed, 20 failed, all 20 in `tests/test_learner_gaps.py`.

## Offline tests (after the gaps were closed)
`outputs/artifacts/pytest_after.txt`: 52 passed.
- `tests/test_agent_loop.py`: 7 passed
- `tests/test_tools_offline.py`: 24 passed
- `tests/test_learner_gaps.py`: 21 passed (9 G1, 2 G3, 7 G4, 1 G5, 2 G6)

## Tool smoke tests (no LLM)
- `tool search_internal_catalog '{"query": "air quality PM2.5 monitoring stations"}' --use-case UC1`: returns JSON; top hit `airq.station_readings`, wiki hit `station_network`.
- `tool inspect_dataset_link` on the UCI 360 page: returns JSON; `link_type` uci_dataset_page; declared `has_missing_values: no`.
- `tool list_external_register '{}' --use-case UC1`: returns JSON; policy and register sources listed.

## Use-case validation
- `validate-use-case UC1`: OK (`outputs/UC1/use_case_validation.txt`)
- `validate-use-case UC2`: OK (`outputs/UC2/use_case_validation.txt`)
