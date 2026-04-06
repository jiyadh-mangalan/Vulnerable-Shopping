import csv
import io
import os
import subprocess
from decimal import Decimal

from flask import g, jsonify, request, Response
from sqlalchemy import func

from app.auth_utils import require_admin, require_auth
from app.extensions import db
from app.models import Order, OrderItem, Payment, Product, Refund, User
from app.models import money
from app.routes import bp_admin


@bp_admin.route("/ping", methods=["GET"])
@require_auth
def admin_ping():
    # VULN-030: command injection (admin-only by token role — forge admin JWT)
    host = request.args.get("host", "127.0.0.1")
    if g.token_payload.get("role") != "admin":
        return jsonify({"error": "forbidden"}), 403
    try:
        out = subprocess.check_output(f"ping -c 1 {host}", shell=True, stderr=subprocess.STDOUT, timeout=5)
        return jsonify({"output": out.decode(errors="replace")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_admin.route("/products", methods=["GET"])
@require_admin
def admin_list_products():
    items = Product.query.all()
    return jsonify(
        {
            "items": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": money(p.price),
                    "stock": p.stock,
                }
                for p in items
            ]
        }
    )


@bp_admin.route("/products", methods=["POST"])
@require_admin
def admin_create_product():
    data = request.get_json() or {}
    p = Product(
        category_id=data.get("category_id"),
        name=data.get("name") or "item",
        description=data.get("description"),
        price=data.get("price") or 0,
        stock=int(data.get("stock") or 0),
        image_url=data.get("image_url"),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"id": p.id}), 201


@bp_admin.route("/products/<int:pid>", methods=["PUT"])
@require_admin
def admin_update_product(pid):
    p = Product.query.get_or_404(pid)
    data = request.get_json() or {}
    for k in ("name", "description", "price", "stock", "image_url", "is_active"):
        if k in data:
            setattr(p, k, data[k])
    db.session.commit()
    return jsonify({"ok": True})


@bp_admin.route("/stats", methods=["GET"])
@require_admin
def admin_stats():
    user_count = User.query.count()
    order_count = Order.query.count()
    paid_revenue = (
        db.session.query(func.coalesce(func.sum(Order.total), 0))
        .filter(Order.payment_status == "paid")
        .scalar()
    )
    unpaid_orders = Order.query.filter(Order.payment_status != "paid").count()
    return jsonify(
        {
            "users": user_count,
            "orders": order_count,
            "revenue_paid": money(paid_revenue),
            "unpaid_orders": unpaid_orders,
        }
    )


