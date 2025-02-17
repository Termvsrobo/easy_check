from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from handlers.auth import auth_router
from handlers.notes import notes_router
from utils import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

api_router = APIRouter(prefix='/api')

api_router.include_router(auth_router)
api_router.include_router(notes_router)

app.include_router(api_router)
