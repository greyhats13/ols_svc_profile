#App Config
APP_HOST="0.0.0.0"
APP_PORT=8000
APP_LOG_LEVEL="info"
APP_ENV="dev"
APP_NAME="ols_svc_profile"

# Local
# MongoDB Config
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_DBNAME=ols_svc_profile
MONGO_COLLECTION=Profile
MONGO_USER=user
MONGO_PASS=pass
MONGO_AUTH_SOURCE=admin
MONGO_AUTH_MECHANISM=SCRAM-SHA-256
MONGO_DIRECT_CONNECTION=true

# Redis Config
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASS=pass
REDIS_TTL=3600

# Cloud Provider
CLOUD_PROVIDER="local"

# AWS
## IAM
AWS_REGION="us-west-1"
USE_IRSA=True
PROFILE_ROLE_ARN="arn:aws:iam::124456474132:role/iac"
PROFILE_SESSION_NAME="profile"
## DynamoDB
DYNAMODB_TABLE="ols_svc_profile"

# GCP
## Firestore
FIRESTORE_PROJECT_ID="ols-platform-dev"
FIRESTORE_DATABASE="(default)"
FIRESTORE_COLLECTION="profile"

# CORS Config
CORS_ALLOW_ORIGINS="*"
CORS_ALLOW_METHODS="GET,POST,PUT,DELETE"
CORS_ALLOW_HEADERS="*"
CORS_ALLOW_CREDENTIALS=False
CORS_MAX_AGE=86400

# Gzip Config
GZIP_MIN_LENGTH=512

# Trusted Hosts
TRUSTED_HOSTS="*"

#Gzip Config
GZIP_MIN_LENGTH=512

# Rate Limit Config
RATE_LIMIT_TIMES=20 # Number of times a user can access the API
RATE_LIMIT_SECONDS=60 # Timeframe in which the user is allowed to access the API