@bp_admin.route("/orders", methods=["GET"])
@require_admin
def admin_list_orders():
    page = int(request.args.get("page", 1))
    per = min(int(request.args.get("per", 20)), 100)
    status = request.args.get("status")
    q = Order.query.order_by(Order.id.desc())
    if status:
        q = q.filter(Order.status == status)
    items = q.paginate(page=page, per_page=per, error_out=False)
    out = []
    for o in items.items:
        u = User.query.get(o.user_id)
        out.append(
            {
                "id": o.id,
                "user_id": o.user_id,
                "customer_email": u.email if u else "",
                "total": money(o.total),
                "status": o.status,
                "payment_status": o.payment_status,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
        )
    return jsonify({"orders": out, "total": items.total, "page": page})


@bp_admin.route("/orders/<int:order_id>", methods=["GET"])
@require_admin
def admin_get_order(order_id):
    o = Order.query.get_or_404(order_id)
    u = User.query.get(o.user_id)
    lines = OrderItem.query.filter_by(order_id=o.id).all()
    return jsonify(
        {
            "order": {
                "id": o.id,
                "user_id": o.user_id,
                "customer_email": u.email if u else None,
                "subtotal": money(o.subtotal),
                "discount": money(o.discount),
                "total": money(o.total),
                "status": o.status,
                "payment_status": o.payment_status,
                "shipping_address": o.shipping_address,
                "admin_notes": o.admin_notes or "",
                "created_at": o.created_at.isoformat() if o.created_at else None,
            },
            "items": [
                {
                    "product_id": li.product_id,
                    "quantity": li.quantity,
                    "unit_price": money(li.unit_price),
                }
                for li in lines
            ],
        }
    )


@bp_admin.route("/orders/<int:order_id>", methods=["PATCH"])
@require_admin
def admin_patch_order(order_id):
    # VULN-055: admin_notes stored raw (XSS when rendered in admin UI)
    # VULN-056: mass assignment — arbitrary Order columns from JSON
    o = Order.query.get_or_404(order_id)
    data = request.get_json() or {}
    for k, v in data.items():
        if not hasattr(o, k):
            continue
        if k == "id":
            continue
        if k in ("subtotal", "discount", "total") and v is not None:
            setattr(o, k, Decimal(str(v)))
        elif k in ("user_id", "coupon_id") and v is not None:
            setattr(o, k, int(v))
        else:
            setattr(o, k, v)
    db.session.commit()
    return jsonify({"ok": True})


@bp_admin.route("/payments", methods=["GET"])
@require_admin
def admin_list_payments():
    payments = Payment.query.order_by(Payment.id.desc()).limit(200).all()
    out = []
    for p in payments:
        o = Order.query.get(p.order_id)
        u = User.query.get(o.user_id) if o else None
        out.append(
            {
                "id": p.id,
                "order_id": p.order_id,
                "amount": money(p.amount),
                "card_last4": p.card_last4,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "customer_email": u.email if u else "",
            }
        )
    return jsonify({"payments": out})


def export_orders_csv():
    # VULN-057: missing authentication — full order export
    rows = (
        db.session.query(Order, User.email)
        .join(User, Order.user_id == User.id)
        .order_by(Order.id.desc())
        .limit(5000)
        .all()
    )
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["order_id", "email", "total", "status", "payment_status", "created_at"])
    for o, email in rows:
        w.writerow(
            [
                o.id,
                email,
                money(o.total),
                o.status,
                o.payment_status,
                o.created_at.isoformat() if o.created_at else "",
            ]
        )
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"},
    )


@bp_admin.route("/export/orders", methods=["GET"])
def export_orders_public():
    return export_orders_csv()


@bp_admin.route("/users", methods=["GET"])
@require_admin
def admin_users():
    users = User.query.all()
    return jsonify(
        {
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "role": u.role,
                    "full_name": u.full_name,
                }
                for u in users
            ]
        }
    )


@bp_admin.route("/users/<int:uid>", methods=["PATCH"])
@require_auth
def admin_patch_user(uid):
    # VULN-031: broken access control — only checks Bearer present, not admin
    u = User.query.get_or_404(uid)
    data = request.get_json() or {}
    for k in ("role", "email", "full_name"):
        if k in data:
            setattr(u, k, data[k])
    db.session.commit()
    return jsonify({"ok": True})


@bp_admin.route("/orders/<int:order_id>/refund", methods=["POST"])
@require_admin
def admin_refund(order_id):
    # VULN-032: refund amount not capped
    # VULN-058: accepts form-urlencoded (no CSRF token) — vulnerable to CSRF if admin session in browser
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()
    amount = data.get("amount")
    o = Order.query.get_or_404(order_id)
    amt = Decimal(str(amount)) if amount is not None else o.total
    r = Refund(order_id=o.id, amount=amt, reason=data.get("reason"))
    db.session.add(r)
    o.payment_status = "refunded"
    db.session.commit()
    return jsonify({"refund_id": r.id})


@bp_admin.route("/config", methods=["GET"])
@require_admin
def admin_config():
    # VULN-033: sensitive env exposure for admin
    return jsonify(
        {
            "JWT_SECRET": os.environ.get("JWT_SECRET"),
            "DATABASE_URL": os.environ.get("DATABASE_URL"),
            "INTERNAL_API_URL": os.environ.get("INTERNAL_API_URL"),
        }
    )


@bp_admin.route("/upload", methods=["POST"])
@require_admin
def admin_upload():
    # VULN-034: weak file upload — extension check only
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no_file"}), 400
    name = f.filename or "file"
    path = os.path.join("/app/uploads", name)
    f.save(path)
    return jsonify({"path": path, "url": f"/uploads/{name}"})
