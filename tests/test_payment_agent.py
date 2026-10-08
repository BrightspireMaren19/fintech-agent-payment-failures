from payment_agent import PaymentEvent, PaymentOutcome, process_payment


class StubClient:
    def __init__(self):
        self.captured = None

    def capture_failure(self, event):
        self.captured = event
        return {}

    def is_enabled(self, key):
        return key == "payments.hold_on_failure"


def test_failed_charge_is_captured_and_held():
    client = StubClient()
    event = PaymentEvent("pay_7", 5000, "USD", "cus_9")

    result = process_payment(event, lambda _: (_ for _ in ()).throw(ValueError("issuer")), client)

    assert result == PaymentOutcome("held", "Payment held for review")
    assert client.captured["context"]["payment_id"] == "pay_7"
    assert client.captured["fingerprint"] == ["payment-agent", "pay_7"]
