from fastapi import FastAPI
from src.module.auth.controller import auth_router

app = FastAPI()

# Define your API routes in a list
api_routes = [
    {"route": "/auth", "router": auth_router}
]

