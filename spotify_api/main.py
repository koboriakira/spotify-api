from mangum import Mangum
from fastapi import FastAPI, Header
from starlette.middleware.cors import CORSMiddleware
from datetime import date as DateObject
from datetime import datetime as DateTimeObject
from datetime import time as TimeObject
from datetime import timedelta
from typing import Optional
import os
from custom_logger import get_logger

logger = get_logger(__name__)
logger.info("start")
logger.debug("debug: ON")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
ENVIRONMENT = os.environ.get("ENVIRONMENT")

def valid_saccess_token(secret: str) -> None:
    if ENVIRONMENT == "dev":
        return
    # SPOTIFY_CLIENT_SECRETを使って、アクセストークンを検証する
    if secret != SPOTIFY_CLIENT_SECRET:
        raise Exception("invalid secret: " + secret)


app = FastAPI(
    title="My Spotify API",
    version="0.0.1",
)


@app.get("/healthcheck")
def hello():
    """
    Return a greeting
    """
    logger.debug("healthcheck")
    logger.info("healthcheck")
    return {
        'status': 'ok',
    }


handler = Mangum(app, lifespan="off")
