import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import PROJECT_NAME, VERSION, DSN
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.api.routes import router as api_router


def get_application():
    app = FastAPI(title=PROJECT_NAME, version=VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))

    app.include_router(api_router, prefix="/api")

    return app


sentry_sdk.init(
    dsn=DSN,
    traces_sample_rate=1.0
)

app = get_application()
