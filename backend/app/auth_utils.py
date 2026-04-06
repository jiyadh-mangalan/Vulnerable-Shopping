import base64
import json
from functools import wraps

import jwt
from flask import g, jsonify, request

from app.config import Config
from app.models import User


def _decode_none_alg(token: str) -> dict | None:
    """VULN-012: Accept unsigned JWT (alg=none) for lab."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))
        return data
    except Exception:
        return None


def decode_token(token: str) -> dict | None:
    """VULN-011/012: Weak HS256 + alg=none bypass."""
    if not token:
        return None
    secret = Config.JWT_SECRET
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        pass
    # Intentionally weak: try with wrong verify for "none"
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        if unverified.get("alg") == "none" or token.count(".") == 2:
            payload = _decode_none_alg(token)
            if payload:
                return payload
    except Exception:
        pass
    try:
        return jwt.decode(token, secret, algorithms=["HS256"], options={"verify_exp": False})
    except Exception:
        return None


def issue_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "alg": "HS256",
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def get_bearer_token() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return request.cookies.get("access_token")


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_bearer_token()
        data = decode_token(token) if token else None
        if not data or "sub" not in data:
            return jsonify({"error": "unauthorized"}), 401
        user = User.query.get(int(data["sub"]))
        if not user:
            return jsonify({"error": "unauthorized"}), 401
        g.current_user = user
        g.token_payload = data
        return f(*args, **kwargs)

    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_bearer_token()
        data = decode_token(token) if token else None
        if not data or "sub" not in data:
            return jsonify({"error": "unauthorized"}), 401
        user = User.query.get(int(data["sub"]))
        if not user:
            return jsonify({"error": "unauthorized"}), 401
        g.current_user = user
        g.token_payload = data
        # VULN-013: role check only from token; forged token can set role=admin
        role = data.get("role") or user.role
        if role != "admin":
            return jsonify({"error": "forbidden"}), 403
        return f(*args, **kwargs)

    return decorated


def optional_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_bearer_token()
        g.current_user = None
        g.token_payload = None
        if token:
            data = decode_token(token)
            if data and "sub" in data:
                g.current_user = User.query.get(int(data["sub"]))
                g.token_payload = data
        return f(*args, **kwargs)

    return decorated
