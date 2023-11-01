# Path: ols_svc_sample/app/internal/infrastructure/aws/sts.py

import boto3
from functools import lru_cache
from ....internal.config import get_settings

settings = get_settings()

class STS:
    def __init__(self):
        self.sts_client = boto3.client('sts')
        self.settings = get_settings()

    def assume_role(self):
        assumed_role = self.sts_client.assume_role(
            RoleArn=self.settings.profile_role_arn,
            RoleSessionName=self.settings.profile_session_name
        )

        # Extract the temporary credentials
        return assumed_role['Credentials']

@lru_cache()
def get_aws_credentials():
    credentials = STS().assume_role()
    return credentials

