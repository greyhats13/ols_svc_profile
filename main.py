# Path: ols_svc_sample/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.internal.adapter.middleware import LoggingMiddleware
from app.internal.adapter.error_handler import http_exception_handler, server_error_exception_handler
from app.internal.adapter.transport.http.profile_router import profile_http_router
# from .internal.adapter.transport.graphql.profile_router import profile_gql_router
from app.internal.config import get_settings
from app.internal.adapter.event_handler import lifespan
# from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

# apm_config = {
#  'SERVICE_NAME': 'ols_svc_profile',
#  'SERVER_URL': 'http://fleet-server:8200',
#  'ENVIRONMENT': 'dev',
#  'GLOBAL_LABELS': 'platform=DemoPlatform, application=profile'
# }
# apm = make_apm_client(apm_config)

settings = get_settings()

app = FastAPI(lifespan=lifespan)


app.include_router(profile_http_router)
# app.include_router(profile_gql_router)

# Middleware
app.add_middleware(LoggingMiddleware)
# app.add_middleware(ElasticAPM, client=apm)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins.split(','),
    allow_methods=settings.cors_allow_methods.split(','),
    allow_headers=settings.cors_allow_headers.split(',')
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts.split(','))
app.add_middleware(GZipMiddleware, minimum_size=settings.gzip_min_length)

# Error Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, server_error_exception_handler)

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.app_host, port=settings.app_port, log_level="critical")