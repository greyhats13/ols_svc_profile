# app/internal/infrastructure/repositories/local/profile_repository.py

from datetime import timedelta
from fastapi import HTTPException, status
from graphql import GraphQLError
from ....domain.interfaces.profile_interface import ProfileInterface
from ....domain.models.profile import Profile, ProfileCreate, ProfileUpdate
from ...databases.mongodb import Mongo
from ....adapter.event_handler import redis
from ...logger import log

class ProfileRepository(ProfileInterface):
    # Profile Repository constructor
    def __init__(self, transport: str = "http"):
        ## Transport
        self.transport = transport
        ## Get profile collection
        self.collection = Mongo().getCollection()

    # MongoDb
    ## Check the existence of data
    async def isExist(self, id: str) -> bool:
        try:
            ### Get datum from mongodb
            datum = await self.collection.find_one({"uuid": id})
            ### Check if datum exists in mongodb
            if datum:
                return True
            else:
                return False
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "msg": "Cannot check if profile datum exists",
                    "reason": str(e)
                }
            )

    ### check datum integrity
    async def isConflict(self, datum: ProfileCreate ) -> bool:
        try:
            ### Check if datum id already exist in mongodb
            datum = await self.collection.find_one({"email": datum.email})
            if datum:
                return True
            else:
                return False
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "msg": "Cannot check profile datum integrity",
                    "reason": str(e)
                }
            )

    ## List data with pagination
    async def list(self, skip: int = 0, limit: int = 10) -> list[Profile]:
        ## List Data
        try:
            data = await self.collection.find().skip(skip).limit(limit).to_list(length=limit)
        except Exception as e:
            if self.transport == "http":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = {
                        "msg": "Cannot list profile data",
                        "reason": str(e)
                    }
                )
            elif self.transport == "graphql":
                raise GraphQLError(
                    message = "Cannot list profile data",
                    extensions = {
                        "reason": str(e)
                    }
                )
        # for datum in data:
            ### convert _id to string
            # datum["_id"] = str(datum["_id"])
        return data

    ## Get datum by id
    async def get(self, id: str) -> Profile:
        try:
            ### Retrieve a datum
            datum = await self.collection.find_one({"uuid": id})
        except Exception as e:
            ### Raise exception the transport is http
            if self.transport == "http":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = {
                        "msg": "Cannot get profile datum",
                        "reason": str(e)
                    }
                )
            ### Raise exception the transport is graphql
            elif self.transport == "graphql":
                raise GraphQLError(
                    message = "Cannot get profile datum",
                    extensions = {
                        "reason": str(e)
                    }
                )
        return datum
    
    ## Create datum
    async def create(self, datum: ProfileCreate)-> ProfileCreate:
        try:
            ## create datum in mongodb
            temp = await self.collection.insert_one(datum)
            return datum
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "msg": "Cannot create profile datum",
                    "reason": str(e)
                }
            )
        
    ## Update a datum
    async def update(self, id: str, datum: ProfileUpdate):
        try:
            await self.collection.update_one({"uuid": id}, {"$set": datum})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "msg": "Cannot update profile datum",
                    "reason": str(e)
                }
            )
        
    ## Delete a datum
    async def delete(self, id: str):
        try:
            ### delete datum from mongodb
            await self.collection.delete_one({"uuid": id})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "msg": "Cannot delete profile datum",
                    "reason": str(e)
                }
            )
        
    # Redis
    ### get datum from redis
    async def getCache(self, id: str) -> str:
        try:
            ### get datum from redis
            value = await redis["client"].get(f"profile:{id}")
            if value:
                log.debug(f"Profile datum is retrieved from Redis")
            else:
                log.debug(f"Profile datum is not retrieved from Redis")
            return value
        except Exception as e:
            if self.transport == "http":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = {
                        "msg": "Cannot get profile datum from Redis",
                        "reason": str(e)
                    }
                )
            elif self.transport == "graphql":
                raise GraphQLError(
                    message="Cannot get profile datum from Redis",
                    extensions={
                        "reason": str(e)
                    }
                )

    ## set datum to redis with ttl
    async def setCache(self, id: str, profile: Profile):
        try:
            ### set profile data to redis with ttl
            is_cache = await redis["client"].setex(f"profile:{id}", timedelta(seconds=redis['ttl']), profile)
            if is_cache:
                log.debug(f"Profile datum is set to Redis with ttl {redis['ttl']} seconds")
            else:
                log.debug(f"Profile datum is not set to Redis")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "error": "Cannot set profile datum to Redis",
                    "reason": str(e)
                }
            )
        
    ## delete datum from redis
    async def deleteCache(self, id: str):
        try:
            ### delete datum from redis and get number of deleted keys
            num = await redis["client"].delete(f"profile:{id}")
            if num >= 1:
                log.debug(f"Profile datum is deleted from Redis")
            else:
                log.debug(f"Profile datum is not deleted from Redis")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "error": "Cannot delete profile datum from Redis",
                    "reason": str(e)
                }
            )
        
    ## get redis ttl
    async def getTtl(self, id: str) -> int:
        try:
            ### get redis ttl
            ttl = await redis["client"].ttl(f"profile:{id}")
            return ttl
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "error": "Cannot get ttl from Redis",
                    "reason": str(e)
                }
            )