# Path: ols_svc_sample/app/internal/infrastructure/repositories/aws/profile_repository.py

# from datetime import timedelta
from boto3.exceptions import Boto3Error
from fastapi import HTTPException, status
from graphql import GraphQLError
from ....domain.interfaces.profile_interface import ProfileInterface
from ....domain.models.profile import Profile, ProfileCreate, ProfileUpdate
from ...logger import log
from ....adapter.event_handler import dynamodb

class ProfileRepository(ProfileInterface):
    def __init__(self, transport: str = "http"):
        self.transport = transport

    async def isExist(self, id: str) -> bool:
        try:
            response = await dynamodb["table"].get_item(Key={'uuid': id})
            return "Item" in response
        except Boto3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "msg": "Cannot check if profile datum exists",
                    "reason": str(e),
                },
            )
            
    async def isConflict(self, datum: ProfileCreate) -> bool:
        try:
            response = await dynamodb["table"].query(
                IndexName='email-index',
                KeyConditionExpression='email = :email_val',
                ExpressionAttributeValues={
                    ':email_val': datum.email
                }
            )
            return "Items" in response and len(response["Items"]) > 0
        except Boto3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "msg": "Cannot check profile datum integrity",
                    "reason": str(e),
                },
            )

    async def list(self, offset: int = 0, limit: int = 10) -> list:
        try:
            response = await dynamodb["table"].scan(
                Limit=limit,
                ExclusiveStartKey={'uuid': str(offset)}
            )
            return response.get('Items', [])
        except Boto3Error as e:
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

    async def get(self, id: str) -> Profile:
        try:
            response = await dynamodb["table"].get_item(Key={'uuid':id})
            return response
        except Boto3Error as e:
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

    async def create(self, datum: ProfileCreate) -> ProfileCreate:
        try:
            response = await dynamodb["table"].put_item(Item=datum.model_dump())
            log.debug("Create Response: %s", response)
            if response["ResponseMetadata"]["HTTPStatusCode"] < 500:
                return datum
        except Boto3Error as e:
            raise HTTPException(
                status_code=response["ResponseMetadata"]["HTTPStatusCode"],
                detail={"msg": "Cannot create profile datum", "reason": str(e)}
            )

    async def update(self, id: str, datum: ProfileUpdate):
        try:
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in datum.model_dump().items():
                if value is not None:  # Skip null or None value
                    update_expression += f"#{key} = :{key}, "
                    expression_attribute_values[f":{key}"] = value
                    expression_attribute_names[f"#{key}"] = key

            update_expression = update_expression.rstrip(", ")  # Remove trailing comma

            update  = await dynamodb["table"].update_item(
                Key={'uuid': id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )
            # log.debug("Update: %s", update)
            return update
        except Boto3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"msg": "Cannot update profile datum", "reason": str(e)}
            )

    async def delete(self, id: str):
        try:
            await dynamodb["table"].delete_item(Key={'uuid': id})
        except Boto3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"msg": "Cannot delete profile datum", "reason": str(e)}
            )