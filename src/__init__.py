from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.middleware.error_middleware import register_error_handlers
from .router.root_router import root_router
from src.database.engine import db
from contextlib import asynccontextmanager


class AppFactory:
    def __init__(self, title: str = "VIDEO STREAMING APP", version: str = "1.0.0"):
        self.app = FastAPI(
            title=title,
            version=version,
            lifespan=self.lifespan_context(),
        )
        self.configure_cors()
        self.configure_middlewares()
        self.configure_routes()
        self.initialize_routes()

    def configure_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def configure_middlewares(self):
        register_error_handlers(self.app)

    def configure_routes(self):
        @self.app.get("/test")
        async def test():
            return {"message": "hello"}

        @self.app.get("/")
        async def root():
            return {"message": "Hello World 🌍"}

    def initialize_routes(self):
        for route in root_router:
            self.app.include_router(route["router"], prefix=route["prefix"])
            print(f"✅ Registered router with prefix: {route['prefix']}")

    def get_app(self) -> FastAPI:
        return self.app

    def lifespan_context(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await db.init()
            print("✅ Database initialized")
            yield
            await db.close()
            print("✅ Database closed")

        return lifespan


app = AppFactory().get_app()
