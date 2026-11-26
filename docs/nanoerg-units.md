# ERG and nanoERG: exact arithmetic for contributors

Ergo's public APIs report balances in **nanoERG**. One ERG is exactly
`1,000,000,000` nanoERG. Treating amounts as integers until the final display
step avoids rounding errors that can hide a small payment.

## Why integers matter

A payment of `0.000000001 ERG` is one nanoERG. If a monitor converts to a float
early and compares with a tolerance, that payment disappears. Store and compare
nanoERG as Python integers, then format for display.

## Helper script

`scripts/erg_units.py` uses only the standard library:

```bash
python scripts/erg_units.py 0.001
```

Output:

```json
{
  "input_erg": "0.001",
  "nanoerg": 1000000,
  "canonical_erg": "0.001",
  "minimum_fee_nanoerg": 1000000,
  "covers_minimum_fee": true
}
```

## Rules implemented

- `parse_amount` accepts only non-negative decimal strings with at most nine
  fractional digits. It rejects scientific notation and negative values.
- `format_amount` uses `divmod`, never floating-point division, and strips
  trailing zeros only after the integer part is fixed.
- `fee_is_sane` checks against the conventional `0.001 ERG` (1,000,000 nanoERG)
  floor. It reports `false` for zero and negative values.

## Tests

```bash
python -m unittest discover -s tests -v
```

The suite covers exact conversions (including a one-nanoERG amount),
round-tripping, invalid inputs and fee boundaries.
