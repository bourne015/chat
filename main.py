import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.responses import PlainTextResponse
from starlette.middleware.cors import CORSMiddleware

from api.v1 import api_router
from core.config import settings


root = APIRouter()

@root.get("/")
def read_root() -> dict:
    return PlainTextResponse("test chatgpt by fan")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    app.include_router(root)
    app.include_router(api_router, prefix=settings.API_V1_STR)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="debug"
    )
