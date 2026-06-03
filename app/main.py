from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.web.routes import router
from app.infrastructure.config import Settings
from app.infrastructure.database import init_db
from app.infrastructure.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    settings = Settings()
    application = FastAPI(
        title="Eciwise IA - Student Performance Predictor",
        version="1.0.0",
    )

    # CORS restringido a los orígenes configurados (el front / APIM).
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
    )

    application.include_router(router)

    @application.on_event("startup")
    def on_startup() -> None:
        init_db()

    return application


app = create_app()
