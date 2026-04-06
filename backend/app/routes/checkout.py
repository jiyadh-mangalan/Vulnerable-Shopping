from decimal import Decimal

import redis
from flask import current_app, g, jsonify, request

from app.auth_utils import require_auth
from app.extensions import db
from app.models import CartItem, Coupon, Order, OrderItem, Product
from app.models import money
from app.routes import bp_checkout


def _get_redis():
    try:
        return redis.from_url(current_app.config["REDIS_URL"])
    except Exception:
        return None


@bp_checkout.route("", methods=["POST"])
@require_auth
def checkout():
    """
    VULN-021: coupon reuse / stacking
    VULN-022: inventory race (check-then-act; use ab to race)
    VULN-023: client subtotal override
    """
    data = request.get_json() or {}
    u = g.current_user
    coupon_codes = data.get("coupons") or []
    if isinstance(coupon_codes, str):
        coupon_codes = [coupon_codes]
    client_subtotal = data.get("subtotal")
    client_discount = data.get("discount")

    items = CartItem.query.filter_by(user_id=u.id).all()
    if not items:
        return jsonify({"error": "empty_cart"}), 400

    subtotal = Decimal("0")
    order_lines = []
    for ci in items:
        p = Product.query.get(ci.product_id)
        if not p:
            continue
        unit = ci.client_price if ci.client_price is not None else p.price
        line = Decimal(str(unit)) * ci.quantity
        subtotal += line
        # VULN-022: stock check without locking
        if p.stock < ci.quantity:
            return jsonify({"error": "insufficient_stock", "product_id": p.id}), 400
        order_lines.append((p, ci.quantity, unit))

    if client_subtotal is not None:
        subtotal = Decimal(str(client_subtotal))

    discount = Decimal("0")
    applied_coupon_ids = []
    for code in coupon_codes:
        c = Coupon.query.filter_by(code=code, active=True).first()
        if not c:
            continue
        # VULN-021: no per-user tracking; stacking allowed
        d = subtotal * Decimal(c.discount_percent) / Decimal(100)
        discount += d
        c.uses_count = (c.uses_count or 0) + 1
        applied_coupon_ids.append(c.id)

    if client_discount is not None:
        discount = Decimal(str(client_discount))

    total = subtotal - discount
    if total < 0:
        total = Decimal("0")

    primary_coupon = applied_coupon_ids[0] if applied_coupon_ids else None

    order = Order(
        user_id=u.id,
        status="pending",
        subtotal=subtotal,
        discount=discount,
        total=total,
        coupon_id=primary_coupon,
        shipping_address=data.get("shipping_address") or u.address,
        payment_status="unpaid",
    )
    db.session.add(order)
    db.session.flush()

    for p, qty, unit in order_lines:
        oi = OrderItem(order_id=order.id, product_id=p.id, quantity=qty, unit_price=unit)
        db.session.add(oi)
        p.stock -= qty

    for ci in items:
        db.session.delete(ci)

    db.session.commit()

    r = _get_redis()
    if r:
        r.incr(f"orders:created:{order.id}")

    return jsonify(
        {
            "order_id": order.id,
            "subtotal": money(subtotal),
            "discount": money(discount),
            "total": money(total),
            "payment_status": order.payment_status,
        }
    ), 201
