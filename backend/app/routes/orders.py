from flask import g, jsonify, request, Response

from app.auth_utils import require_auth
from app.extensions import db
from app.models import Order, OrderItem, Product, User
from app.models import money
from app.routes import bp_orders


@bp_orders.route("", methods=["GET"])
@require_auth
def list_orders():
    u = g.current_user
    orders = Order.query.filter_by(user_id=u.id).order_by(Order.id.desc()).all()
    return jsonify({"orders": [_order_summary(o) for o in orders]})


@bp_orders.route("/all", methods=["GET"])
def list_all_orders():
    # VULN-024: missing auth — list everyone's orders
    orders = Order.query.order_by(Order.id.desc()).limit(100).all()
    return jsonify({"orders": [_order_summary(o) for o in orders]})


@bp_orders.route("/<int:order_id>", methods=["GET"])
@require_auth
def get_order(order_id):
    # VULN-025: IDOR — any user can read any order
    o = Order.query.get_or_404(order_id)
    return jsonify({"order": _order_detail(o)})


@bp_orders.route("/<int:order_id>/invoice", methods=["GET"])
@require_auth
def invoice(order_id):
    # VULN-026: IDOR invoice
    o = Order.query.get_or_404(order_id)
    u = User.query.get(o.user_id)
    lines = OrderItem.query.filter_by(order_id=o.id).all()
    body = f"""INVOICE #{o.id}
Customer: {u.email if u else ""}
Subtotal: {money(o.subtotal)}
Discount: {money(o.discount)}
Total: {money(o.total)}
Status: {o.status} / payment: {o.payment_status}
"""
    for li in lines:
        p = Product.query.get(li.product_id)
        body += f"- {p.name if p else '?'} x{li.quantity} @ {money(li.unit_price)}\n"
    return Response(body, mimetype="text/plain")


@bp_orders.route("/<int:order_id>/duplicate", methods=["POST"])
@require_auth
def duplicate_order(order_id):
    # VULN-027: order duplication — replay without payment check
    src = Order.query.get_or_404(order_id)
    items = OrderItem.query.filter_by(order_id=src.id).all()
    o = Order(
        user_id=g.current_user.id,
        status="pending",
        subtotal=src.subtotal,
        discount=src.discount,
        total=src.total,
        coupon_id=src.coupon_id,
        shipping_address=src.shipping_address,
        payment_status="unpaid",
    )
    db.session.add(o)
    db.session.flush()
    for li in items:
        db.session.add(
            OrderItem(order_id=o.id, product_id=li.product_id, quantity=li.quantity, unit_price=li.unit_price)
        )
    db.session.commit()
    return jsonify({"order_id": o.id}), 201


def _order_summary(o: Order):
    return {
        "id": o.id,
        "total": money(o.total),
        "status": o.status,
        "payment_status": o.payment_status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _order_detail(o: Order):
    u = User.query.get(o.user_id)
    lines = OrderItem.query.filter_by(order_id=o.id).all()
    return {
        "id": o.id,
        "user_id": o.user_id,
        "customer_email": u.email if u else None,
        "subtotal": money(o.subtotal),
        "discount": money(o.discount),
        "total": money(o.total),
        "status": o.status,
        "payment_status": o.payment_status,
        "items": [
            {
                "product_id": li.product_id,
                "quantity": li.quantity,
                "unit_price": money(li.unit_price),
            }
            for li in lines
        ],
    }
