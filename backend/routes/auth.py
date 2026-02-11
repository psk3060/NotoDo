# routes/auth.py
from fastapi import APIRouter, Request

from model import LoginRequest, LoginResponse, PublicKeyResponse
from service.impl.auth_service_impl import AuthServiceImpl
from core.security import rsa_manager

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=LoginResponse)
async def login_proc(loginRequest : LoginRequest, request: Request) -> bool :
    
    '''Login 처리 메소드
        1. IP 체크(5회) - 잠김 여부 파악
        2. 패스워드 복호화
        3. Token 발급
    '''
    
    # TODO IP에서 5회 실패 했는가? (잠긴 상태인가?)
    authService = AuthServiceImpl()
    # 메시지
    message = ''
    
    # RSA는 Deprecated
    # plain_password = rsa_manager.decrypt_password(loginRequest.encryptedPassword)
    
    # 평문으로 복호화
    plain_password = rsa_manager.decrypt_password_AES(loginRequest)
    
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
    '''Client에 RSA Public Key 전달'''
    
    return {
        "publicKey": rsa_manager.export_public_key_pem()
    }