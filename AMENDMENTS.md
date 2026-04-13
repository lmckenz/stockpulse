# StockPulse — Implementation Amendment Log

This document records intentional deviations from the original project specification.
It is a living document and should be updated as new amendments arise during development.

When conflicts exist between this document and the project specification, **this document takes precedence**.

---

## Amendment 001 — Analyzer Output Format

**Affected module:** `analyzer.py`
**Affected spec section:** Section 4 (Statistical Analysis Plan), Section 9 (Data Contract)
**Phase introduced:** Phase 3
**Status:** Accepted deviation

### Original spec
`daily_returns` and SMA series (`sma_20`, `sma_50`) to be returned as plain lists of floats.

### Actual implementation
Both are returned as lists of `(date, float)` tuples, where `date` is a string in `YYYY-MM-DD` format.

Example:
```python
[("2024-01-15", 0.0142), ("2024-01-16", -0.0083), ...]
```

### Reason
The tuple format was necessary to solve the date alignment problem in `compute_correlation()`. Bare floats carry no date context, making alignment across tickers impossible without passing dates separately. The tuple approach is cleaner, more self-documenting, and makes downstream labelling by date straightforward.

### Downstream impact
Any module consuming `daily_returns`, `sma_20`, or `sma_50` must unpack tuples. Key patterns:

```python
# Get the most recent float value from a series
latest_value = series[-1][1]

# Get the float at position i
value_at_i = series[i][1]

# Iterate over a series
for date, value in series:
    ...
```

`display.py` has been updated to handle this format using tuple unpacking throughout.

---

## Amendment 002 — run_analysis() Return Structure

**Affected module:** `analyzer.py`
**Affected spec section:** Section 9 (Data Contract)
**Phase introduced:** Phase 3
**Status:** Accepted deviation

### Original spec
`run_analysis()` to return a dict keyed directly by ticker, with the correlation matrix passed as a separate structure to downstream modules.

### Actual implementation
Both structures are wrapped in a single dict with two top-level keys:

```python
{
    "results": {ticker: {metrics}},
    "correlation_matrix": {ticker_a: {ticker_b: float}}
}
```

### Reason
Returning a single object is more convenient for callers — both structures arrive together without requiring tuple unpacking. It also makes the return value self-documenting: the keys name what each structure is, rather than relying on positional unpacking order.

### Downstream impact
Callers must access the two structures via their keys:

```python
analysis = run_analysis(ticker_data)
results = analysis["results"]
correlation_matrix = analysis["correlation_matrix"]
```

Direct iteration over the return value will yield the key strings `"results"` and `"correlation_matrix"`, not ticker symbols. Callers should always unpack explicitly as shown above.

---

## Amendment 003 — generate_report() Optional output_dir Parameter

**Affected module:** `reporter.py`
**Affected spec section:** Section 8 (Phase 5 scope)
**Phase introduced:** Phase 5
**Status:** Accepted deviation

### Original spec
Phase 5 defines the reporter's primary function as `generate_report(analysis, output_dir)`, with `output_dir` as a required positional argument. The caller is always expected to supply the output path explicitly.

### Actual implementation
`output_dir` is an optional parameter with a default value of `None`. When `None` is received, the function falls back to `config.OUTPUT_DIR`:

```python
def generate_report(analysis, output_dir=None):
    if output_dir is None:
        output_dir = config.OUTPUT_DIR
```

### Reason
`config.OUTPUT_DIR` already defines the canonical output path for the project, anchored to the project root via `config.PROJECT_ROOT`. Requiring callers to pass this path explicitly on every call would mean duplicating a value that config already owns. The optional default keeps the interface convenient for the common case while preserving full flexibility — any caller that needs a custom path (such as a `--output-dir` CLI flag in Phase 6) can still pass one and it will be respected.

### Downstream impact
`main.py` in Phase 6 may call `generate_report(analysis)` without an `output_dir` argument and will receive output at `config.OUTPUT_DIR` by default. If a `--output-dir` flag is supplied via the CLI, `main.py` should pass it explicitly: `generate_report(analysis, output_dir=args.output_dir)`. Both call patterns are valid.

```python
# Default — writes to config.OUTPUT_DIR
generate_report(analysis)

# Custom path — writes to the specified directory
generate_report(analysis, output_dir="/some/other/path")
```

Any future caller that passes `output_dir` as a positional argument continues to work without modification, as the parameter position is unchanged.

---

*End of Amendment Log*
