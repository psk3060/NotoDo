# backend/routes/auth.py
from fastapi import APIRouter, Request

from model import LoginRequest, LoginResponse, PublicKeyResponse
from service.impl.auth_service_impl import AuthServiceImpl
from core.security import rsa_manager

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=LoginResponse)
async def user_authenticate(loginRequest : LoginRequest, request: Request) -> bool :
    
    # TODO IP에서 5회 실패 했는가? (잠긴 상태인가?)
    authService = AuthServiceImpl()
    
    message = ''
    plain_password = rsa_manager.decrypt_password(loginRequest.encryptedPassword)
    
    result = await authService.login(loginRequest.userId, plain_password)
    
    client_ip = request.headers.get("x-forwarded-for") or request.client.host
    
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    if result :
        message = '로그인 성공'
        # TODO Access Token과 Refresh Token 발급
        
        # TODO Refresh Token은 DB에 저장
        
        # TODO Access Token과 Refresh Token 모두 Cookie에 저장
        
        # TODO Redis 초기화
    else :
        # TODO IP에서 5회 실패 시 5분 잠금(Redis에서 카운트)
        message = '아이디 또는 비밀번호를 찾을 수 없습니다.'
    
    return {
        "success" : result
        , "message" : message
    }
    
@router.get("/public-key", response_model=PublicKeyResponse)
async def get_publicKey() -> str : 
    
    return {
        "publicKey": rsa_manager.get_public_key_pem()
    }