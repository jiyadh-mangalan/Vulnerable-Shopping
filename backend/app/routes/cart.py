from decimal import Decimal

from flask import g, jsonify, request

from app.auth_utils import require_auth
from app.extensions import db
from app.models import CartItem, Product
from app.models import money
from app.routes import bp_cart


@bp_cart.route("", methods=["GET"])
@require_auth
def get_cart():
    u = g.current_user
    items = CartItem.query.filter_by(user_id=u.id).all()
    out = []
    total = Decimal("0")
    for ci in items:
        p = Product.query.get(ci.product_id)
        if not p:
            continue
        unit = ci.client_price if ci.client_price is not None else p.price
        line = Decimal(str(unit)) * ci.quantity
        total += line
        out.append(
            {
                "id": ci.id,
                "product_id": ci.product_id,
                "name": p.name,
                "quantity": ci.quantity,
                "unit_price": money(unit),
                "line_total": money(line),
            }
        )
    return jsonify({"items": out, "subtotal": money(total)})


@bp_cart.route("/items", methods=["POST"])
@require_auth
def add_item():
    # VULN-020: client-trusted price (negative / arbitrary)
    data = request.get_json() or {}
    u = g.current_user
    pid = int(data.get("product_id"))
    qty = int(data.get("quantity", 1))
    client_price = data.get("price")
    p = Product.query.get_or_404(pid)
    ci = CartItem.query.filter_by(user_id=u.id, product_id=pid).first()
    if ci:
        ci.quantity = qty
        if client_price is not None:
            ci.client_price = Decimal(str(client_price))
    else:
        ci = CartItem(
            user_id=u.id,
            product_id=pid,
            quantity=qty,
            client_price=Decimal(str(client_price)) if client_price is not None else None,
        )
        db.session.add(ci)
    db.session.commit()
    return jsonify({"ok": True})


@bp_cart.route("/items/<int:item_id>", methods=["DELETE"])
@require_auth
def remove_item(item_id):
    u = g.current_user
    ci = CartItem.query.filter_by(id=item_id, user_id=u.id).first_or_404()
    db.session.delete(ci)
    db.session.commit()
    return jsonify({"ok": True})


@bp_cart.route("/items/<int:item_id>", methods=["PATCH"])
@require_auth
def patch_item(item_id):
    data = request.get_json() or {}
    u = g.current_user
    ci = CartItem.query.filter_by(id=item_id, user_id=u.id).first_or_404()
    if "quantity" in data:
        ci.quantity = int(data["quantity"])
    if "price" in data:
        ci.client_price = Decimal(str(data["price"]))
    db.session.commit()
    return jsonify({"ok": True})
