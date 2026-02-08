# backend/routes/auth.py
from fastapi import APIRouter

from model.LoginParam import LoginParam

from service.impl.auth_service_impl import AuthServiceImpl

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login")
async def user_authenticate(loginParam : LoginParam) -> bool :
    
    authService = AuthServiceImpl()
    
    result = await authService.login(loginParam.userId, loginParam.password)
    
    return result
    