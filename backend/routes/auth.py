# routes/auth.py
from service.impl.auth_service_impl import get_auth_service
from service.impl.ip_service import IpService
from service.impl.ip_service import get_ip_service
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse

from db.postgre_session import get_db

from model import LoginRequest, LoginResponse, PublicKeyResponse
from service.impl import AuthServiceImpl
from core.security import rsa_manager

from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=LoginResponse)
async def login_proc(
                        loginRequest : LoginRequest
                        , request: Request
                        , response: Response
                        , db: AsyncSession = Depends(get_db)
                        , ip_service : IpService = Depends(get_ip_service)
                        , authService : AuthServiceImpl = Depends(get_auth_service)
                        ) :
    
    '''Login 처리 메소드
        1. IP 체크(5회) - 잠김 여부 파악
        2. 패스워드 복호화(RSA + AES 하이브리드)
        3. Token 발급 정책
            - Access Token : 로그인 할 때마다 
            - Refresh Token : 갱신 하였을 경우
        
    '''
    
    returnMsg : str = ""
    
    ip = ip_service.get_ip_info(request)['client_ip']
    
    # print(await ip_service.debug_fail_by_ip(ip))
    
    if await ip_service.exists_block_ip(ip):
        returnMsg = "아이디 또는 비밀번호를 찾을 수 없습니다."
    else :
        # 정보 검증
        result = await authService.verifyLoginInfo(loginRequest, db)
        
        if result :
            # 기존 토큰 모두 revoke(reason = login)
            await authService.revoke_user_refresh_tokens(loginRequest.userId)
            
            await authService.saveToken(loginRequest.userId, 'login', request, response)
            
            # IP COUNT 초기화 - 성공 시
            await ip_service.delete_all_fail_ip(ip)
            
        else :
            # IP COUNT 1회 증가
            count = await ip_service.add_fail_ip(ip, loginRequest.userId)
            
            # IP에서 1분 동안 5회 실패 시 BLOCK IP에 등록(TTL : 5분) -> COUNT_IP 모두 제거
            if count is not None and count >= 5:
                await ip_service.block_ip(ip)
            
            
            returnMsg = "아이디 또는 비밀번호를 찾을 수 없습니다."

    return LoginResponse(success = result, message = returnMsg)


@router.get("/public-key", response_model=PublicKeyResponse)
def get_publicKey() -> str : 
    '''Client에 RSA Public Key 전달'''
    
    return {
        "publicKey": rsa_manager.export_public_key_pem()
    }
    

@router.post("/logout")
async def logout(request : Request
            , response : Response
            , authService : AuthServiceImpl = Depends(get_auth_service)):
    '''
        로그아웃 로직
            1. 사용자가 로그아웃 버튼 클릭
            2. Refresh Token revoke (Redis + PostgreSQL)
            3. ACCESS_TOKEN, REFRESH_TOKEN 삭제
            4. 프론트엔드에서 로그아웃 진행
    '''
    
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token :
        return JSONResponse(status_code=401,content={"code" : "empty_token", "message" : "토큰이 비어있습니다."})
    
    authService.deleteCookie(response)

    await authService.revoke_refresh_token(refresh_token, request, response)
    
    return None

@router.post("/refresh")
def refreshToken(request : Request, response: Response
                 , authService : AuthServiceImpl = Depends(get_auth_service)
                 ) :
    '''Refresh Token 갱신'''
    
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token :
        return JSONResponse(status_code=401,content={"code" : "empty_token", "message" : "토큰이 비어있습니다."})
    
    authService.reissue_refresh_token(refresh_token, response)
    
    return None