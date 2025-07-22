from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.api import api_routes
from src.common.logging import configure_logging, LogLevels
from src.database.engine import db
from contextlib import asynccontextmanager


class AppFactory:
    def __init__(self, title: str = "VIDEO STREAMING APP", version: str = "1.0.0"):
        self.app = FastAPI(
            title=title, version=version, lifespan=self.lifespan_context()
        )
        self.configure_logging()
        self.configure_cors()
        self.register_routes()
        self.register_test_routes()

    def configure_logging(self):
        configure_logging(LogLevels)

    def configure_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def register_routes(self):
        for api in api_routes:
            self.app.include_router(api["router"], prefix=api["route"])

    def register_test_routes(self):
        @self.app.get("/test")
        async def test():
            return {"message": "hello"}

        @self.app.get("/")
        async def root():
            return {"message": "Hello World 🌍"}

    def lifespan_context(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await db.init()
            print("✅ Database initialized")
            yield
            await db.close()
            print("✅ Database closed")

        return lifespan

    def get_app(self) -> FastAPI:
        return self.app


# Entry point for FastAPI to detect
app = AppFactory().get_app()
