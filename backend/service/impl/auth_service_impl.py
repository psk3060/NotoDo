from pydantic import BaseModel
from core.security import verify_password
from db.mongo import User
import os, jwt, uuid, json, hashlib
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Response
from model import LoginRequest
from core.security import rsa_manager

from db.redis import redis_container

class AuthServiceImpl(BaseModel) : 
    
    async def verifyLoginInfo(self, loginRequest : LoginRequest) -> bool:
        '''
            회원 정보 검증
                - ID(정보 검색)
                - PASSWORD
        '''
        user = await User.find_one(User.userId == loginRequest.userId)
        
        if not user:
            raise ValueError("User not found in DB")
        
        plain_password = await rsa_manager.decrypt_password_AES(loginRequest)
        
        return verify_password(plain_password, user.password)
    
    
    def deleteCookie(self, response: Response) :
        '''Token 삭제
                - 삭제 기준 : 로그아웃 할 때마다'''
                
        # 쿠키 삭제
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/auth")
        
        
    
    
    def generateToken(self, user_id : str, token_type : str, SECRET_KEY : str, TOKEN_ALGORITHM : str, response : Response) -> str:
        '''Token(Access, Refresh) 생성'''
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', '') 
        
        if token_type == "access":
            expire = datetime.now(timezone.utc) + timedelta(minutes=15) # seconds=10
        elif token_type == "refresh":
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        else :
            raise HTTPException(
                status_code=400,
                detail="잘못된 토큰 타입입니다."
            )
        
        if not SECRET_KEY:
            raise RuntimeError(
                f"{token_type.upper} secret_key가 설정되지 않았습니다."
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
        
        return jwt.encode(payload, SECRET_KEY, algorithm=TOKEN_ALGORITHM, headers = headers)
    
    
    def saveCookie(self, token_type : str, token : str, response : Response) : 
        
        key = f"{token_type.lower()}_token"
        
        max_age = 60 * 15
        token_path = "/"
        
        if token_type == "refresh":
            max_age = 7 * 24 * 3600
            token_path = "/auth"
            
        
        # 토큰을 Cookie에 저장
        response.set_cookie(
            key=key,
            value=token,
            httponly=True,
            secure=os.getenv('TODO_ENV') == "prod",
            max_age=max_age,
            samesite="lax",
            path=token_path
        )
    
    async def saveToken(self, user_id : str, response : Response) :
        ''' Token 생성
            1. 생성 기준
                - 로그인 할 때마다
                - Refresh Token 갱신 할 때마다
            2. 세션 정책 : 단일 세션 정책(전부 제거)
                - 다중 세션 정책 → 동일 device_id만 제거(다중 디바이스 관리 시)
            3. DB 별 Refresh Token 관점(Refresh Token은 Hash 값만 저장)
                - Redis : 세션 접근(성능), TTL 설정
                - PostgreSQL : 세션 관리(이력 관리 / 권한 관리)
            4. Cookie 저장 옵션 : Secure=True, SameSite=Lax, HttpOnly
        '''
        
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', '') 
        
        if not TOKEN_ALGORITHM:
            raise RuntimeError("토큰 알고리즘이 설정되지 않았습니다.")
        
        refresh_token_SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY', '')
        
        # 1. Refresh Token 생성
        refresh_token = self.generateToken(user_id, 'refresh', refresh_token_SECRET_KEY, TOKEN_ALGORITHM, response)
        
        if not refresh_token:
            raise RuntimeError("Refresh Token이 생성되지 않았습니다.")
        
        # 2. Payload 확보(1에서 생성한 토큰 Decode)
        refresh_payload = jwt.decode(refresh_token, refresh_token_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        
        user_id = refresh_payload['user_id']
        
        # 3. 기존 Refresh 삭제
        await self.delete_user_refresh_tokens(user_id)
        
        # 4. Redis에 저장
        token_hash = self.hash_jwt(refresh_token)
        key = f"refresh:{user_id}:{refresh_payload['jti']}"
        
        await redis_container.refresh.set(key, token_hash, ex=60*60*24*7)
        
        # 5. Access Token 생성
        access_token = self.generateToken(user_id, 'access', os.getenv('ACCESS_TOKEN_SECRET_KEY', ''), TOKEN_ALGORITHM, response)
        
        if not access_token:
            raise RuntimeError("Access Token이 생성되지 않았습니다.")
        
        # 6. Access Token, Refresh Token 쿠키에 저장
        self.saveCookie('access', access_token, response)
        self.saveCookie('refresh', refresh_token, response)
        
        return None
    
    async def delete_user_refresh_tokens(self, user_id: str):
        pattern = f"refresh:{user_id}:*"
        cursor = 0
        keys_to_delete = []

        while True:
            cursor, keys = await redis_container.refresh.scan(cursor=cursor, match=pattern, count=100)
            
            keys_to_delete.extend(keys)
            
            if cursor == 0:
                break

        if keys_to_delete:
            await redis_container.refresh.delete(*keys_to_delete)
    
    
    
    def hash_jwt(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
            
    def decodeToken(self, token : str) -> str:
        SECRET_KEY = os.getenv('ACCESS_TOKEN_SECRET_KEY', '')
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', '') 
        TOKEN_ISSUER = os.getenv('TOKEN_ISSUER', 'localhost')
        
        try:
            
            if not SECRET_KEY:
                raise Exception("SECRET_KEY가 설정되지 않았습니다.")
            
            if not TOKEN_ALGORITHM:
                raise Exception("토큰 알고리즘이 설정되지 않았습니다.")

            payload = jwt.decode(token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM], issuer = TOKEN_ISSUER)
            
            payload["code"] = "success"
            payload["message"] = "토큰이 정상적으로 인코딩 되었습니다."
            
            return json.dumps(payload)
        
        except Exception as e:
            raise e
            
    
    
    async def reissue_refresh_token(self, refresh_token : str, response : Response) :
        
        SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY', '')
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', '') 
        
        try :
            if not SECRET_KEY:
                raise Exception("SECRET_KEY가 설정되지 않았습니다.")
            
            if not TOKEN_ALGORITHM:
                raise Exception("토큰 알고리즘이 설정되지 않았습니다.")
            
            token_hash = self.hash_jwt(refresh_token)
            
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM])

            key = f"refresh:{payload['user_id']}:{payload['jti']}"
            
            stored_hash = await redis_container.refresh.get(key)
            
            if stored_hash is None:
                raise Exception("Refresh Token이 존재하지 않습니다.")

            if stored_hash.decode() != token_hash:
                raise Exception("Refresh Token이 일치하지 않습니다.")
            
            user_id = payload.get("user_id")
            
            # 토큰 발급(DB, Redis, 쿠키에 저장하는 로직도 있기 때문에 saveToken)
            await self.saveToken(user_id, response)
            
        except Exception as e:
            raise e
        