# Confidence Service

## Time decay model

`ConfidenceEngine.calculate_path_confidence` applies **exponential decay** to a
base path confidence score as observations age.

### Constants

- `half_life_hours = 6.0` (default): confidence drops to 50% every 6 hours.
- `lambda_per_hour = ln(2) / half_life_hours`: derived from half-life to keep
  decay behavior interpretable and tunable.

### Rationale

- Exponential decay models uncertainty growth smoothly over time.
- A half-life representation is easier to reason about operationally than
  directly tuning a raw lambda value.
- Elapsed time is computed in hours using total seconds to preserve minute-level
  precision:
  - `hours_elapsed = (now_utc - observed_at_utc).total_seconds() / 3600`
- Both timestamps are normalized to timezone-aware UTC before subtraction.
- Negative elapsed values are clamped to `0` to protect against clock skew.
