from pydantic import BaseModel
from core.security import verify_password
from db.mongo import User
from model import GenerateTokenResponse
import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status, Request, Response

class AuthServiceImpl(BaseModel) : 
    
    # Login Check
    async def login(self, userId:str, password:str) -> bool:
        user = await User.find_one(User.userId == userId)
        
        if not user:
            raise ValueError("User not found in DB")
        
        result = verify_password(password, user.password)
        
        return result
    
    async def generateToken(self, user_id : str, token_type : str) -> str:
        '''Token(Access, Refresh) 생성'''
        SECRET_KEY = ""
        
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
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "type" : token_type
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    
    
    async def saveToken(self, tokenPair : GenerateTokenResponse, request : Request, response : Response):
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
        
        # Access / Refresh Token을 Secure=True, SameSite=Lax, HttpOnly Cookie에 저장
        response.set_cookie(
            key="access_token",
            value=tokenPair.access_token,
            httponly=True,
            secure=os.getenv('TODO_ENV') == "prod",
            samesite="lax",
            max_age=60 * 30,          # 30분
            path="/"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=tokenPair.refresh_token,
            path="/auth/refresh",
            httponly=True,
            secure=os.getenv('TODO_ENV') == "prod",
            samesite="lax",
        )
        
        return None
    
    
def clear_auth_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth/refresh")