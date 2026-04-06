from flask import Response, jsonify, request

from app.routes import bp_misc


@bp_misc.route("/health", methods=["GET"])
def health():
    # VULN-042: version / build info disclosure
    return jsonify(
        {
            "status": "ok",
            "version": "vuln-shop-api-0.9.9-lab",
            "build": "debug-true",
            "internal_schema": "public",
        }
    )


@bp_misc.route("/cache/user-profile", methods=["GET"])
def cache_profile():
    # VULN-043: cache poisoning — key from X-Forwarded-Host reflected
    host = request.headers.get("X-Forwarded-Host", "default")
    body = '{"user":"guest","host":"%s"}' % host
    return Response(
        body,
        headers={
            "Cache-Control": "public, max-age=60",
            "Vary": "X-Forwarded-Host",
            "Content-Type": "application/json",
        },
    )


@bp_misc.route("/legacy/email", methods=["POST"])
def legacy_email():
    # VULN-044: CSRF-prone — no CSRF token, no JSON-only check
    email = request.form.get("email") or (request.get_json() or {}).get("email")
    return jsonify({"updated": True, "email": email})


@bp_misc.route("/graphql", methods=["POST"])
def fake_graphql():
    # VULN-045: GraphQL-like introspection exposure
    return jsonify(
        {
            "data": {
                "__schema": {
                    "types": [
                        {"name": "User", "fields": [{"name": "passwordHash"}]},
                        {"name": "Order", "fields": [{"name": "internalNotes"}]},
                    ]
                }
            }
        }
    )


@bp_misc.route("/search-raw", methods=["GET"])
def search_raw():
    # VULN-046: reflected XSS in JSON error (some clients render)
    q = request.args.get("q", "")
    return jsonify({"query": q, "echo": f"You searched for {q}"})


@bp_misc.route("/backup/config.bak", methods=["GET"])
def backup_config():
    # VULN-047: sensitive backup filename exposure
    return jsonify({"note": "rotated_keys", "old_jwt_secret": "weak_lab_secret_change_me"})
