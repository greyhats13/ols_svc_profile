# Path: ols_svc_sample/app/internal/infrastructure/repositories/gcp/profile_repository.py

# from datetime import timedelta
from fastapi import HTTPException, status
from graphql import GraphQLError
from ....domain.interfaces.profile_interface import ProfileInterface
from ....domain.models.profile import Profile, ProfileCreate, ProfileUpdate
from ...logger import log
from .....internal.config import get_settings
from ....infrastructure.gcp.firestore import Firestore

settings = get_settings()

class ProfileRepository(ProfileInterface):
    # Profile Repository constructor
    def __init__(self, transport: str = "http"):
        ## Transport
        self.transport = transport
        ## Initialize mongo and redis
        self.collection = Firestore().getCollection()
    # MongoDb
    ## Check the existence of data
    async def isExist(self, id: str) -> bool:
        try:
            ### Get datum from mongodb
            datum = await self.collection.document(id).get()
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
            datum = await self.collection.where('email', '==', datum.email).get()
            ### add datum uuid to datum
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
    async def list(self, order_by: str = "uuid", limit: int = 1, offset: int = 10) -> list[Profile]:
        ## List Data
        try:
            ## ref: https://cloud.google.com/firestore/docs/samples/firestore-query-cursor-pagination-async
            first_query = self.collection.order_by(order_by).limit(limit)
            # Get the last document from the results
            docs = [d async for d in first_query.stream()]
            last_doc = list(docs)[-1]
            # Construct a new query starting at this document
            # Note: this will not have the desired effect if
            # multiple profile have the exact same profile value
            last_pop = last_doc.to_dict()[order_by]

            next_query = (
                self.collection.order_by(order_by).start_at({order_by: last_pop}).limit(offset)
            )
            new_docs = [d async for d in next_query.stream()]
            data = [Profile(**d.to_dict()) for d in new_docs]
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
        return data
    
    ## Get datum by id
    async def get(self, id: str) -> Profile:
        try:
            ### Retrieve a datum
            datum = await self.collection.document(id).get()
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
            await self.collection.document(datum.uuid).set(datum.model_dump())
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
            # Update the rest of the fields
            await self.collection.document(id).update(datum.model_dump(exclude_unset=True))
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
            await self.collection.document(id).delete()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = {
                    "msg": "Cannot delete profile datum",
                    "reason": str(e)
                }
            )