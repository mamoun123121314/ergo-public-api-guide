#!/usr/bin/env python3
"""Integer-safe ERG / nanoERG conversions and fee sanity checks.

Standard library only. Never uses floating point for amounts, so a one-nanoERG
difference can never be lost to rounding.
"""

import json
import re
import sys

NANOERG_PER_ERG = 1_000_000_000
MIN_FEE_NANOERG = 1_000_000  # 0.001 ERG, the usual minimum-fee floor


def parse_amount(value):
    """Parse a decimal ERG string into an exact integer number of nanoERG."""
    text = str(value).strip()
    if not re.fullmatch(r"\d+(?:\.\d{1,9})?", text):
        raise ValueError("amount must be a non-negative decimal with at most 9 decimals")
    whole, _, frac = text.partition(".")
    return int(whole) * NANOERG_PER_ERG + int((frac + "0" * 9)[:9] or "0")


def format_amount(nanoerg):
    """Format an integer nanoERG amount as a canonical ERG decimal string."""
    nanoerg = int(nanoerg)
    if nanoerg < 0:
        raise ValueError("amount cannot be negative")
    whole, frac = divmod(nanoerg, NANOERG_PER_ERG)
    return "{}.{:09d}".format(whole, frac).rstrip("0").rstrip(".") or "0"


def fee_is_sane(nanoerg, exactly_minimum=False):
    """Check a fee against the conventional 0.001 ERG floor."""
    nanoerg = int(nanoerg)
    if nanoerg <= 0:
        return False
    return nanoerg == MIN_FEE_NANOERG if exactly_minimum else nanoerg >= MIN_FEE_NANOERG


def main():
    if len(sys.argv) != 2:
        print("usage: python erg_units.py <amount-in-ERG>", file=sys.stderr)
        return 2
    try:
        nanoerg = parse_amount(sys.argv[1])
    except ValueError as exc:
        print("invalid amount: {}".format(exc), file=sys.stderr)
        return 1
    print(json.dumps({
        "input_erg": sys.argv[1],
        "nanoerg": nanoerg,
        "canonical_erg": format_amount(nanoerg),
        "minimum_fee_nanoerg": MIN_FEE_NANOERG,
        "covers_minimum_fee": fee_is_sane(nanoerg),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
