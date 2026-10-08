from payment_agent import PaymentEvent, process_payment
from infrai_client import InfraiClient


def charge(event: PaymentEvent) -> None:
    raise RuntimeError("issuer response requires review")


if __name__ == "__main__":
    event = PaymentEvent("pay_demo_001", 12500, "USD", "cus_42")
    outcome = process_payment(event, charge, InfraiClient())
    print(f"{outcome.status}: {outcome.notification}")
