import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://vulnshop:vulnshop_secret@localhost:5432/vulnshop",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.environ.get("JWT_SECRET", "weak_lab_secret_change_me")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    INTERNAL_API_URL = os.environ.get("INTERNAL_API_URL", "http://internal-api:8080")
    METADATA_URL = os.environ.get("METADATA_URL", "http://metadata:8080")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/app/uploads")
    LAB_SECRETS_DIR = "/app/lab-secrets"
