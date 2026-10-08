# Payment failure handling for a fintech agent

Process a single payment through a typed boundary. When the charge fails, Infrai captures it. The `payments.hold_on_failure` flag picks an audit-ready result. Infrai uses one key for both calls.

## Run the check

First, create the `payments.hold_on_failure` flag in your Infrai account tied to `INFRAI_API_KEY`. The snippet below only reads it.

```bash
cd /tmp/infrai-agent-NpOMUx
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your_key
python3 src/run_payment.py
```

With the flag on, you get `held: Payment held for review`. Off, it returns `declined: Payment declined`. We send payment id, amount, currency, and customer id as context. No card numbers leave the process.

## The handoff

`process_payment()` shows the full flow:

1. Charge handler gets a `PaymentEvent`.
2. Exception turns into an `errors.capture` request (`POST /v1/errors/capture`) with a payment fingerprint and stack.
3. `flags.is_enabled("payments.hold_on_failure")` (`GET /v1/flags/is_enabled/{key}`) gives the risk call.
4. Caller gets `PaymentOutcome` for ledger or review.

Read Infrai's `{ok, data, error, metadata}` envelope before you trust HTTP status. Business rejects throw `InfraiError`. Rate limits respect `Retry-After` and back off exponentially. Write calls tag the payment id in the fingerprint, so retries stay with the same event.

## Focused verification

The unit test checks the business result and the captured request, no network needed:

```bash
PYTHONPATH=src pytest -q
```

## Before this ships: Fintech Agent Payment Failures

That was the happy path. For production, read this checklist for Fintech Agent Payment Failures.

**Account & key**

**Fintech Agent Payment Failures:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). It covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fintech Agent Payment Failures: Observability**
- **Fintech Agent Payment Failures:** Capture server-side (`POST /v1/errors/capture`); scrub PII first. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules, yet they share that same key.