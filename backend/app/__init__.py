import os
import traceback

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.config import Config
from app.extensions import db, init_cors
from app.routes import (
    bp_admin,
    bp_auth,
    bp_cart,
    bp_checkout,
    bp_debug,
    bp_misc,
    bp_orders,
    bp_payments,
    bp_products,
    bp_users,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    init_cors(app)

    with app.app_context():
        try:
            from sqlalchemy import text

            db.session.execute(
                text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS admin_notes TEXT")
            )
            db.session.commit()
        except Exception:
            db.session.rollback()

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_users)
    app.register_blueprint(bp_products)
    app.register_blueprint(bp_cart)
    app.register_blueprint(bp_checkout)
    app.register_blueprint(bp_orders)
    app.register_blueprint(bp_payments)
    app.register_blueprint(bp_admin)
    app.register_blueprint(bp_debug)
    app.register_blueprint(bp_misc)

    @app.errorhandler(Exception)
    def handle_exc(e):
        # VULN-048: verbose errors in API (lab)
        if isinstance(e, HTTPException):
            return e
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "traceback": tb}), 500

    @app.route("/uploads/<path:fname>")
    def serve_upload(fname):
        # VULN-049: path traversal in uploads
        from flask import send_from_directory

        base = "/app/uploads"
        return send_from_directory(base, fname)

    @app.route("/uploads-list", methods=["GET"])
    def uploads_list():
        # VULN-050: directory listing of uploads
        base = "/app/uploads"
        try:
            names = os.listdir(base)
        except Exception:
            names = []
        return jsonify({"files": names})

    return app
