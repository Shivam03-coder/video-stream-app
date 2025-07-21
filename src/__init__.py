from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.middleware.error_middleware import register_error_handlers
from .router.root_router import root_router


class AppFactory:
    def __init__(self, title: str = "VIDEO STREAMING APP", version: str = "1.0.0"):
        self.app = FastAPI(
            title=title,
            version="1.0.0",
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


app = AppFactory().get_app()
