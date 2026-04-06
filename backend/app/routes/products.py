from flask import jsonify, request
from sqlalchemy import text

from app.auth_utils import optional_auth, require_auth
from app.extensions import db
from app.models import Category, Product, Review, User
from app.models import money
from app.routes import bp_products


def _product_dict(p: Product):
    return {
        "id": p.id,
        "category_id": p.category_id,
        "name": p.name,
        "description": p.description,
        "price": money(p.price),
        "stock": p.stock,
        "image_url": p.image_url,
    }


@bp_products.route("", methods=["GET"])
def list_products():
    category = request.args.get("category")
    category_slug = request.args.get("category_slug")
    q = Product.query.filter_by(is_active=True)
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            q = q.filter(Product.category_id == cat.id)
    elif category:
        q = q.filter(Product.category_id == int(category))
    page = int(request.args.get("page", 1))
    per = min(int(request.args.get("per", 20)), 100)
    items = q.paginate(page=page, per_page=per, error_out=False)
    return jsonify(
        {
            "items": [_product_dict(p) for p in items.items],
            "total": items.total,
            "page": page,
        }
    )


@bp_products.route("/search", methods=["GET"])
def search_products():
    # VULN-001: SQL injection in search (classic)
    term = request.args.get("q", "")
    sql = f"SELECT id, name, price, stock, image_url FROM products WHERE is_active = true AND name ILIKE '%{term}%'"
    rows = db.session.execute(text(sql)).fetchall()
    out = [
        {
            "id": r[0],
            "name": r[1],
            "price": str(r[2]),
            "stock": r[3],
            "image_url": r[4] or "",
        }
        for r in rows
    ]
    return jsonify({"items": out})


@bp_products.route("/search-blind", methods=["GET"])
def search_blind():
    # VULN-002: blind SQLi — boolean feedback
    term = request.args.get("q", "")
    sql = f"SELECT COUNT(*) FROM products WHERE is_active = true AND name ILIKE '%{term}%'"
    try:
        c = db.session.execute(text(sql)).scalar()
        return jsonify({"count": int(c)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_products.route("/sorted", methods=["GET"])
def sorted_products():
    # VULN-003: order by injection
    sort_col = request.args.get("sort", "id")
    allowed = {"id", "name", "price"}
    # Intentionally permissive: allow arbitrary if contains comma for stacked injection
    order = request.args.get("order", "asc")
    frag = f"{sort_col} {order}"
    sql = text(f"SELECT id, name, price FROM products WHERE is_active = true ORDER BY {frag}")
    try:
        rows = db.session.execute(sql).fetchall()
        return jsonify({"items": [{"id": r[0], "name": r[1], "price": str(r[2])} for r in rows]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_products.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({"product": _product_dict(p)})


@bp_products.route("/detail", methods=["GET"])
def detail_by_param():
    # VULN-004: IDOR — no ownership; exposes any product by id
    pid = request.args.get("id")
    p = Product.query.get(int(pid))
    if not p:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"product": _product_dict(p)})


@bp_products.route("/<int:product_id>/reviews", methods=["GET"])
def list_reviews(product_id):
    reviews = Review.query.filter_by(product_id=product_id).all()
    out = []
    for r in reviews:
        u = User.query.get(r.user_id)
        out.append(
            {
                "id": r.id,
                "rating": r.rating,
                "title": r.title,
                "body": r.body,
                "author": u.email if u else "",
            }
        )
    return jsonify({"reviews": out})


@bp_products.route("/<int:product_id>/reviews", methods=["POST"])
@require_auth
def add_review(product_id):
    from flask import g

    data = request.get_json() or {}
    # VULN-005: stored XSS — body/title stored raw
    r = Review(
        product_id=product_id,
        user_id=g.current_user.id,
        rating=int(data.get("rating", 5)),
        title=data.get("title") or "",
        body=data.get("body") or "",
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({"id": r.id}), 201


@bp_products.route("/preview", methods=["GET"])
@optional_auth
def preview_template():
    # VULN-006: SSTI — user-controlled Jinja2 template string
    from jinja2 import Template

    name = request.args.get("name", "")
    return Template(name).render(), 200, {"Content-Type": "text/html; charset=utf-8"}
