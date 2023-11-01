# Path: ols_svc_sample/app/internal/config.py

from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "info"
    app_env: str = "dev"
    app_name: str = "ols_svc_profile"

    ## MongoDB
    mongo_host: str = "127.0.0.1"
    mongo_port: int = 27017
    mongo_dbname: str = "ols_svc_profile"
    mongo_collection: str = "Profile"
    mongo_user: str = "user"
    mongo_pass: str = "pass"
    mongo_auth_source: str = "admin"
    mongo_auth_mechanism: str = "SCRAM-SHA-256"
    mongo_direct_connection: str = "true"

    ## Redis
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    redis_pass: str = "pass"
    redis_ttl: int = 3600

    # Cloud Provider
    cloud_provider: str = "local"
    # AWS
    ## IAM
    aws_region: str = "us-west-1"
    use_irsa: bool = False
    profile_role_arn: str = "arn:aws:iam::124456474132:role/iac"
    profile_session_name: str = "ols_svc_profile"
    ## DynamoDB
    dynamodb_table: str = "profile"

    # GCP
    ## Firestore
    firestore_project_id: str = "ols-platform-dev"
    firestore_database: str = "(default)"
    firestore_collection: str = "sample"

    # Middleware
    ## Cors
    cors_allow_origins: str = "*"
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"
    cors_allow_credentials: bool = False
    cors_max_age: int = 86400

    ## TrustedHostMiddleware
    trusted_hosts: str = "*"

    ## GZipMiddleware
    gzip_min_length: int = 512

    # Rate Limit Config
    rate_limit_times: int = 20 #times
    rate_limit_seconds: int = 60 #second

    # Loading .env file if present
    class Config:
        env_file = ".env.app"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()