# routes/auth.py

from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse

from db.postgres.client_config import get_pg_session

from service import TokenService
from service import RedisManageIpServiceImpl
from service import AuthService, TokenAuthServiceImpl
from service import UserServiceImpl

from service import get_token_service

from repository import UserBaseRepository

from model import LoginRequest, LoginResponse, PublicKeyResponse

from core.rsa_mamanger import rsa_manager

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def get_auth_service(
    session : AsyncSession = Depends(get_pg_session)
) -> AuthService:
    user_service = UserServiceImpl(UserBaseRepository(session))
    token_service = get_token_service('jwt')
    ip_service = RedisManageIpServiceImpl()
    
    return TokenAuthServiceImpl(token_service=token_service, user_service=user_service, ip_service=ip_service)


@router.post("/login", response_model=LoginResponse)
async def login_proc(
                        loginRequest : LoginRequest
                        , request: Request
                        , response: Response
                        , auth_service : AuthService = Depends(get_auth_service)
                        ) :
    return await auth_service.login(loginRequest, request, response)


@router.get("/public-key", response_model=PublicKeyResponse)
def get_publicKey() -> str : 
    '''Client에 RSA Public Key 전달'''
    
    return {
        "publicKey": rsa_manager.export_public_key_pem()
    }
    

@router.post("/logout")
async def logout(request : Request
            , response : Response
            , auth_service : AuthService = Depends(get_auth_service)):
    '''
        로그아웃 로직
            1. 사용자가 로그아웃 버튼 클릭
            2. Refresh Token revoke (Redis + PostgreSQL)
            3. ACCESS_TOKEN, REFRESH_TOKEN 삭제
            4. 프론트엔드에서 로그아웃 진행
    '''
    await auth_service.logout(request, response)
    
    return {"status_code" : 200, "message": "정상적으로 로그아웃 되었습니다."}
    


@router.post("/refresh")
async def refreshToken(request : Request, response: Response, token_service : TokenService = Depends(get_token_service)) :
    '''Refresh Token 갱신'''
    
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token :
        return JSONResponse(status_code=401,content={"code" : "empty_token", "message" : "토큰이 비어있습니다."})
    
    await token_service.reissue_refresh_token(refresh_token, request, response)
    
    return {"status_code" : 200, "message": "토큰이 갱신되었습니다."}
    
