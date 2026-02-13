from pydantic import BaseModel
from core.security import verify_password
from db.mongo import User
from model import GenerateTokenResponse
import os, jwt, uuid, json
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Request, Response


class AuthServiceImpl(BaseModel) : 
    
    # Login Check
    async def login(self, userId:str, password:str) -> bool:
        user = await User.find_one(User.userId == userId)
        
        if not user:
            raise ValueError("User not found in DB")
        
        result = verify_password(password, user.password)
        
        return result
    
    
    async def saveToken(self, user_id : str, request : Request, response : Response):
        '''
            Token 저장
            1. (정책 기준) 기존 Refresh Token 정리(TODO)
                - Redis : 기존 RT 제거
                - PostgreSQL : 기존 세션 revoke 처리 (이력 유지)
                    - 단일 세션 정책 → 전부 제거
                    - 다중 세션 정책 → 동일 device_id만 제거
            2. 새 Refresh Token을 Redis에 저장(TODO 유효성 인증 기준)
            3. Refresh Token 메타데이터를 PostgreSQL에 저장 (세션 이력 / 권한 회수 대상 관리, TODO)
            4. Access / Refresh Token을 Secure=True, SameSite=Lax, HttpOnly Cookie에 저장
        '''
        # 제거
        if request.cookies.get("access_token"):
            response.delete_cookie("access_token", path="/")
        
        service = AuthServiceImpl()
        
        # 1. Access Token 생성
        access_token = await service.encodeToken(user_id, "access")
        
        # 2. Refresh Token 생성
        refresh_token = await service.encodeToken(user_id, "refresh")
        
        # tokenPair = GenerateTokenResponse(user_id = user_id, access_token = access_token, refresh_token = refresh_token)
        
        # Access / Refresh Token을 Secure=True, SameSite=Lax, HttpOnly Cookie에 저장
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=os.getenv('TODO_ENV') == "prod",
            samesite="lax",
            max_age=60 * 30,          # 30분
            path="/"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            path="/auth/refresh",
            httponly=True,
            secure=os.getenv('TODO_ENV') == "prod",
            samesite="lax",
        )
        
        return None
    
    
    async def encodeToken(self, user_id : str, token_type : str) -> str:
        '''Token(Access, Refresh) 생성'''
        SECRET_KEY = ""
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', '') 
        
        if token_type == "access":
            SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY', '')
            expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        elif token_type == "refresh":
            SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY', '')
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        else :
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="잘못된 토큰 타입입니다."
            )
        
        if not SECRET_KEY:
            raise RuntimeError(
                f"{token_type.upper} SECRET_KEY가 설정되지 않았습니다."
            )
        
        if not TOKEN_ALGORITHM:
            raise RuntimeError(
                f"토큰 알고리즘이 설정되지 않았습니다."
            )
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "type" : token_type,
            "iat" : datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
            "sid" : str(uuid.uuid4()),
            "iss" : os.getenv('TOKEN_ISSUER', 'localhost')
        }
        
        headers = {
            "kid": str(uuid.uuid4())
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256", headers = headers)
    
    
        
    def decodeToken(self, token : str) -> str:
        SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY', '')
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', '') 
        TOKEN_ISSUER = os.getenv('TOKEN_ISSUER', 'localhost')
        
        try:
            
            if not SECRET_KEY:
                raise Exception()
            
            if not TOKEN_ALGORITHM:
                raise RuntimeError(
                    f"토큰 알고리즘이 설정되지 않았습니다."
                )
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM], issuer = TOKEN_ISSUER)
            
            return json.dumps(payload)
        
        except jwt.ExpiredSignatureError:
            return json.dumps({
                "type" : "tee"
                , "message" : "Token expired"
            })
        
        except jwt.InvalidTokenError:
            return json.dumps({
                "type" : "tie"
                , "message" : "Invalid token"
            })
        except :
            return json.dumps({
                "type" : "sys"
                , "message" : "Service Error"
            })
            
    
    
    
    
def clear_auth_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth/refresh")