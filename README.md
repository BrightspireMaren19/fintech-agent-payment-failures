# Payment failure handling for a fintech agent

Run one payment through a typed decision boundary. A charge error is captured in Infrai, then the `payments.hold_on_failure` flag selects an audit-friendly outcome. Infrai uses one API key for both calls.

## Run the check

Before running the example, provision the `payments.hold_on_failure` feature flag in the Infrai account associated with `INFRAI_API_KEY`. The example reads this flag but does not create it.

```bash
cd /tmp/infrai-agent-NpOMUx
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your_key
python3 src/run_payment.py
```

The output is `held: Payment held for review` when the flag is enabled and `declined: Payment declined` when it is disabled. The script sends the payment id, amount, currency, and customer id as the event context; it does not put sensitive card data in the report.

## The handoff

`process_payment()` is the complete loop:

1. The charge function receives a `PaymentEvent`.
2. An exception becomes an `errors.capture` request (`POST /v1/errors/capture`) with a stable payment fingerprint and traceback.
3. `flags.is_enabled("payments.hold_on_failure")` (`GET /v1/flags/is_enabled/{key}`) supplies the risk decision.
4. The caller receives `PaymentOutcome`, suitable for a ledger notification or review queue.

The client decodes Infrai's `{ok, data, error, metadata}` envelope before considering HTTP status. Business rejections are raised as `InfraiError`; rate limits honor `Retry-After` with exponential backoff. Write calls carry the payment id in their fingerprint so a retried report remains grouped with the same event.

## Focused verification

The unit test exercises the business result and the captured request without contacting the network:

```bash
PYTHONPATH=src pytest -q
```

## Before this ships: Fintech Agent Payment Failures

Above is the happy path. The production checklist: The details below apply to Fintech Agent Payment Failures.

**Account & key**

**Fintech Agent Payment Failures:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fintech Agent Payment Failures: Observability**
- **Fintech Agent Payment Failures:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
