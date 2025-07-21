from fastapi import APIRouter, HTTPException
from src.module.auth.auth_schema import SignUpRequest
from src.module.auth.auth_service import AuthService
from src.utils.error_utils import ValidationError

auth_router = APIRouter(tags=["Auth"])


@auth_router.post("/sign_up")
async def register(user_data: SignUpRequest):
    try:
        response = AuthService.sign_up(user_data)
        return {"message": "User registered successfully", "data": response}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
