#!/usr/bin/env python3
"""Read-only Ergo address balance check using the public explorer API.

No keys, no wallet, no third-party dependencies. Python 3.8+.
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.ergoplatform.com/api/v0/addresses/{}"
NANOERG_PER_ERG = 1_000_000_000


def fetch(address):
    url = API.format(urllib.parse.quote(address, safe=""))
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "ergo-public-api-guide/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def summary(address):
    data = fetch(address)
    tx = data.get("transactions", {})
    balance = tx.get("totalBalance", 0)
    return {
        "address": data.get("summary", {}).get("id", address),
        "confirmed_transactions": tx.get("confirmed", 0),
        "received_nanoerg": tx.get("totalReceived", 0),
        "balance_nanoerg": balance,
        "balance_erg": balance / NANOERG_PER_ERG,
    }


def main():
    if len(sys.argv) != 2:
        print("usage: python check_ergo_address.py <ergo-address>", file=sys.stderr)
        return 2
    try:
        result = summary(sys.argv[1])
    except (urllib.error.URLError, ValueError, KeyError) as exc:
        print("could not read address: {}".format(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
