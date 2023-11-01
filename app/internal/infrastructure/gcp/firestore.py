# Path: ols_svc_sample/app/internal/infrastructure/gcp/firestore.py

import google.cloud.firestore as firestore
from ....dependencies import get_settings

settings = get_settings()

class Firestore:
    def __init__(self):
        self.client = firestore.AsyncClient(database=settings.firestore_database, project=settings.firestore_project_id)

    def getCollection(self):
        return self.client.collection(settings.firestore_collection)