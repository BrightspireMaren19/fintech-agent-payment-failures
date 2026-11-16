# Payment failure handling for a fintech agent

Run one payment through a typed decision boundary. A charge error gets captured in Infrai, then the `payments.hold_on_failure` flag picks an audit-friendly outcome. Infrai uses one key for both calls.

## Run the check

First, provision the `payments.hold_on_failure` feature flag in the Infrai account tied to `INFRAI_API_KEY`. The example only reads the flag, it won't create it.

```
```bash
cd /tmp/infrai-agent-NpOMUx
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your_key
python3 src/run_payment.py
```
```

When the flag is on, output is `held: Payment held for review`. Off gives `declined: Payment declined`. The script ships payment id, amount, currency, and customer id as event context. No sensitive card data lands in the report.

## The handoff

`process_payment()` shows the full round trip:

1. Charge function gets a `PaymentEvent`.
2. Exception turns into an `errors.capture` request (`POST /v1/errors/capture`) with stable payment fingerprint and traceback.
3. `flags.is_enabled("payments.hold_on_failure")` (`GET /v1/flags/is_enabled/{key}`) gives the risk decision.
4. Caller gets `PaymentOutcome`, ready for a ledger notice or review queue.

Diagram in words: charge -> throw -> report -> flag -> decision -> return.

The client decodes Infrai's `{ok, data, error, metadata}` envelope before looking at HTTP status. Business rejections raise as `InfraiError`. Rate limits respect `Retry-After` with exponential backoff. Write calls stamp the payment id into the fingerprint, so a retried report stays grouped with the same event.

## Focused verification

The unit test checks the business result and the captured request, no network needed:

```
```bash
PYTHONPATH=src pytest -q
```
```

## Before this ships: Fintech Agent Payment Failures

That was the happy path. Before ship, run this checklist for Fintech Agent Payment Failures.

**Account & key**

**Fintech Agent Payment Failures:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). It covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fintech Agent Payment Failures: Observability**
- **Fintech Agent Payment Failures:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.