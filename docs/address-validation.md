# Validate an Ergo address before using it in a claim

A malformed receive address can make a valid bounty claim unpayable. This guide
shows a two-step check that needs no wallet and no secrets: a cheap local format
check, then a read-only lookup on the public explorer API.

## The check

```bash
python scripts/validate_ergo_address.py 9hTcHpkQYmq8AETagsQ6RypRoGrXifC4g4dYECqfePLKFcGTLYc
```

The script returns JSON such as:

```json
{
  "address": "9hTcHpkQYmq8AETagsQ6RypRoGrXifC4g4dYECqfePLKFcGTLYc",
  "valid": true,
  "reason": "address exists on the public API",
  "checked_with_api": true
}
```

## What it does

1. Local check: the address must be a 35–60 character base58 string. This
   rejects whitespace, `0`, `O`, `I`, `l` and other characters outside the
   base58 alphabet before any network call.
2. API check: `GET https://api.ergoplatform.com/api/v0/addresses/{address}`
   must return JSON whose `summary.id` is exactly the address supplied. A
   mismatch is treated as invalid.

HTTP errors and network failures are reported as `valid: false` with
`checked_with_api: true`, so a script can distinguish "bad address" from
"could not check".

## Safety rules

- Only ever paste **public** receive addresses into the URL or an issue.
- A successful validation proves the address is known to the public API. It
  does not prove control of the address; do not treat it as proof of payment.
- Do not paste seed phrases, secret keys or signing passwords anywhere.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests cover a valid address, a local-format rejection, and an API mismatch.
