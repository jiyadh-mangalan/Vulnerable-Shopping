from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def init_cors(app):
    origins = app.config.get("CORS_ORIGINS", "*")
    if origins == "*":
        CORS(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})
    else:
        CORS(app, origins=origins.split(","))
