from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/login")
async def login():
    return {"message": "Logged in"}

@auth_router.post("/register")
async def register():
    return {"message": "Registered"}
