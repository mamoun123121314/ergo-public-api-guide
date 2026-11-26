#!/usr/bin/env python3
"""Poll an Ergo address with the public API and record observed increases.

Read-only and standard library only. An increase in `totalBalance` is recorded
as an observation, not as a confirmed payment from a particular bounty.
"""

import json
import sys
import time
import urllib.request

API = "https://api.ergoplatform.com/api/v0/addresses/{}"


def fetch_balance(address, opener=urllib.request.urlopen):
    request = urllib.request.Request(API.format(address), headers={"Accept": "application/json"})
    with opener(request, timeout=20) as response:
        data = json.load(response)
    return int(data["transactions"]["totalBalance"])


def observe(address, state_path, opener=urllib.request.urlopen, now=time.time):
    """Compare the current balance with the last observation and return an event."""
    balance = fetch_balance(address, opener)
    previous = None
    try:
        with open(state_path, encoding="utf-8") as handle:
            previous = json.load(handle).get("balance_nanoerg")
    except (OSError, ValueError):
        pass

    increase = None if previous is None else balance - int(previous)
    event = {
        "observed_at_epoch": int(now()),
        "address": address,
        "balance_nanoerg": balance,
        "previous_nanoerg": previous,
        "increase_nanoerg": max(0, increase) if increase is not None else None,
        "status": "observed" if increase and increase > 0 else "unchanged",
    }
    with open(state_path, "w", encoding="utf-8") as handle:
        json.dump({"balance_nanoerg": balance}, handle)
    return event


def main():
    if len(sys.argv) != 3:
        print("usage: python watch_address.py <address> <state.json>", file=sys.stderr)
        return 2
    print(json.dumps(observe(sys.argv[1], sys.argv[2]), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
