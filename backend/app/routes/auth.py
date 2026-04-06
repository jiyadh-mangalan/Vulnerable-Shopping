import hashlib
import secrets

from flask import jsonify, redirect, request

from app.auth_utils import decode_token, get_bearer_token, issue_token, require_auth
from app.extensions import db
from app.models import User
from app.routes import bp_auth


def _enumerate_error(email: str):
    # VULN-014: user enumeration via distinct error messages
    u = User.query.filter_by(email=email).first()
    if not u:
        return jsonify({"error": "no_such_user", "detail": f"No account for {email}"}), 400
    return None


@bp_auth.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = data.get("full_name") or ""
    if not email or not password:
        return jsonify({"error": "invalid"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_taken"}), 409
    user = User(email=email, full_name=full_name, role="user")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    token = issue_token(user)
    return jsonify({"access_token": token, "user": _user_public(user)}), 201


@bp_auth.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user:
        err = _enumerate_error(email)
        return err if err else (jsonify({"error": "invalid"}), 400)
    if not user.check_password(password):
        return jsonify({"error": "wrong_password", "detail": "Password does not match"}), 401
    token = issue_token(user)
    resp = jsonify({"access_token": token, "user": _user_public(user)})
    # VULN-015: token also in cookie without secure flags (lab)
    resp.set_cookie("access_token", token, httponly=False, samesite="Lax")
    return resp


@bp_auth.route("/logout", methods=["POST"])
@require_auth
def logout():
    from flask import g

    resp = jsonify({"ok": True})
    resp.set_cookie("access_token", "", expires=0)
    return resp


@bp_auth.route("/me", methods=["GET"])
def me():
    token = get_bearer_token()
    if not token:
        return jsonify({"error": "unauthorized"}), 401
    data = decode_token(token)
    if not data or "sub" not in data:
        return jsonify({"error": "unauthorized"}), 401
    user = User.query.get(int(data["sub"]))
    if not user:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"user": _user_public(user)})


@bp_auth.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "no_such_user"}), 404
    # VULN-016: predictable reset token (hash of email + short secret)
    token = hashlib.sha256(f"{email}:reset:weak".encode()).hexdigest()[:16]
    user.reset_token = token
    db.session.commit()
    return jsonify({"message": "reset_token_issued", "token": token})


@bp_auth.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    token = data.get("token") or ""
    new_password = data.get("new_password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or user.reset_token != token:
        return jsonify({"error": "invalid"}), 400
    user.set_password(new_password)
    user.reset_token = None
    db.session.commit()
    return jsonify({"ok": True})


@bp_auth.route("/redirect", methods=["GET"])
def open_redirect():
    # VULN-017: open redirect
    nxt = request.args.get("next") or "/"
    return redirect(nxt, code=302)


def _user_public(u: User):
    return {
        "id": u.id,
        "email": u.email,
        "role": u.role,
        "full_name": u.full_name,
    }
