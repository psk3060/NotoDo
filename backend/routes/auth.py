# routes/auth.py
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from model import LoginRequest, LoginResponse, PublicKeyResponse
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
    
    result = await authService.login(user_id, plain_password)
    
    if result :
        returnMsg = "로그인 성공"
        
        await authService.saveToken(user_id, request, response)
        
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
    

@router.post("/logout")
def logout(request : Request, response : Response):
    '''
        로그아웃 로직
            1. 사용자가 로그아웃 버튼 클릭
            2. 쿠키에 담긴 accessToken으로 로그아웃 요청
            3. 서버에서 Refresh Token 기준으로 세션 식별 →  Refresh Token revoke (Redis + PostgreSQL)
            4. accessToken, refreshToken 쿠키 삭제
            5. 프론트엔드에서 로그아웃 진행
    '''
    
    authService = AuthServiceImpl()
    authService.clear_auth_cookies(response)
    
    return True

@router.post("/refresh")
async def refreshToken(request : Request, response: Response) :
    '''Refresh Token 갱신(TODO)'''
    
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token :
        return JSONResponse(status_code=401,content={"code" : "empty_token", "message" : "토큰이 비어있습니다."})
    
    
    authService = AuthServiceImpl()
    
    await authService.renewal_refresh_token(refresh_token, request, response)
    
    return None