from .custom_logger import get_logger
from fastapi import FastAPI
from mangum import Mangum
from .router import authorize as authorize_router
from .router import current as current_router
from .router import track as track_router

logger = get_logger(__name__)
logger.info("start")
logger.debug("debug: ON")

app = FastAPI(
    title="My Spotify API",
    version="0.0.1",
)
app.include_router(track_router.router, prefix="/track", tags=["track"])
app.include_router(current_router.router, prefix="/current", tags=["current"])
app.include_router(authorize_router.router, tags=["authorize"])


@app.get("/healthcheck")
def hello():
    """
    Return a greeting
    """
    logger.debug("healthcheck")
    logger.info("healthcheck")
    return {
        "status": "ok",
    }


handler = Mangum(app, lifespan="off")
