# Path: ols_svc_sample/app/internal/adapters/event_handler.py

from contextlib import asynccontextmanager
from ..config import get_settings
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter
from ..infrastructure.logger import log
from ..infrastructure.databases.mongodb import Mongo
# from fastapi_limiter.depends import RateLimiter

settings = get_settings()
if settings.cloud_provider == "aws":
    import aioboto3
    from ..infrastructure.aws.sts import get_aws_credentials

    dynamodb = {}
elif settings.cloud_provider == "local":
    mongo_collection = Mongo().getCollection()
    redis = {}

@asynccontextmanager
async def lifespan(app):
    if settings.cloud_provider == "aws":
      # dynamodb
      if settings.use_irsa:
          async with aioboto3.Session().resource(
              "dynamodb", region_name=settings.aws_region
          ) as resource:
              dynamodb["table"] = await resource.Table(settings.dynamodb_table)
              yield
      else:
          credentials = get_aws_credentials()
          async with aioboto3.Session().resource(
              "dynamodb",
              aws_access_key_id=credentials["AccessKeyId"],
              aws_secret_access_key=credentials["SecretAccessKey"],
              aws_session_token=credentials["SessionToken"],
              region_name=settings.aws_region,
          ) as resource:
              dynamodb["table"] = await resource.Table(settings.dynamodb_table)
              yield
    elif settings.cloud_provider == "local":
        await mongo_collection.create_index("uuid", unique=True)
        uri = f"redis://:{settings.redis_pass}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
        redis["ttl"] = settings.redis_ttl
        async with aioredis.from_url(uri, encoding="utf-8", decode_responses=True) as client:
            redis["client"] = client
            await FastAPILimiter.init(redis["client"])
            yield