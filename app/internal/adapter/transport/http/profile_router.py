# Path: ols_svc_sample/app/internal/adapters/transport/http/profile_router.py

from fastapi import APIRouter, status, Depends
from ....config import get_settings
from ....domain.models.profile import Profile
from ....application.http.profile_service import ProfileService
from fastapi_limiter.depends import RateLimiter

# from .....dependencies import get_token_header

settings = get_settings()

profile_service = ProfileService()

profile_http_router = APIRouter(
    prefix="/v1",
)

profile_http_router.add_api_route("/profiles", profile_service.list, methods=["GET"], response_model=list[Profile], dependencies=[Depends((RateLimiter(times=settings.rate_limit_times, seconds=settings.rate_limit_seconds)))])
profile_http_router.add_api_route("/profiles/{uuid}", profile_service.get, methods=["GET"], response_model=Profile, dependencies=[Depends((RateLimiter(times=settings.rate_limit_times, seconds=settings.rate_limit_seconds)))])
profile_http_router.add_api_route("/profiles", profile_service.post, methods=["POST"], response_model=Profile, status_code=status.HTTP_201_CREATED, dependencies=[Depends((RateLimiter(times=settings.rate_limit_times, seconds=settings.rate_limit_seconds)))])
profile_http_router.add_api_route("/profiles/{uuid}", profile_service.put, methods=["PUT"], response_model=Profile, dependencies=[Depends((RateLimiter(times=settings.rate_limit_times, seconds=settings.rate_limit_seconds)))])
profile_http_router.add_api_route("/profiles/{uuid}", profile_service.delete, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends((RateLimiter(times=settings.rate_limit_times, seconds=settings.rate_limit_seconds)))])
profile_http_router.add_api_route("/healthcheck", profile_service.health, methods=["GET"], status_code=status.HTTP_200_OK)

# profile_http_router.add_api_route("/profiles", profile_service.list, methods=["GET"], response_model=list[Profile], dependencies=[Depends(get_token_header)])
# profile_http_router.add_api_route("/profiles/{profileUserId}", profile_service.get, methods=["GET"], response_model=Profile, dependencies=[Depends(get_token_header)])
# profile_http_router.add_api_route("/profiles", profile_service.post, methods=["POST"], response_model=Profile, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_token_header)])
# profile_http_router.add_api_route("/profiles/{profileUserId}", profile_service.put, methods=["PUT"], response_model=Profile, dependencies=[Depends(get_token_header)])
# profile_http_router.add_api_route("/profiles/{profileUserId}", profile_service.delete, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_token_header)])

