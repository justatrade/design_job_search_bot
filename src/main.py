from contextlib import asynccontextmanager

from fastapi import FastAPI
from uvicorn import Config, Server

from src.api import auth, chats, config, filters, health
from src.api.deps import PROTECTED
from src.core.settings import settings
from src.core.logger import setup_logging
from src.telegram.instance import tg


setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    tg.start_background_listener()
    yield

app = FastAPI(
    title=settings.app.app_name,
    lifespan=lifespan,
    version="0.1.0",
    docs_url="/swagger",
)

app.include_router(health.router, dependencies=PROTECTED)
app.include_router(auth.router, dependencies=PROTECTED)
app.include_router(chats.router, dependencies=PROTECTED)
app.include_router(config.router, dependencies=PROTECTED)
app.include_router(filters.router, dependencies=PROTECTED)

if __name__ == "__main__":
    config = Config(
        app="src.main:app",
        host=settings.app.listen_address,
        port=settings.app.listen_port,
        reload=True
    )
    server = Server(config)
    server.run()
