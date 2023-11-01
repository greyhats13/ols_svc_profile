# Path: ols_svc_sample/app/infrastructure/databases/mongodb.py

from motor import motor_asyncio
from ....internal.config import get_settings

class Mongo:
    def __init__(self):
        self.settings = get_settings()
        ## Set mongo connection string
        self.uri = f"mongodb://{self.settings.mongo_user}:{self.settings.mongo_pass}@{self.settings.mongo_host}:{self.settings.mongo_port}/{self.settings.mongo_dbname}?authSource={self.settings.mongo_auth_source}&authMechanism={self.settings.mongo_auth_mechanism}&directConnection={self.settings.mongo_direct_connection}"
        self._client = motor_asyncio.AsyncIOMotorClient(self.uri)

    def getCollection(self):
        ## Get database
        collection = self._client[self.settings.mongo_dbname][self.settings.mongo_collection]
        return collection