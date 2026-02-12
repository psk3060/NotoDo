# routes/auth.py
from fastapi import APIRouter, Request, Response

from model import LoginRequest, LoginResponse, PublicKeyResponse, GenerateTokenResponse
from service.impl import AuthServiceImpl
from core.security import rsa_manager

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=LoginResponse)
async def login_proc(loginRequest : LoginRequest, request: Request, response: Response) :
    
    '''Login 처리 메소드
        1. IP 체크(5회) - 잠김 여부 파악(Redis TODO)
        2. 패스워드 복호화(RSA + AES 하이브리드)
        3. Token 발급 정책
            - Access Token : 로그인 할 때마다 
            - Refresh Token : 갱신 하였을 경우
    '''
    
    # TODO IP에서 5회 실패 했는가? (잠긴 상태인가?)
    authService = AuthServiceImpl()
    
    # 메시지
    returnMsg : str = ""
    
    # 평문으로 복호화
    plain_password = rsa_manager.decrypt_password_AES(loginRequest)
    
    user_id = loginRequest.userId
    
    result = await authService.login(loginRequest.userId, plain_password)
    
    client_ip = request.headers.get("x-forwarded-for") or request.client.host
    
    access_token = ""
    refresh_token = ""
    
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    if result :
        returnMsg = "로그인 성공"
        
        # Access Token 
        
        # 제거
        if request.cookies.get("access_token"):
            response.delete_cookie("access_token", path="/")
        
        # 발급
        access_token = await authService.generateToken(user_id, "access")
        
        # Access Token 
        
        
        # Refresh Token
        
        # Refresh Token : Redis에서 조회 → (Miss) PostgreSQL에서 조회 → (Miss) 새로 생성
        refresh_token = await authService.generateToken(user_id, "refresh")
        
        tokenResponse = GenerateTokenResponse(user_id = user_id, access_token = access_token, refresh_token = refresh_token)
        
        await authService.saveToken(tokenResponse, request, response)
        
        
        # TODO IP Redis 초기화
    else :
        # TODO IP에서 5회 실패 시 5분 잠금(Redis에서 카운트)
        returnMsg = "아이디 또는 비밀번호를 찾을 수 없습니다."

    return LoginResponse(success = result, message = returnMsg)

    
    
@router.get("/public-key", response_model=PublicKeyResponse)
async def get_publicKey() -> str : 
    '''Client에 RSA Public Key 전달'''
    
    return {
        "publicKey": rsa_manager.export_public_key_pem()
    }
    

@router.get("/logout")
def logout(respone : Response):
    '''
        로그아웃 로직
            1. 사용자가 로그아웃 버튼 클릭
            2. 쿠키에 담긴 accessToken으로 로그아웃 요청
            3. 서버에서 Refresh Token 기준으로 세션 식별 →  Refresh Token revoke (Redis + PostgreSQL)
            4. accessToken, refreshToken 쿠키 삭제
            5. 204 No Content 응답
    '''
    
    authService = AuthServiceImpl()
    authService.clear_auth_cookies(respone)
    

