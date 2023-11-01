# Path: ols_svc_sample/app/internal/application/http/profile_service.py

import ujson
from uuid import uuid4
from datetime import datetime
from starlette.exceptions import HTTPException
from ...domain.models.profile import ProfileCreate, ProfileUpdate
from ....internal.config import get_settings
from ...infrastructure.logger import log

settings = get_settings()

if settings.cloud_provider == "aws":
    from fastapi import status, APIRouter, HTTPException
    from ...infrastructure.repositories.aws.profile_repository import ProfileRepository
elif settings.cloud_provider == "gcp":
    from ...infrastructure.repositories.gcp.profile_repository import ProfileRepository
elif settings.cloud_provider == "local":
    from fastapi import status, APIRouter, HTTPException, Request, Response
    from fastapi.responses import JSONResponse
    from ...infrastructure.repositories.local.profile_repository import ProfileRepository

class ProfileService:
    def __init__(self):
        self.profile_repo = ProfileRepository()

    async def list(self, offset: int = 0, limit: int = 10) -> APIRouter:
        profiles = await self.profile_repo.list(offset, limit)
        return profiles

    # Get a profile data for http
    async def get(self, uuid: str, request: Request=None) -> APIRouter:
        if settings.cloud_provider == "aws":
            profile = await self.profile_repo.get(uuid)
            ## check if profile exists
            if 'Item' not in profile:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
            ## create response
            return profile['Item']
        elif settings.cloud_provider == "local":
            ttl = await self.profile_repo.getTtl(uuid)
            ## check if request header has if-none-match & return 304 not modified
            if request:
                if request.headers.get("if-none-match") == "W/"+uuid and ttl > 0:
                    return Response(status_code=304, headers={"Cache-Control": f"max-age={ttl}"})
            ## check if profile is cached
            profile = await self.profile_repo.getCache(uuid)
            if profile:
                ## create response
                response = JSONResponse(content=ujson.loads(profile))
                ## add cache hit headers
                response.headers["X-Cache"] = "HIT"
                ttl = await self.profile_repo.getTtl(uuid)
                response.headers["Cache-Control"] = f"max-age={ttl}"
                response.headers["Expires"] = str(ttl)
                response.headers["Etag"] = "W/"+uuid
                return response
            ## if profile is not cached, get profile db
            profile = await self.profile_repo.get(uuid)
            if not profile:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
            ## remove _id
            profile.pop("_id")
            ## cache profile
            await self.profile_repo.setCache(uuid, ujson.dumps(profile))
            ## create response
            response = JSONResponse(content=profile)
            ## add cache miss headers
            response.headers["X-Cache"] = "MISS"
            return response
    
    # Create a profile data
    async def post(self, profile: ProfileCreate) -> APIRouter:
        ## check data integrity
        if await self.profile_repo.isConflict(profile):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile email already exist")
        profile.uuid = str(uuid4())
        if profile.birthdate:
            profile.birthdate = profile.birthdate.isoformat()
        profile.updatedAt = datetime.now().isoformat()
        profile.createdAt = datetime.now().isoformat()
        # log.debug("Profile Service: %s", profile)
        if settings.cloud_provider == "aws":
            profile = await self.profile_repo.create(profile)
        elif settings.cloud_provider == "local":
            await self.profile_repo.create(profile.model_dump())
        # log.debug("Profile Service: %s", profile)
        return profile

    # Update a profile data
    async def put(self, uuid: str, profile: ProfileUpdate) -> APIRouter:
        ## check if profile exists
        if not await self.profile_repo.isExist(uuid):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        ## convert birthdate to isoformat
        if profile.birthdate:
            profile.birthdate = profile.birthdate.isoformat()
        profile.updatedAt = datetime.now().isoformat()
        if settings.cloud_provider == "aws":
            ## update profile
            await self.profile_repo.update(uuid, profile)
            profile = await self.profile_repo.get(uuid)
            # log.debug("Profile Service: %s", profile)
            return profile["Item"]
        elif settings.cloud_provider == "local":
            await self.profile_repo.update(uuid, profile.model_dump(exclude_unset=True))
            ## delete profile cache
            await self.profile_repo.deleteCache(uuid)
            profile = await self.profile_repo.get(uuid)
            return profile

    # Delete a profile data
    async def delete(self, uuid: str):
        ## check if profile exists
        if not await self.profile_repo.isExist(uuid):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        ## delete profile cache
        await self.profile_repo.deleteCache(uuid)
        ## delete profile
        await self.profile_repo.delete(uuid)

    # health check
    async def health(self):
        # return 200
        JSONResponse(content={"status": "ok"})
