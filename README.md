# Check an Ergo address with public APIs

A small, read-only guide for checking an Ergo address balance and transaction count without a wallet, node, API key, or third-party Python package.

Everything below uses public data. Never paste a seed phrase, secret key, or signing password into a URL, a script argument, or a public issue.

## Why this guide

New Ergo contributors often want to answer a simple question: "did this address receive anything?" The explorer website answers it interactively, but scripts need the underlying HTTP API. Two details are easy to get wrong:

1. The explorer frontend host and the public API host are different.
2. Ergo balances are returned in nanoERG, not ERG.

## The endpoint that works

Use the public explorer API:

```text
GET https://api.ergoplatform.com/api/v0/addresses/{address}
```

Example:

```bash
curl -sS 'https://api.ergoplatform.com/api/v0/addresses/9hTcHpkQYmq8AETagsQ6RypRoGrXifC4g4dYECqfePLKFcGTLYc'
```

A fresh address returns a JSON body shaped like this (abbreviated):

```json
{
  "summary": { "id": "9hTcHpkQYmq8AETagsQ6RypRoGrXifC4g4dYECqfePLKFcGTLYc" },
  "transactions": {
    "confirmed": 0,
    "totalReceived": 0,
    "totalBalance": 0,
    "confirmedBalance": 0
  }
}
```

Fields used here:

- `transactions.confirmed` — number of confirmed transactions involving the address.
- `transactions.totalReceived` — total received, in nanoERG.
- `transactions.totalBalance` — current balance, in nanoERG.

Do **not** use `https://explorer.ergoplatform.com/api/v1/addresses/...` for this. That host serves the explorer single-page application, so a `200` response can contain HTML rather than JSON. Check the response body or `Content-Type`, not just the status code. Some `/api/v1` paths on the API host also return `404`; `api/v0/addresses/{address}` is the stable read-only route for this task.

## Units

`1 ERG = 1,000,000,000 nanoERG`. Divide the integer balance by `1e9` only for display; keep it as an integer for comparisons so rounding never hides a small payment.

## Runnable script

`check_ergo_address.py` uses only the Python standard library.

```bash
python check_ergo_address.py 9hTcHpkQYmq8AETagsQ6RypRoGrXifC4g4dYECqfePLKFcGTLYc
```

Pinned output, verified on 2026-11-26 against `api.ergoplatform.com/api/v0`:

```json
{
  "address": "9hTcHpkQYmq8AETagsQ6RypRoGrXifC4g4dYECqfePLKFcGTLYc",
  "confirmed_transactions": 0,
  "received_nanoerg": 0,
  "balance_nanoerg": 0,
  "balance_erg": 0.0
}
```

Exit codes: `0` on a successful read, `1` on a network/JSON error, `2` on bad usage. For a payment monitor, poll gently (for example once every 10 minutes), compare `balance_nanoerg` with the last observed integer, and treat any `>= 1` increase as "observed" before confirming the transaction on a second read.

## Practical cautions

- This is an address **read**, not a payment proof. A balance change tells you funds arrived; it does not tell you which bounty paid them.
- Public APIs can rate-limit or return `5xx`. Retry with backoff rather than hammering the endpoint.
- Never derive a receiving address from a private key in a public script. Addresses are public data; keys are not.
- When recording an observed payment, store the amount, unit, transaction id if available, timestamp, and the endpoint that reported it. Do not record a reward as paid until the funds are actually visible.
