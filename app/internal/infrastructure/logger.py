# Path: ols_svc_sample/app/internal/infrastructure/logger.py

import uvicorn, logging
from fastapi.logger import logger

class Logger:
    def __init__(self):
        self.log = logger

    def getLogger(self):
        ## set fastapi log level
        self.log.setLevel(logging.DEBUG)
        ## set stream handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ## set log format
        formatter = logging.Formatter('%(levelprefix)s %(asctime)s %(message)s')
        FORMAT: str = "%(levelprefix)s %(asctime)s | %(message)s"
        ## set Uvicorn default log format
        formatter = uvicorn.logging.DefaultFormatter(FORMAT)
        ch.setFormatter(formatter)
        if not self.log.hasHandlers():
            self.log.addHandler(ch)
        return self.log

log = Logger().getLogger()