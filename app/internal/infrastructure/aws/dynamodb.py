# Path: ols_svc_sample/app/internal/infrastructure/aws/dynamodb.py

import boto3
from ....internal.config import get_settings
from .sts import get_aws_credentials
# from ...infrastructure.logger import log

class DynamoDB:
    def __init__(self):
        self.settings = get_settings()

    def get_table(self):
        if self.settings.use_irsa:
            self.client = boto3.resource(
                "dynamodb",
                region_name=self.settings.aws_region,
            )
            return self.client.Table(self.settings.dynamodb_table)
        else:
            credentials = get_aws_credentials()
            # log.debug(f"STS: {credentials}")
            self.client = boto3.resource(
                "dynamodb",
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=self.settings.aws_region,
            )
            table = self.client.Table(self.settings.dynamodb_table)
            # log.debug(f"DynamoDb Table: {table}")
            return table