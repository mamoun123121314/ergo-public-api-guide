#!/usr/bin/env python3
"""Validate an Ergo address with local checks and the public explorer API.

Read-only, standard library only. Never handles keys or signing data.
"""

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.ergoplatform.com/api/v0/addresses/{}"
BASE58 = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{35,60}$")


def local_check(address):
    """Return a problem string, or None when the address is plausible."""
    address = address.strip()
    if not address:
        return "address is empty"
    if not BASE58.fullmatch(address):
        return "address is not a 35-60 character base58 string"
    return None


def fetch(address):
    url = API.format(urllib.parse.quote(address, safe=""))
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def validate(address, fetcher=fetch):
    """Return a JSON-serialisable validation result."""
    problem = local_check(address)
    if problem:
        return {"address": address, "valid": False, "reason": problem, "checked_with_api": False}
    try:
        data = fetcher(address.strip())
    except urllib.error.HTTPError as exc:
        return {"address": address.strip(), "valid": False,
                "reason": "public API returned HTTP {}".format(exc.code), "checked_with_api": True}
    except (urllib.error.URLError, ValueError) as exc:
        return {"address": address.strip(), "valid": False,
                "reason": "public API unavailable: {}".format(exc), "checked_with_api": True}
    returned = data.get("summary", {}).get("id")
    if returned != address.strip():
        return {"address": address.strip(), "valid": False,
                "reason": "API returned a different address", "checked_with_api": True}
    return {"address": address.strip(), "valid": True, "reason": "address exists on the public API",
            "checked_with_api": True}


def main():
    if len(sys.argv) != 2:
        print("usage: python validate_ergo_address.py <address>", file=sys.stderr)
        return 2
    print(json.dumps(validate(sys.argv[1]), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
