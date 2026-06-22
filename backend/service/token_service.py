import os, jwt, uuid, logging

from abc import ABC, abstractmethod
from fastapi import HTTPException, Response, Request
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from model.auth.refresh_token_log import RefreshTokenLogDTO
from repository.auth_repository import RefreshTokenLogRepository
from config.redis_setup import redis_container

from utils.string_utils import replace_hash_string

load_dotenv()

logger = logging.getLogger(__name__)

def get_token_service(token_type : str | None = 'jwt'):
    # token_type 환경변수로
    if token_type == 'jwt':
        return JwtTokenServiceImpl(RefreshTokenLogRepository())
    

class TokenService(ABC):
    @abstractmethod
    def saveToken(self, user_id : str, issued_type : str, request : Request, response : Response) :
        pass
    
    @abstractmethod
    def revoke_user_refresh_tokens(self, user_id: str):
        pass
    
    @abstractmethod
    def revoke_refresh_token(self, refresh_token : str):
        pass
    
    @abstractmethod
    def reissue_refresh_token(self, refresh_token : str, request : Request, response : Response) :
        pass
    
    
class JwtTokenServiceImpl(TokenService):
    
    def __init__(self, refresh_token_log_repo: RefreshTokenLogRepository | None = None):
        
        if refresh_token_log_repo:
            self.refresh_token_log_repo = refresh_token_log_repo
    
    def saveCookie(self, token_type : str, token : str, response : Response) : 
        '''쿠키에 저장 - JWT일 경우'''
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
    
    
    def encodeToken(self, user_id : str, token_type : str, secret_key : str) -> str:
        '''Token(Access, Refresh) 생성'''
        
        try:
            
            if not secret_key or secret_key == "":
                raise Exception(f"{token_type.upper()} SECRET_KEY 환경변수가 설정되지 않았습니다.")
            
            token_algorithm = os.getenv('TOKEN_ALGORITHM', '')
        
            if not token_algorithm or token_algorithm == "":
                raise Exception("TOKEN_ALGORITHM 환경변수가 설정되지 않았습니다.")
            
        except Exception as e:
            logger.critical(e)
            raise HTTPException(
                status_code=500,
                detail= "서버 설정 오류입니다."
            )
            
        
        if token_type == "access":
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        elif token_type == "refresh":
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        else :
            raise HTTPException(
                status_code=400,
                detail="잘못된 토큰 타입입니다."
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
        
        return jwt.encode(payload, secret_key, algorithm=token_algorithm, headers = headers)
        
    
    def generateTokenPair(self, user_id : str) -> dict[str] :
        
        result = {}
        
        try :
            # 1. Refresh Token 생성
            refresh_token = self.encodeToken(user_id, 'refresh', os.getenv('REFRESH_TOKEN_SECRET_KEY', ''))
            
            if not refresh_token or refresh_token == "":
                raise Exception("refresh_token이 생성되지 않았습니다.")
            
            # 2. Access Token 생성
            access_token = self.encodeToken(user_id, 'access', os.getenv('ACCESS_TOKEN_SECRET_KEY', ''))
            
            if not access_token or access_token == "":
                raise Exception("access_token이 생성되지 않았습니다.")
            
            result['access_token'] = access_token
            result['refresh_token'] = refresh_token
            
        except Exception as e:
            
            result = {}
            
            logger.error(e)
            
            raise HTTPException(
                status_code=500,
                detail= "서버 오류입니다."
            )
        
        return result
        
        
    async def saveToken(self, user_id : str, issued_type : str, request : Request, response : Response) -> dict[str] :
        
        ''' Token 생성
            1. 생성 기준
                - 로그인 할 때마다(기존 모두 미사용 처리 이후 신규 발급)
                - Refresh Token 갱신 할 때마다
            2. 세션 정책 : 단일 세션 정책(전부 제거)
                - 다중 세션 정책 → 동일 device_id만 제거(다중 디바이스 관리 시)
            3. DB 별 Refresh Token 관점(Refresh Token은 Hash 값만 저장)
                - Redis : 세션 접근(성능), TTL 설정
                - PostgreSQL : 세션 관리(이력 관리 / 권한 관리)
            4. Cookie 저장 옵션 : Secure=True, SameSite=Lax, HttpOnly
        '''
        
        token_pair = self.generateTokenPair(user_id)
        
        refresh_token = token_pair["refresh_token"]
        access_token = token_pair["access_token"]
        # payload 조회
        refresh_payload = jwt.decode(refresh_token, os.getenv('REFRESH_TOKEN_SECRET_KEY'), algorithms=[os.getenv('TOKEN_ALGORITHM')])
        
        access_payload = jwt.decode(access_token, os.getenv('ACCESS_TOKEN_SECRET_KEY'), algorithms=[os.getenv('TOKEN_ALGORITHM')])
        
        payload_user_id = refresh_payload['user_id']
        
        # 해시 생성
        refresh_token_hash = replace_hash_string(refresh_token)
        key = f"refresh:{payload_user_id}:{refresh_payload['jti']}"
        
        # Redis에 저장(TTL = 7일)
        await redis_container.refresh.set(key, refresh_token_hash, ex=60*60*24*7)
        
        # TODO
        is_save_token_history = True
        
        if is_save_token_history:
            await self.refresh_token_log_repo.insert(
                RefreshTokenLogDTO(
                    user_id = user_id
                    , refresh_token_hash = refresh_token_hash
                    , refresh_token_jti = refresh_payload['jti']
                    , access_token_hash = replace_hash_string(access_token)
                    , access_token_jti = access_payload['jti']
                    , issued_at = datetime.fromtimestamp(refresh_payload["iat"]).isoformat()
                    , expires_at=datetime.fromtimestamp(refresh_payload["exp"]).isoformat()
                    , ip=request.client.host if request else None
                    , user_agent=request.headers.get("user-agent") if request else None
                    , issued_type=issued_type
                )
            ) 
        
        # Save Cookie
        self.saveCookie('access', access_token, response)
        self.saveCookie('refresh', refresh_token, response)
        
    
    async def revoke_user_refresh_tokens(self, user_id: str):
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
        
        await self.refresh_token_log_repo.revoke(revoke_reason="login", user_id = user_id)
        
    
    
    async def revoke_refresh_token(self, refresh_token : str):
        SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY', '')
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', '') 
        
        try :
            if not SECRET_KEY:
                raise Exception("SECRET_KEY가 설정되지 않았습니다.")
            
            if not TOKEN_ALGORITHM:
                raise Exception("토큰 알고리즘이 설정되지 않았습니다.")
            
            refresh_token_hash = replace_hash_string(refresh_token)
            
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM])

            key = f"refresh:{payload['user_id']}:{payload['jti']}"
            
            stored_hash = await redis_container.refresh.get(key)
            
            if stored_hash is None:
                raise Exception("Refresh Token이 존재하지 않습니다.")

            if isinstance(stored_hash, bytes):
                stored_hash = stored_hash.decode()

            if stored_hash != refresh_token_hash:
                raise Exception("Refresh Token이 일치하지 않습니다.")
            
            user_id = payload.get("user_id")
            
            await self.refresh_token_log_repo.revoke(revoke_reason = "logout", user_id=user_id, refresh_token_hash = refresh_token_hash, refresh_token_jti = payload['jti'])
            
        except Exception as e:
            print(e)
    
    
    async def reissue_refresh_token(self, refresh_token : str, request : Request, response : Response) :
        
        SECRET_KEY = os.getenv('REFRESH_TOKEN_SECRET_KEY', '')
        TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM', '') 
        
        try :
            if not SECRET_KEY:
                raise Exception("SECRET_KEY가 설정되지 않았습니다.")
            
            if not TOKEN_ALGORITHM:
                raise Exception("토큰 알고리즘이 설정되지 않았습니다.")
            
            refresh_token_hash : str = replace_hash_string(refresh_token)
            
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM])

            key = f"refresh:{payload['user_id']}:{payload['jti']}"
            
            stored_hash = await redis_container.refresh.get(key)
            
            if stored_hash is None:
                raise Exception("Refresh Token이 존재하지 않습니다.")

            if isinstance(stored_hash, bytes):
                stored_hash = stored_hash.decode()

            if stored_hash != refresh_token_hash:
                raise Exception("Refresh Token이 일치하지 않습니다.")
            
            user_id = payload.get("user_id")
            
            await self.refresh_token_log_repo.revoke(revoke_reason = "refresh", user_id=user_id, refresh_token_hash = refresh_token_hash, refresh_token_jti = payload['jti'])
            
            # 토큰 발급(DB, Redis, 쿠키에 저장하는 로직도 있기 때문에 saveToken)
            await self.saveToken(user_id, 'refresh', request, response)
            
        except Exception as e:
            raise e
        
    
    
    