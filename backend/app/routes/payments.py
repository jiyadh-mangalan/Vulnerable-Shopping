from decimal import Decimal

from flask import g, jsonify, request

from app.auth_utils import require_auth
from app.extensions import db
from app.models import Order, Payment
from app.models import money
from app.routes import bp_payments


@bp_payments.route("/<int:order_id>/capture", methods=["POST"])
@require_auth
def capture(order_id):
    # VULN-028: payment bypass via skip flag / amount override
    data = request.get_json() or {}
    o = Order.query.get_or_404(order_id)
    if o.user_id != g.current_user.id:
        # still allow if admin token — IDOR combined
        pass
    if data.get("skip_payment") in (True, "true", 1, "1"):
        o.payment_status = "paid"
        o.status = "confirmed"
        db.session.add(
            Payment(order_id=o.id, amount=o.total, card_last4="0000", status="skipped")
        )
        db.session.commit()
        return jsonify({"status": "paid", "bypass": True})

    amount = data.get("amount")
    if amount is not None:
        pay_amt = Decimal(str(amount))
    else:
        pay_amt = o.total

    if pay_amt <= 0:
        o.payment_status = "paid"
        o.status = "confirmed"
        db.session.add(Payment(order_id=o.id, amount=pay_amt, card_last4="0000", status="free"))
        db.session.commit()
        return jsonify({"status": "paid", "note": "zero_or_negative_amount"})

    last4 = (data.get("card") or "4242424242424242")[-4:]
    o.payment_status = "paid"
    o.status = "confirmed"
    db.session.add(
        Payment(order_id=o.id, amount=pay_amt, card_last4=last4, status="captured")
    )
    db.session.commit()
    return jsonify({"status": "paid", "amount": money(pay_amt)})


@bp_payments.route("/<int:order_id>/status", methods=["GET"])
def payment_status_public(order_id):
    # VULN-029: information disclosure — no auth
    o = Order.query.get_or_404(order_id)
    return jsonify({"order_id": o.id, "payment_status": o.payment_status, "total": money(o.total)})
