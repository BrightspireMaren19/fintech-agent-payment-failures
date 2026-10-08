import traceback
from dataclasses import dataclass
from typing import Any, Callable

from infrai_client import InfraiClient


@dataclass(frozen=True)
class PaymentEvent:
    payment_id: str
    amount_minor: int
    currency: str
    customer_id: str


@dataclass(frozen=True)
class PaymentOutcome:
    status: str
    notification: str


def process_payment(event: PaymentEvent, charge: Callable[[PaymentEvent], Any], client: InfraiClient) -> PaymentOutcome:
    try:
        charge(event)
        return PaymentOutcome("settled", "Payment settled")
    except Exception as exc:
        client.capture_failure({
            "title": "payment agent failure",
            "message": f"{type(exc).__name__}: {exc}",
            "level": "error",
            "fingerprint": ["payment-agent", event.payment_id],
            "exception": traceback.format_exc(),
            "context": {"payment_id": event.payment_id, "amount_minor": event.amount_minor, "currency": event.currency},
        })
        if client.is_enabled("payments.hold_on_failure"):
            return PaymentOutcome("held", "Payment held for review")
        return PaymentOutcome("declined", "Payment declined")
