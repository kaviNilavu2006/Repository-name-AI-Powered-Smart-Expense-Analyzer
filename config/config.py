"""Central application configuration.

Production secrets are supplied through environment variables (for example,
Elastic Beanstalk environment properties). Never commit real secrets or AWS
access keys to source control.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


class Config:
    # Flask
    FLASK_ENV = os.environ.get("FLASK_ENV", "development").lower()
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if FLASK_ENV == "production" and not SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be set in production.")
    SECRET_KEY = SECRET_KEY or "dev-only-secret-key-change-me"
    DEBUG = _env_bool("FLASK_DEBUG", False) and FLASK_ENV != "production"

    # Session cookie security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = FLASK_ENV == "production"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7  # 7 days

    # Limit request bodies to the receipt upload size.
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))

    # AWS General
    AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

    # DynamoDB
    DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "ExpenseAnalyzerExpenses")
    DYNAMODB_USERS_TABLE_NAME = os.environ.get("DYNAMODB_USERS_TABLE_NAME", "ExpenseAnalyzerUsers")
    DYNAMODB_ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL")

    # S3
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "smart-expense-analyzer-receipts")
    S3_PRESIGNED_URL_EXPIRY = int(os.environ.get("S3_PRESIGNED_URL_EXPIRY", 3600))

    # Bedrock
    BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    BEDROCK_REGION = os.environ.get("BEDROCK_REGION", AWS_REGION)
    BEDROCK_ENABLED = _env_bool("BEDROCK_ENABLED", True)

    # Uploads
    MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 5))
    ALLOWED_RECEIPT_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}
    LOCAL_UPLOAD_FOLDER = os.environ.get("LOCAL_UPLOAD_FOLDER", "uploads")

    # App behaviour
    USE_LOCAL_STORAGE_FALLBACK = _env_bool("USE_LOCAL_STORAGE_FALLBACK", FLASK_ENV != "production")
    DEMO_MODE = _env_bool("DEMO_MODE", False)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    USE_LOCAL_STORAGE_FALLBACK = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config_by_name.get(env, DevelopmentConfig)
