from flask import g, jsonify, request

from app.auth_utils import require_auth
from app.extensions import db
from app.models import User
from app.routes import bp_users


@bp_users.route("/me", methods=["GET"])
@require_auth
def get_me():
    u = g.current_user
    return jsonify({"user": _full(u)})


@bp_users.route("/me", methods=["PATCH"])
@require_auth
def patch_me():
    # VULN-018: mass assignment — client can set role via JSON
    u = g.current_user
    data = request.get_json() or {}
    for key in ("full_name", "address", "settings_json", "role"):
        if key in data:
            setattr(u, key, data[key])
    db.session.commit()
    return jsonify({"user": _full(u)})


@bp_users.route("/<int:user_id>", methods=["GET"])
@require_auth
def get_user(user_id):
    # VULN-019: IDOR — any authenticated user can read any profile
    u = User.query.get_or_404(user_id)
    return jsonify({"user": _full(u)})


def _full(u: User):
    return {
        "id": u.id,
        "email": u.email,
        "role": u.role,
        "full_name": u.full_name,
        "address": u.address,
        "settings_json": u.settings_json,
    }
