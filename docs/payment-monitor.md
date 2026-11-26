# Observe Ergo payments without a wallet

A payment monitor should report what it saw, not what it assumes. This guide
uses the read-only public explorer API to compare the current balance of an
address with the last observed value and write a JSON observation line.

## Script

```bash
python scripts/watch_address.py <address> state.json
```

Example observation:

```json
{
  "observed_at_epoch": 1764168000,
  "address": "9hTcHpkQYmq8AETagsQ6RypRoGrXifC4g4dYECqfePLKFcGTLYc",
  "balance_nanoerg": 1000000000,
  "previous_nanoerg": 0,
  "increase_nanoerg": 1000000000,
  "status": "observed"
}
```

## Important distinctions

- `status: "observed"` means the balance increased by at least one nanoERG.
  It does **not** identify which bounty paid it.
- A decrease writes `increase_nanoerg: 0` and never reports a payment.
- The first run only establishes a baseline (`status: "unchanged"`).
- Poll gently — once every 10 minutes is plenty — and use backoff on `5xx`.

## Recording observations

Store the amount in nanoERG, the address, the timestamp, and the endpoint that
reported it. Only mark a reward as paid when funds are visible on-chain and the
transaction can be tied to the claim.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests cover baseline creation, a two-nanoERG increase and a decrease.
